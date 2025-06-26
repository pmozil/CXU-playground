MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

BOARD?=arty_s7
BUILD_DIR?=$(abspath $(MAKEFILE_DIR)../build/$(BOARD))

include $(BUILD_DIR)/software/include/generated/variables.mak
include $(SOC_DIRECTORY)/software/common.mak

# pull in dependency info for *existing* .o files
-include $(OBJECTS:.o=.d)

%.bin: %.elf
	$(OBJCOPY) -O binary $< $@
	chmod -x $@

crt0.o: $(CPU_DIRECTORY)/crt0.S
	$(assemble)

%.o: %.c
	$(compile)

%.o: %.S
	$(assemble)
