PROG = pdwm
SRC = ${PROG} utils.py dwmparser.py dwmparams.py

PREFIX = /usr

install:
	mkdir -p ${PREFIX}/bin
	mkdir -p ${PREFIX}/share/${PROG}
	cp -f ${SRC} ${PREFIX}/share/${PROG}/
	ln -sf ${PREFIX}/share/${PROG}/${PROG} ${PREFIX}/bin/${PROG}

uninstall:
	rm -f ${PREFIX}/share/${PROG}
	rm -f ${PREFIX}/bin/${PROG}

.PHONY = all install
