include ../common.mk

OBJECTS=main.o isr.o

all: firmware.bin

firmware.elf: $(OBJECTS)
	$(CC) $(LDFLAGS) \
		-T linker.ld \
		-N -o $@ \
		$(OBJECTS) \
		$(PACKAGES:%=-L$(BUILD_DIR)/software/%) \
		$(LIBS:lib%=-l%)
	chmod -x $@

main.o: main.c
	$(compile)

clean:
	$(RM) $(OBJECTS) $(OBJECTS:.o=.d) firmware.elf* firmware.bin crt0.d crt0.o .*~ *~

.PHONY: all main.o clean load
