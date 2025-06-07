# usage:
# 1) make BUILD_DIR=<the directory where you generated the SOC>
#   (for instance, LiteX/build/radiona_ulx3s)
#   Alternatively you can edit this file and change LITEX_DIR and
#   LITEX_PLATFORM below.
# 2) litex_term /dev/ttyUSBnnn --kernel demo.bin
# 3) litex> reboot

include ../common.mk


OBJ_DIR=build

OBJECTS   = $(CPU_DIRECTORY)/crt0.o
OBJECTS   += $(patsubst %.c,%.o,$(wildcard *.c */*.c */*/*.c))

all: demo.bin

vpath %.a $(PACKAGES:%=../%)

demo.elf: $(OBJECTS)
	echo $(LIBS:lib%=-l%)
	$(CC) $(LDFLAGS) -T linker.ld -N -o $@ \
		$(OBJECTS) \
		$(PACKAGES:%=-L$(BUILD_DIR)/software/%) \
		-Wl,--whole-archive \
		-Wl,--gc-sections \
		-Wl,-Map,$@.map \
		$(LIBS:lib%=-l%)

-include $(OBJECTS:.o=.d)

VPATH = $(BIOS_DIRECTORY):$(BIOS_DIRECTORY)/cmds:$(CPU_DIRECTORY)

$(OBJ_DIR)/%.o: %.cpp
	$(compilexx)

$(OBJ_DIR)/%.o: %.c
	$(compile)

$(OBJ_DIR)/%.o: %.S
	$(assemble)

clean:
	$(RM) $(OBJECTS) $(OBJECTS:.o=.d) demo.elf demo.bin .*~ *~ *.d

.PHONY: all clean
