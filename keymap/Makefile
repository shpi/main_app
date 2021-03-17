# config

# add our flags + libs
CFLAGS	+= -DVERSION='"$(VERSION)"'
LDLIBS	+= -lm

# build
TARGETS	:= keymap lircd.conf
HEADERS	:= EV.h REL.h ABS.h MSC.h LED.h SND.h REP.h KEY.h BTN.h BUS.h SW.h

# default target
all: build

build: $(TARGETS)

$(HEADERS): name.sh
	sh name.sh $* > $@

lircd.conf: lirc.sh
	sh lirc.sh > $@

keymap: keymap.o

install: build
	$(INSTALL_BINARY) keymap $(bindir)

clean:
	-rm -f *.o $(depfiles)

realclean distclean: clean
	-rm -f $(TARGETS) $(HEADERS) *~ xpm/*~ *.bak


-include $(depfiles)

