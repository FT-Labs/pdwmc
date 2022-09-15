#!/usr/bin/env python

from PyQt5 import Qt, QtCore, QtWidgets as qw, uic
from PyQt5 import *
import sys
import dwmparams as dp


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
                return
            sequence.append(text)

    key = keymap.get(event.key(), event.text())
    if key not in sequence:
        if col == "MODIFIERS":
            if key == "Super_L":
                key = "Win"
            if key in modmap.values():
                sequence.append(key)
        elif col == "KEY" and event.key() not in modmap:
            if (key not in special_keys and (len(key) > 1 and key[0] != 'F')) or len(key) == 1:
                key = "XK_" + key.lower()
            else:
                key = "XK_" + key
            sequence.append(key)
    return '|'.join(sequence)

class TableWidget(qw.QTableWidget):

    def set_popup(self, p, d):
        self.pop_key_actions = p
        self.pop_key_actions.setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)
        self.dialog = d

    def keyPressEvent(self, event):
        header = self.horizontalHeaderItem(self.currentColumn()).text()
        if header != "ACTION":
            s = keyevent_to_string(event, header)
            self.currentItem().setText(s)
            self.resizeColumnsToContents()
        else:
            if event.key() == QtCore.Qt.Key_Return:
                self.dialog.show()
            super(TableWidget, self).keyPressEvent(event)

    def cell_clicked(self, row, col):
        col_header = self.horizontalHeaderItem(col).text()
        if col_header == "ACTION":
            x = self.columnViewportPosition(col)
            y = self.rowViewportPosition(row) + self.rowHeight(row)
            pos = self.viewport().mapToGlobal(QtCore.QPoint(x, y))
            self.pop_key_actions.move(pos)
            self.pop_key_actions.adjustSize()
            if self.pop_key_actions.exec_() == qw.QDialog.Accepted:
                self.currentItem().setText(self.pop_key_actions.text())

class PdwmCommandDialog(qw.QDialog):
    def __init__(self):
        super(PdwmCommandDialog, self).__init__()
        uic.loadUi('dialog.ui', self)
        self.setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)

class PdwmGui(qw.QMainWindow):
    def __init__(self, dwm_parser):
        super(PdwmGui, self).__init__()
        uic.loadUi('main.ui', self)
        self.d_custom_action = PdwmCommandDialog()
        self.d_custom_action.accepted.connect(self.custom_action_accepted)
        self.dwm_parser = dwm_parser
        self.dwm_parser.get_files("/buttons", "/keys", "/appearance", "rules")
        self.dwm_parser.make_tables()
        self.t_keys = TableWidget(self.tab_keys)
        self.t_keys.setSizeAdjustPolicy(qw.QAbstractScrollArea.AdjustToContents)
        self.t_keys.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.t_keys.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.t_keys.setObjectName("t_keys")
        self.t_keys.cellClicked.connect(self.t_keys.cell_clicked)
        self.t_keys.cellDoubleClicked.connect(self.t_keys_cell_double_clicked)
        self.t_keys.set_popup(PopUp(list(dp.keys_dict.values())), self.d_custom_action)
        self.gridLayout_5.addWidget(self.t_keys, 0, 0, 1, 1)
        self.set_buttons_table()
        self.set_keys_table()
        self.set_appr_table()

    def custom_action_accepted(self):
        is_term = self.d_custom_action.c_isterminal.isChecked()
        command = self.d_custom_action.le_command.text()
        cmd = self.dwm_parser.make_action(command, is_term)
        self.t_keys.currentItem().setText(cmd)

    def t_keys_cell_double_clicked(self):
        header = self.t_keys.horizontalHeaderItem(self.t_keys.currentColumn()).text()
        if header == "ACTION":
            self.d_custom_action.show()
            self.d_custom_action.adjustSize()

    def set_appr_table(self):
        self.t_appr.setColumnCount(2)
        self.t_appr.setRowCount(len(self.dwm_parser.tabular_appearance[:-1]))
        for i, arr in enumerate(self.dwm_parser.tabular_appearance[:-1]):
            for j, attr in enumerate(arr):
                new_item = qw.QTableWidgetItem(attr)
                self.t_appr.setItem(i, j, new_item)
        self.t_appr.resizeColumnsToContents()
        self.t_appr.resizeRowsToContents()

        self.t_fonts.setColumnCount(1)
        self.t_fonts.setRowCount(len(self.dwm_parser.tabular_appearance[-1]))
        for i, arr in enumerate(self.dwm_parser.tabular_appearance[-1]):
            new_item = qw.QTableWidgetItem(arr)
            self.t_fonts.setItem(i, 0, new_item)
        self.t_fonts.resizeColumnsToContents()
        self.t_fonts.resizeRowsToContents()
        self.t_fonts.setHorizontalHeaderLabels(["FONTS"])
    def set_buttons_table(self):
        h = ["CLICK WIN", "KEY", "BUTTON", "ACTION"]
        self.t_buttons.setColumnCount(len(h))
        self.t_buttons.setRowCount(len(self.dwm_parser.tabular_buttons))
        for i, arr in enumerate(self.dwm_parser.tabular_buttons):
            for j, attr in enumerate(arr):
                new_item = qw.QTableWidgetItem(attr)
                self.t_buttons.setItem(i, j, new_item)
        self.t_buttons.setHorizontalHeaderLabels(h)
        self.t_buttons.resizeColumnsToContents()
        self.t_buttons.resizeRowsToContents()

    def set_keys_table(self):
        h = ["MODIFIERS", "KEY", "ACTION"]
        self.t_keys.setColumnCount(len(h))
        self.t_keys.setRowCount(len(self.dwm_parser.tabular_keys))
        for i, arr in enumerate(self.dwm_parser.tabular_keys):
            for j, attr in enumerate(arr):
                new_item = qw.QTableWidgetItem(attr)
                if j == 2 or j == 0:
                    new_item.setFlags(new_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.t_keys.setItem(i, j, new_item)
        self.t_keys.setHorizontalHeaderLabels(h)
        self.t_keys.resizeColumnsToContents()
        self.t_keys.resizeRowsToContents()

    def set_rules_table(self):
        h = ["CLASS", "INSTANCE", "TITLE", "TAGS", "ISFLOATING", "ISTERMINAL", "ISCENTERED", "NOSWALLOW", "MANAGEDSIZE", "MON"]
        self.t_rules.setColumnCount(len(h))
        self.t_rules.setRowCount(len(self.dwm_parser.tabular_buttons))
        for i, arr in enumerate(self.dwm_parser.tabular_rules):
            for j, attr in enumerate(arr):
                new_item = qw.QTableWidgetItem(attr)
                self.t_rules.setItem(i, j, new_item)
        self.t_rules.setHorizontalHeaderLabels(h)
        self.t_rules.resizeColumnsToContents()
        self.t_rules.resizeRowsToContents()

if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    pdwmGui = PdwmGui()
    pdwmGui.show()
    app.exec_()
