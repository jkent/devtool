#
#  Copyright (C) 2013 Jeff Kent <jeff@jkent.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License version 2 as
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

AS      := $(CROSS_COMPILE)as
LD      := $(CROSS_COMPILE)ld
CC      := $(CROSS_COMPILE)gcc
CPP     := $(CC) -E
AR      := $(CROSS_COMPILE)ar
NM      := $(CROSS_COMPILE)nm
STRIP   := $(CROSS_COMPILE)strip
OBJCOPY := $(CROSS_COMPILE)objcopy
OBJDUMP := $(CROSS_COMPILE)objdump
SIZE    := $(CROSS_COMPILE)size

ifeq (${CURDIR},$(_DT_PROJECT))
  OBJDIR := $(_DT_PROJECT)/obj
else
  OBJDIR := ${CURDIR}
endif

CFLAGS   = -std=gnu99 -Wall -fms-extensions $(cflags-y)
ASFLAGS := -Wa,--defsym,_entry=0
LDFLAGS := -Wl,-M,-Map,$(OBJDIR)/$(basename $(target)).map
LIBS     = -lgcc $(libs-y)
INCLUDE  = $(addprefix -I$(_DT_PROJECT)/,include $(includes))

ifdef CONFIG_DEBUG
  cflags-y += -O0 -g3 -DDEBUG
else
  cflags-y += -Os
endif

ifeq ($(V),1)
  D := @true
  Q :=
else
  D := @echo
  Q := @
endif

include $(_DT_PROJECT)/include/auto.conf

ifdef CONFIG_ARCH_ARM
  include $(_DT)/mk/arm.mk
endif

includes :=
objs :=
define collect_vars
  include-y :=
  subdir-y :=
  obj-y :=
  include $(_DT_PROJECT)/$(1)/Makefile
  includes := $$(includes) $$(addprefix $(1)/,$$(include-y))
  objs := $$(objs) $$(addprefix $(OBJDIR)/$(1)/,$$(obj-y))
  $$(foreach dir,$$(subdir-y),\
    $$(eval dirs += $(1)/$$(dir))\
    $$(eval $$(call collect_vars,$(1)/$$(dir)))\
  )
endef

dirs := $(srcdirs)
$(foreach dir,$(srcdirs),\
	$(eval $(call collect_vars,$(dir)))\
)

.PHONY: all
all: $(target) deps

-include $(OBJDIR)/deps.mk

.PHONY: deps
deps:
	@rm -f $(OBJDIR)/deps.mk
	@$(foreach dir,$(dirs),\
	  $(foreach file,$(wildcard $(OBJDIR)/$(dir)/*.d),\
	    cat $(file) >> $(OBJDIR)/deps.mk;\
	  )\
	)

$(basename $(target)).elf: $(OBJDIR)/$(ld_script) $(objs)
	$(D) "   LD       $(subst $(OBJDIR)/,,$@)"
	$(Q)$(CC) $(CFLAGS) $(LDFLAGS) -T $^ -o $@

$(OBJDIR)/%.o: $(_DT_PROJECT)/%.S
	$(D) "   AS       $(subst $(_DT_PROJECT)/,,$<)"
	@mkdir -p $(@D)
	$(Q)$(CC) -c -MMD -MP -MF $@.d -MQ $@ $(CFLAGS) $(ASFLAGS) $(INCLUDE) -o $@ $<

$(OBJDIR)/%.o: $(_DT_PROJECT)/%.c
	$(D) "   CC       $(subst $(_DT_PROJECT)/,,$<)"
	@mkdir -p $(@D)
	$(Q)$(CC) -c -MMD -MP -MF $@.d -MQ $@ $(CFLAGS) $(INCLUDE) -o $@ $<

$(OBJDIR)/%: $(_DT_PROJECT)/%.in
	$(D) "   CPP      $(subst $(_DT_PROJECT)/,,$<)"
	@mkdir -p $(@D)
	$(Q)$(CPP) -P -MMD -MP -MF $@.d -MQ $@ -x c $(INCLUDE) -o $@ $<

.PHONY: clean
clean:
	@rm -f $(basename $(target)).elf $(basename $(target)).bin
	@if [ ${CURDIR} = $(_DT_PROJECT) ]; then\
	  rm -rf $(OBJDIR);\
	else\
	  rm -rf $(addprefix $(OBJDIR)/,$(dirs));\
	  rm -f $(OBJDIR)/$(ld_script) $(OBJDIR)/$(ld_script).d;\
	  rm -f $(objs) $(addsuffix .d,$(objs));\
	  rm -f $(OBJDIR)/deps.mk;\
	  rm -f $(OBJDIR)/$(basename $(target)).map;\
	  rm -f $(OBJDIR)/$(basename $(target)).dis;\
	fi

