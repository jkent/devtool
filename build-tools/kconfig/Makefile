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

yconf.c: yconf.y
lconf.c: lconf.l
hconf.c: hconf.gperf
	gperf -t --output-file $@ -a -C -E -g -k 1,3,$$ -p -t $<

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

