PROG = pdwmc
UI = dialog.ui main.ui dialog-appr.ui dialog-buttons.ui dialog-keys.ui dialog-rules.ui help-64x64.png
SRC = ${PROG} ${UI} utils.py dwmparser.py dwmparams.py pdwmgui.py  phyOS_simple_term_menu.py

PREFIX = /usr

install:
	mkdir -p ${DESTDIR}${PREFIX}/bin
	mkdir -p ${DESTDIR}${PREFIX}/share/${PROG}
	cp -f ${SRC} ${DESTDIR}${PREFIX}/share/${PROG}/
	ln -sf ${PREFIX}/share/${PROG}/${PROG} ${DESTDIR}${PREFIX}/bin/${PROG}

uninstall:
	rm -rf ${DESTDIR}${PREFIX}/share/${PROG}
	rm -rf ${DESTDIR}${PREFIX}/bin/${PROG}

.PHONY: all install uninstall
