PROG = pdwm
SRC = ${PROG} utils.py dwmparser.py dwmparams.py

PREFIX = /usr

install:
	mkdir -p ${DESTDIR}${PREFIX}/bin
	mkdir -p ${DESTDIR}${PREFIX}/share/${PROG}
	cp -f ${SRC} ${DESTDIR}${PREFIX}/share/${PROG}/
	ln -sf ${DESTDIR}${PREFIX}/share/${PROG}/${PROG} ${DESTDIR}${PREFIX}/bin/${PROG}

uninstall:
	rm -rf ${DESTDIR}${PREFIX}/share/${PROG}
	rm -rf ${DESTDIR}${PREFIX}/bin/${PROG}

.PHONY: all install uninstall
