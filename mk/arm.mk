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

cflags-y += -mlittle-endian -msoft-float
cflags-$(CONFIG_CPU_ARM926T) += -mtune=arm9tdmi -march=armv5te

ifdef CONFIG_ARCH_ARM_THUMB
  cflags-y += -mthumb
endif

$(basename $(target)).bin: $(basename $(target)).elf
	$(D) "   OBJDUMP  $(@:.bin=.dis)"
	$(Q)$(OBJDUMP) -d -m armv5te $< > $(OBJDIR)/$(@:.bin=.dis)
	$(D) "   OBJCOPY  $@"
	$(Q)$(OBJCOPY) -S -I elf32-littlearm -O binary $< $@
	@echo
	@$(SIZE) --target=binary $@

