#!/usr/bin/env python

from PyQt5 import QtGui, QtCore, QtWidgets as qw, uic
from PyQt5 import *
import sys

import dwmparams as dp
import subprocess
from math import log2


keymap = {}
for key, value in vars(QtCore.Qt).items():
    if isinstance(value, QtCore.Qt.Key):
        keymap[value] = key.partition('_')[2]

modmap = {
    QtCore.Qt.ControlModifier: keymap[QtCore.Qt.Key_Control],
    QtCore.Qt.AltModifier: keymap[QtCore.Qt.Key_Alt],
    QtCore.Qt.ShiftModifier: keymap[QtCore.Qt.Key_Shift],
    QtCore.Qt.MetaModifier: "Win",
    QtCore.Qt.GroupSwitchModifier: keymap[QtCore.Qt.Key_AltGr],
    QtCore.Qt.Key_Super_L : "Win",
    QtCore.Qt.KeypadModifier: keymap[QtCore.Qt.Key_NumLock],
    }

special_keys = ["Delete", "BackSpace", "Return", "Tab", "Escape", "Print"]

class FloatingButtonWidget(qw.QAbstractButton):
    def __init__(self, picture, parent):
        super().__init__(parent)
        self.paddingLeft = 5
        self.paddingTop = 5
        self.setPicture(QtGui.QPixmap(picture))

    def setPicture(self, picture):
        self.picture = picture
        self.update_position()
        self.update()

    def sizeHint(self):
        return self.picture.size()

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.picture)

    def update_position(self):
        if hasattr(self.parent(), 'viewport'):
            parent_rect = self.parent().viewport().rect()
        else:
            parent_rect = self.parent().rect()

        if not parent_rect:
            return

        x = parent_rect.width() -  self.picture.width() - self.paddingLeft
        y = parent_rect.height() - self.picture.height() - self.paddingTop
        self.setGeometry(x, y, self.picture.width(), self.picture.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_position()
        self.update()

class PopUp(qw.QDialog):
    def __init__(self, labels):
        qw.QDialog.__init__(self, None, QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint)
        self.itemSelected = ""
        self.setLayout(qw.QVBoxLayout())
        l_widget = qw.QListWidget(self)
        self.layout().addWidget(l_widget)
        l_widget.addItems(labels)
        l_widget.itemClicked.connect(self.onItemClicked)
        l_widget.setMinimumWidth(l_widget.sizeHintForColumn(0))
        l_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        l_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def onItemClicked(self, item):
        self.itemSelected = item.text()
        self.accept()

    def text(self):
        return self.itemSelected

def keyevent_to_string(event, col):
    sequence = []
    for modifier, text in modmap.items():
        if event.modifiers() & modifier:
            if col != "MODIFIERS":
                return "0"
            sequence.append(text)

    key = keymap.get(event.key(), event.text()) if event.key() != QtCore.Qt.Key_Super_L else "Win"
    if key not in sequence:
        if col == "MODIFIERS":
            if key == "Escape":
                key = "Win"
            if key in modmap.values():
                sequence.append(key)
        elif col == "KEY" and event.key() not in modmap:
            if (key not in special_keys and (len(key) > 1 and key[0] != 'F')) or len(key) == 1:
                key = "XK_" + key.lower()
            else:
                key = "XK_" + key
            sequence.append(key)
    return '|'.join(sequence) if sequence else "0"

class TableWidget(qw.QTableWidget):

    floatingButtonClicked = QtCore.pyqtSignal()

    def __init__(self, parent=None, enable_keypress=False):
        self.enable_keypress = enable_keypress
        super().__init__(parent)
        self.floating_button = FloatingButtonWidget("./help-64x64.png", parent=self)
        self.setStyleSheet("""
        QHeaderView::section {
            background-color: rgb(106, 116, 255);
		    color: black; }
        """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.floating_button.update_position()

    def set_dialog(self, d):
        self.dialog = d

    def keyPressEvent(self, event):
        if self.enable_keypress:
            header = self.horizontalHeaderItem(self.currentColumn()).text()
            if header != "ACTION":
                s = keyevent_to_string(event, header)
                self.currentItem().setText(s)
                self.resizeColumnsToContents()
            else:
                if event.key() == QtCore.Qt.Key_Return:
                    self.dialog.show()
        super(TableWidget, self).keyPressEvent(event)

class PdwmHelpDialog(qw.QDialog):
    def __init__(self, dlg):
        super(PdwmHelpDialog, self).__init__()
        uic.loadUi(dlg, self)
        self.pb_close.clicked.connect(lambda : self.close())

class PdwmCommandDialog(qw.QDialog):
    def __init__(self):
        super(PdwmCommandDialog, self).__init__()
        uic.loadUi('dialog.ui', self)
        self.setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)

class PdwmGui(qw.QMainWindow):
    def __init__(self, dwm_parser):
        super(PdwmGui, self).__init__()
        uic.loadUi('main.ui', self)
        self.dwm_parser = dwm_parser
        self.dwm_parser.get_files("/buttons", "/keys", "/appearance", "/rules")
        self.dwm_parser.update()
        self.d_custom_action = PdwmCommandDialog()
        self.d_custom_action.accepted.connect(self.custom_action_accepted)
        self.pop_key_actions = PopUp(list(dp.keys_dict.values()))
        self.pop_key_actions.setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)
        self.pop_colorschemes = PopUp(self.get_schemes())
        self.pop_button_actions = PopUp(list(dp.buttons_dict.values()))
        self.pop_button_actions.setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)
        self.pop_button_clickwin = PopUp(["ClkClientWin", "ClkRootWin", "ClkTagBar", "ClkStatusText", "ClkLtSymbol"])
        self.pop_button_clickwin.setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)
        self.pop_button_buttons = PopUp(["LeftClick", "RightClick", "MiddleClick", "WheelUp", "WheelDown"])
        self.pop_button_buttons.setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)
        self.dwm_parser.make_tables()
        self.t_keys = TableWidget(self.tab_keys, True)
        self.t_keys.setSizeAdjustPolicy(qw.QAbstractScrollArea.AdjustToContents)
        self.t_keys.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.t_keys.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.t_keys.verticalHeader().setVisible(False)
        self.t_keys.horizontalHeader().setStretchLastSection(True)
        self.t_keys.setObjectName("t_keys")
        self.t_keys.cellDoubleClicked.connect(self.t_keys_cell_double_clicked)
        self.t_keys.set_dialog(self.d_custom_action)
        self.gridLayout_5.addWidget(self.t_keys, 0, 0, 1, 1)

        self.t_rules = TableWidget(self.tab_rules)
        self.gridLayout_6.addWidget(self.t_rules, 0, 0, 1, 1)
        self.t_rules.setObjectName("t_rules")

        self.action_close.triggered.connect(lambda : sys.exit())
        self.action_save.triggered.connect(self.save_config)
        self.action_savebuild.triggered.connect(lambda : (self.save_config(), self.dwm_parser.build_dwm()))
        self.pb_key.clicked.connect(self.t_keys_add)
        self.pb_button.clicked.connect(self.t_buttons_add)
        self.pb_key_delete.clicked.connect(lambda : self.t_keys.removeRow(self.t_keys.currentRow()))
        self.pb_button_delete.clicked.connect(lambda : self.t_buttons.removeRow(self.t_buttons.currentRow()))
        self.pb_rule_add.clicked.connect(self.t_rules_add_rule)
        self.pb_rule_delete.clicked.connect(lambda : self.t_rules.removeRow(self.t_rules.currentRow()))
        self.t_buttons = TableWidget(self.tab_buttons, True)
        self.t_buttons.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.t_buttons.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.t_buttons.setSizeAdjustPolicy(qw.QAbstractScrollArea.AdjustToContents)
        self.t_buttons.horizontalHeader().setStretchLastSection(True)
        self.t_buttons.setAutoScroll(False)
        self.t_buttons.setObjectName("t_buttons")
        self.t_buttons.set_dialog(self.d_custom_action)
        self.t_buttons.verticalHeader().setVisible(False)
        self.t_buttons.cellDoubleClicked.connect(self.t_buttons_cell_double_clicked)
        self.gridLayout_4.addWidget(self.t_buttons, 0, 0, 1, 1)

        self.t_appr.itemChanged.connect(self.t_appr_check_item)
        self.help_d = [PdwmHelpDialog("dialog-appr.ui"),
                       PdwmHelpDialog("dialog-keys.ui"),
                       PdwmHelpDialog("dialog-buttons.ui"),
                       ]
        self.pb_appr_help.clicked.connect(lambda : self.help_d[0].show())

        self.set_buttons_table()
        self.set_keys_table()
        self.set_appr_table()
        self.set_rules_table()
        self.set_colors_table()

    def build(self):
        self.save_config()
        self.dwm_parser.build_dwm()

    def get_schemes(self):
        cmd = "ls /usr/share/phyos/config/rofi/colors | tr '.' ' ' | awk '{print $1}'"
        col_arr = subprocess.check_output(cmd, text=True, shell=True)
        return str(col_arr).strip('\n').split("\n")

    def t_rules_add_rule(self):
        subprocess.run(["dunstify", "-a", "center", "PLEASE CLICK A WINDOW TO SET A RULE"])
        class_name, instance = subprocess.check_output("xprop | grep 'WM_CLASS' | tr -d ',' | awk '{print $NF,$(NF-1)}'", shell=True, text=True).strip("\n ").split(" ")
        new_rule = [class_name, instance, "NULL", "0", "0", "0", "0", "0", "0", "-1"]
        self.t_rules.insertRow(self.t_rules.rowCount())
        for j in range(self.t_rules.columnCount()):
            new_item = qw.QTableWidgetItem()
            new_item.setText(new_rule[j])
            self.t_rules.setItem(self.t_rules.rowCount() - 1, j, new_item)


    def t_appr_check_item(self, item):
        try:
            if int(item.text()) < 0:
                raise ValueError
            self.t_appr.resizeColumnsToContents()
        except:
            if (item.flags() & QtCore.Qt.ItemIsEditable):
                item.setText("0")

    def t_keys_add(self):
        self.t_keys.insertRow(self.t_keys.rowCount())
        for j in range(self.t_keys.columnCount()):
            new_item = qw.QTableWidgetItem()
            if j == 2 or j == 0:
                new_item.setFlags(new_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.t_keys.setItem(self.t_keys.rowCount() - 1, j, new_item)

    def t_buttons_add(self):
        self.t_buttons.insertRow(self.t_buttons.rowCount())
        for j in range(self.t_buttons.columnCount()):
            new_item = qw.QTableWidgetItem()
            new_item.setFlags(new_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.t_buttons.setItem(self.t_buttons.rowCount() - 1, j, new_item)

    def t_buttons_cell_double_clicked(self, row, col):
        col_header = self.t_buttons.horizontalHeaderItem(col).text()
        if col_header != "MODIFIERS":
            x = self.t_buttons.columnViewportPosition(col)
            y = self.t_buttons.rowViewportPosition(row) + self.t_keys.rowHeight(row)
            pos = self.t_buttons.viewport().mapToGlobal(QtCore.QPoint(x, y))

            if col_header == "ACTION":
                self.pop_button_actions.move(pos)
                self.pop_button_actions.adjustSize()
                if self.pop_button_actions.exec_() == qw.QDialog.Accepted:
                    self.t_buttons.currentItem().setText(self.pop_button_actions.text())
            elif col_header == "CLICK WIN":
                self.pop_button_clickwin.move(pos)
                self.pop_button_clickwin.adjustSize()
                if self.pop_button_clickwin.exec_() == qw.QDialog.Accepted:
                    self.t_buttons.currentItem().setText(self.pop_button_clickwin.text())
            else:
                self.pop_button_buttons.move(pos)
                self.pop_button_buttons.adjustSize()
                if self.pop_button_buttons.exec_() == qw.QDialog.Accepted:
                    self.t_buttons.currentItem().setText(self.pop_button_buttons.text())


    def t_keys_cell_double_clicked(self, row, col):
        col_header = self.t_keys.horizontalHeaderItem(col).text()
        if col_header == "ACTION":
            x = self.t_keys.columnViewportPosition(col)
            y = self.t_keys.rowViewportPosition(row) + self.t_keys.rowHeight(row)
            pos = self.t_keys.viewport().mapToGlobal(QtCore.QPoint(x, y))
            self.pop_key_actions.move(pos)
            self.pop_key_actions.adjustSize()
            if self.pop_key_actions.exec_() == qw.QDialog.Accepted:
                self.t_keys.currentItem().setText(self.pop_key_actions.text())

    def custom_action_accepted(self):
        is_term = self.d_custom_action.c_isterminal.isChecked()
        cmd = self.d_custom_action.le_command.text()
        if is_term:
            cmd = "TERM(" + cmd + ")"
        if self.tab_widget.tabText(self.tab_widget.currentIndex()) == "KEYS":
            self.t_keys.currentItem().setText(cmd)
            self.t_keys.resizeColumnsToContents()
            self.adjustSize()
        else:
            self.t_buttons.currentItem().setText(cmd)
            self.t_buttons.resizeColumnsToContents()

    def set_appr_table(self):
        h = ["ATTRIBUTE", "VALUE"]
        self.t_appr.setColumnCount(2)
        self.t_appr.setRowCount(len(self.dwm_parser.tabular_appearance[:-1]))
        for i, arr in enumerate(self.dwm_parser.tabular_appearance[:-1]):
            for j, attr in enumerate(arr):
                new_item = qw.QTableWidgetItem(attr)
                if j == 0:
                    new_item.setFlags(new_item.flags() & ~QtCore.Qt.ItemIsEditable)
                else:
                    new_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.t_appr.setItem(i, j, new_item)

        self.t_appr.setHorizontalHeaderLabels(h)
        self.t_appr.resizeColumnsToContents()
        self.t_appr.horizontalHeader().setStretchLastSection(True)

        self.t_fonts.setColumnCount(1)
        self.t_fonts.setRowCount(len(self.dwm_parser.tabular_appearance[-1]))
        for i, arr in enumerate(self.dwm_parser.tabular_appearance[-1]):
            new_item = qw.QTableWidgetItem(arr)
            self.t_fonts.setItem(i, 0, new_item)
        self.t_fonts.setHorizontalHeaderLabels(["FONTS"])
        self.t_fonts.resizeColumnsToContents()
        self.t_fonts.horizontalHeader().setStretchLastSection(True)

    def set_buttons_table(self):
        h = ["CLICK WIN", "MODIFIERS", "BUTTON", "ACTION"]
        self.t_buttons.floating_button.clicked.connect(lambda : self.help_d[2].show())
        self.t_buttons.setColumnCount(len(h))
        self.t_buttons.setRowCount(len(self.dwm_parser.tabular_buttons))
        for i, arr in enumerate(self.dwm_parser.tabular_buttons):
            for j, attr in enumerate(arr):
                new_item = qw.QTableWidgetItem(attr)
                self.t_buttons.setItem(i, j, new_item)
                new_item.setFlags(new_item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.t_buttons.setHorizontalHeaderLabels(h)
        self.t_buttons.resizeColumnsToContents()

    def set_keys_table(self):
        h = ["MODIFIERS", "KEY", "ACTION"]
        self.t_keys.setColumnCount(len(h))
        self.t_keys.floating_button.clicked.connect(lambda : self.help_d[1].show())
        self.t_keys.setRowCount(len(self.dwm_parser.tabular_keys))
        for i, arr in enumerate(self.dwm_parser.tabular_keys):
            for j, attr in enumerate(arr):
                new_item = qw.QTableWidgetItem(attr)
                if j == 2 or j == 0:
                    new_item.setFlags(new_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.t_keys.setItem(i, j, new_item)
        self.t_keys.setHorizontalHeaderLabels(h)
        self.t_keys.resizeColumnsToContents()

    def set_rules_table(self):
        h = ["CLASS", "INSTANCE", "TITLE", "TAGS", "ISFLOATING", "ISTERMINAL", "ISCENTERED", "NOSWALLOW", "MANAGEDSIZE", "MON"]
        self.t_rules.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.t_rules.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.t_rules.setSizeAdjustPolicy(qw.QAbstractScrollArea.AdjustToContents)
        self.t_rules.setColumnCount(len(h))
        self.t_rules.setRowCount(len(self.dwm_parser.tabular_rules))
        self.t_rules.verticalHeader().setVisible(False)
        for i, arr in enumerate(self.dwm_parser.tabular_rules):
            for j, attr in enumerate(arr):
                if j == 3:
                    attr = eval(attr)
                    attr = '0' if attr == 0 else str(int(log2(attr) + 1))
                new_item = qw.QTableWidgetItem(attr)
                self.t_rules.setItem(i, j, new_item)
        self.t_rules.setHorizontalHeaderLabels(h)
        self.t_rules.resizeColumnsToContents()
        self.adjustSize()


    def t_colors_header_clicked(self, idx):
            x = self.t_colors.columnViewportPosition(idx)
            y = self.t_colors.rowViewportPosition(idx)
            pos = self.t_colors.viewport().mapToGlobal(QtCore.QPoint(x, y))
            self.pop_colorschemes.move(pos)
            self.pop_colorschemes.adjustSize()

            if self.pop_colorschemes.exec_() == qw.QDialog.Accepted:
                cmd = f'cat /usr/share/phyos/config/rofi/colors/{self.pop_colorschemes.text()}.rasi | grep "#" | awk \'{{print $2}}\' | cut -c  -7'
                col_arr = str(subprocess.check_output(cmd, text=True, shell=True)).strip("\n").split("\n")

                for i in range(7):
                    self.t_colors.item(i, 1).setText(col_arr[i])
                self.t_colors.resizeColumnsToContents()

    def set_colors_table(self):
        h = ["CLICK HERE TO CHOOSE COLORSCHEME", ""]
        self.t_colors.setColumnCount(2)
        self.t_colors.setRowCount(7)
        self.t_colors.verticalHeader().setVisible(False)
        cmd = 'cat ~/.config/phyos/pdwm/colors.h | grep "#" | awk \'{print $5}\' | tr -d \'";\''
        hex_arr = str(subprocess.check_output(cmd, shell=True, text=True)).strip('\n').split("\n")
        col_arr = ["black", "gray2", "blue2", "white", "blue", "green", "red"]

        for i in range(7):
            new_item = qw.QTableWidgetItem(col_arr[i])
            new_item.setFlags(new_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.t_colors.setItem(i, 0, new_item)
            new_item = qw.QTableWidgetItem(hex_arr[i])
            self.t_colors.setItem(i, 1, new_item)
        self.t_colors.horizontalHeader().sectionClicked.connect(self.t_colors_header_clicked)
        self.t_colors.setHorizontalHeaderLabels(h)
        self.t_colors.resizeColumnsToContents()

    def save_config(self):
        self.dwm_parser.tabular_keys.clear()
        self.dwm_parser.tabular_buttons.clear()
        self.dwm_parser.tabular_appearance.clear()
        self.dwm_parser.tabular_rules.clear()

        for i in range(self.t_keys.rowCount()):
            self.dwm_parser.tabular_keys.append([])
            for j in range(self.t_keys.columnCount()):
                self.dwm_parser.tabular_keys[i].append(self.t_keys.item(i, j).text())

        for i in range(self.t_buttons.rowCount()):
            self.dwm_parser.tabular_buttons.append([])
            for j in range(self.t_buttons.columnCount()):
                self.dwm_parser.tabular_buttons[i].append(self.t_buttons.item(i, j).text())

        for i in range(self.t_rules.rowCount()):
            self.dwm_parser.tabular_rules.append([])
            for j in range(self.t_rules.columnCount()):
                if j != 3:
                    self.dwm_parser.tabular_rules[i].append(self.t_rules.item(i, j).text())
                else:
                    t = eval(self.t_rules.item(i, j).text())
                    if t != 0:
                        t -= 1
                        s = f"1 << {t}"
                    else:
                        s = "0"
                    self.dwm_parser.tabular_rules[i].append(s)

        for i in range(self.t_appr.rowCount()):
            self.dwm_parser.tabular_appearance.append([])
            for j in range(self.t_appr.columnCount()):
                self.dwm_parser.tabular_appearance[i].append(self.t_appr.item(i, j).text())

        self.dwm_parser.tabular_appearance.append([])
        for i in range(self.t_fonts.rowCount()):
            self.dwm_parser.tabular_appearance[-1].append(self.t_fonts.item(i, 0).text())

        dir = self.dwm_parser.data_dir
        with open(f"{dir}/colors.h", "w") as f:
            for i in range(7):
                l = f'static char {self.t_colors.item(i, 0).text()}[] = "{self.t_colors.item(i, 1).text()}";\n'
                f.write(l)

        self.dwm_parser.write_tmp_files()

    def resize_table_to_contents(self, table):
            vh = table.verticalHeader()
            hh = table.horizontalHeader()
            size = QtCore.QSize(hh.length(), vh.length())  # Get the length of the headers along each axis.
            size += QtCore.QSize(vh.size().width(), hh.size().height())  # Add on the lengths from the *other* header
            size += QtCore.QSize(20, 20)  # Extend further so scrollbars aren't shown.
            table.resize(size)

if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    pdwmGui = PdwmGui()
    pdwmGui.show()
    app.exec_()
