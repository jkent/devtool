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

# default rule
.PHONY: all
all:

BASEDIR ?= $(patsubst %/,%,$(dir $(firstword $(MAKEFILE_LIST))))
BUILD := $(BASEDIR)/build/$(_DT_PROFILE)

# prepare build
define nl


endef
$(eval $(subst #,$(nl),$(shell dt _prepmk $(BASEDIR)|tr '\n' '#')))

ifndef _DT_PROFILE
$(error cannot continue)
endif

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

CFLAGS   = -std=gnu99 -Wall -fms-extensions $(cflags-y)
ASFLAGS := -Wa,--defsym,_entry=0
LDFLAGS := -Wl,-M,-Map,$(BUILD)/$(basename $(target)).map
LIBS     = -lgcc $(libs-y)
INCLUDE  = --include $(BUILD)/config.h $(addprefix -I$(BASEDIR)/,$(BUILD) $(includes))

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

include $(BUILD)/auto.mk

ifdef CONFIG_ARCH_ARM
  include $(_DT)/mk/arm.mk
endif

includes :=
objs :=
define collect_vars
  include-y :=
  subdir-y :=
  obj-y :=
  include $(BASEDIR)/$(1)/Makefile
  includes := $$(includes) $$(addprefix $(1)/,$$(include-y))
  objs := $$(objs) $$(addprefix $(BUILD)/$(1)/,$$(obj-y))
  $$(foreach dir,$$(subdir-y),\
    $$(eval dirs += $(1)/$$(dir))\
    $$(eval $$(call collect_vars,$(1)/$$(dir)))\
  )
endef

dirs := $(srcdirs)
$(foreach dir,$(srcdirs),\
	$(eval $(call collect_vars,$(dir)))\
)

all: $(BUILD)/$(target)
	@$(MAKE) -s -f $(firstword $(MAKEFILE_LIST)) deps

-include $(BUILD)/deps.mk

.PHONY: deps
deps:
	@rm -f $(BUILD)/deps.mk
	@$(foreach dir,$(dirs),\
	  $(foreach file,$(wildcard $(BUILD)/$(dir)/*.d),\
	    cat $(file) >> $(BUILD)/deps.mk;\
	  )\
	)

$(BUILD)/$(basename $(target)).elf: $(BUILD)/$(ld_script) $(objs)
	@mkdir -p $(@D)
	$(D) "   LD       $<"
	$(Q)$(CC) $(CFLAGS) $(LDFLAGS) -T $^ $(LIBS) -o $@

$(BUILD)/%.o: $(BASEDIR)/%.S
	@mkdir -p $(@D)
	$(D) "   AS       $<"
	$(Q)$(CC) -c -MMD -MP -MF $@.d -MQ $@ $(CFLAGS) $(ASFLAGS) $(INCLUDE) $< -o $@

$(BUILD)/%.o: $(BASEDIR)/%.c
	@mkdir -p $(@D)
	$(D) "   CC       $<"
	$(Q)$(CC) -c -MMD -MP -MF $@.d -MQ $@ $(CFLAGS) $(INCLUDE) $< -o $@

$(BUILD)/%: $(BASEDIR)/%.in
	@mkdir -p $(@D)
	$(D) "   CPP      $<"
	$(Q)$(CPP) -P -MMD -MP -MF $@.d -MQ $@ -x c -DBUILD=$(BUILD:./%=%) $(INCLUDE) $< -o $@

.PHONY: clean
clean:
	@rm -f $(BUILD)/$(ld_script).d
	@rm -f $(addsuffix .d,$(objs))
	@rm -f $(BUILD)/deps.mk
	@rm -f $(BUILD)/$(ld_script)
	@rm -f $(objs)
	@rm -rf $(addprefix $(BUILD)/,$(dirs))
	@rm -f $(BUILD)/$(basename $(target)).map
	@rm -f $(BUILD)/$(basename $(target)).dis
	@rm -f $(BUILD)/$(basename $(target)).elf
	@rm -f $(BUILD)/$(basename $(target)).bin

