PROG = pdwm
SRC = ${PROG} utils.py dwmparser.py dwmparams.py

PREFIX = /usr

install:
	mkdir -p ${DESTDIR}${PREFIX}/bin
	mkdir -p ${DESTDIR}${PREFIX}/share/${PROG}
	cp -f ${SRC} ${DESTDIR}${PREFIX}/share/${PROG}/
	ln -sf ${DESTDIR}${PREFIX}/share/${PROG}/${PROG} ${PREFIX}/bin/${PROG}

uninstall:
	rm -f ${DESTDIR}${PREFIX}/share/${PROG}
	rm -f ${DESTDIR}${PREFIX}/bin/${PROG}

.PHONY: all install uninstall
