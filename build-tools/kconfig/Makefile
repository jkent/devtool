config_prefix=CONFIG_
export YFLAGS=-t -l -p zconf
export LFLAGS=-L -P zconf
export LDFLAGS=-lcurses
export CFLAGS=-DROOTMENU=\"Configuration\" -DCONFIG=\"$(config_prefix)\"

.PHONY: all
all: conf mconf tweak

conf: conf.o yconf.o
mconf: mconf.o yconf.o lxdialog.a
tweak: tweak.in
	sed -r -e "s/@CONFIG_@/$(config_prefix)/g" $< >$@
	@chmod +x $@

conf.o: conf.c
mconf.o: mconf.c
yconf.o: yconf.c hconf.c lconf.c util.c confdata.c expr.c symbol.c menu.c lkc.h expr.h lkc_proto.h list.h

ifeq ($(shell which yacc),)
yconf.c: yconf.c.dist
	cp yconf.c.dist yconf.c
else
yconf.c: yconf.y
endif

ifeq ($(shell which lex),)
lconf.c: lconf.c.dist
	cp lconf.c.dist lconf.c
else
lconf.c: lconf.l
endif

ifeq ($(shell which gperf),)
hconf.c: hconf.c.dist
	cp hconf.c.dist hconf.c
else
hconf.c: hconf.gperf
	gperf -t --output-file $@ -a -C -E -g -k 1,3,$$ -p -t $<
endif

lxdialog.a: lxdialog/*.c lxdialog/*.h
	@make -e -C lxdialog

.PHONY: install
install: all
	if [ -d "$(_DT)/bin" ]; then \
	  for f in conf mconf merge tweak; do \
	    cp $$f $(_DT)/bin/kconfig-$$f; \
          done \
	fi

.PHONY: clean
clean:
	rm -f conf mconf tweak *.o *.a yconf.c hconf.c lconf.c
	@make -e -C lxdialog clean

.PHONY: dist
dist: yconf.c lconf.c hconf.c
	mv yconf.c yconf.c.dist
	mv lconf.c lconf.c.dist
	mv hconf.c hconf.c.dist

