.PHONY: all
all: ../lxdialog.a

../lxdialog.a: checklist.o inputbox.o menubox.o textbox.o util.o yesno.o
	ar rc $@ $^

checklist.o: checklist.c
inputbox.o: inputbox.c
menubox.o: menubox.c
textbox.o: textbox.c
util.o: util.c
yesno.o: yesno.c

.PHONY: clean
clean:
	rm -f *.o

