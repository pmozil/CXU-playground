MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

BOARD?=arty_s7
BUILD_DIR?=$(abspath $(MAKEFILE_DIR)../build/$(BOARD))

include $(BUILD_DIR)/software/include/generated/variables.mak
include $(SOC_DIRECTORY)/software/common.mak
