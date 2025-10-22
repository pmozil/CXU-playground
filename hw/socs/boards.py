#!/usr/bin/env python3

#
# This file is part of Linux-on-LiteX-VexRiscv
#
# Copyright (c) 2019-2024, Linux-on-LiteX-VexRiscv Developers
# SPDX-License-Identifier: BSD-2-Clause

# Patched add_cpu  and init for soc ------------------------------------------------------------


def patched_init(
    self,
    platform,
    clk_freq,
    # Bus parameters.
    bus_standard="wishbone",
    bus_data_width=32,
    bus_address_width=32,
    bus_timeout=1e6,
    bus_bursting=False,
    bus_interconnect="shared",
    # CPU parameters.
    cpu_type="vexriscv",
    cpu_reset_address=None,
    cpu_variant=None,
    cpu_cfu=None,
    # CFU parameters.
    cfu_filename=None,
    cxus=None,
    # ROM parameters.
    integrated_rom_size=0,
    integrated_rom_mode="rx",
    integrated_rom_init=[],
    # SRAM parameters.
    integrated_sram_size=0x2000,
    integrated_sram_init=[],
    # MAIN_RAM parameters.
    integrated_main_ram_size=0,
    integrated_main_ram_init=[],
    # CSR parameters.
    csr_data_width=32,
    csr_address_width=14,
    csr_paging=0x800,
    csr_ordering="big",
    # Interrupt parameters.
    irq_n_irqs=32,
    # Identifier parameters.
    ident="",
    ident_version=False,
    # UART parameters.
    with_uart=True,
    uart_name="serial",
    uart_baudrate=115200,
    uart_fifo_depth=16,
    uart_pads=None,
    uart_with_dynamic_baudrate=False,
    # Timer parameters.
    with_timer=True,
    timer_uptime=False,
    # Controller parameters.
    with_ctrl=True,
    # JTAGBone.
    with_jtagbone=False,
    jtagbone_chain=1,
    # UARTBone.
    with_uartbone=False,
    # Watchdog.
    with_watchdog=False,
    watchdog_width=32,
    watchdog_reset_delay=None,
    # Others.
    **kwargs,
):
    from litex.soc.integration.soc import LiteXSoC

    # New LiteXSoC class -----------------------------------------------------------------------
    LiteXSoC.__init__(
        self,
        platform,
        clk_freq,
        bus_standard=bus_standard,
        bus_data_width=bus_data_width,
        bus_address_width=bus_address_width,
        bus_timeout=bus_timeout,
        bus_bursting=bus_bursting,
        bus_interconnect=bus_interconnect,
        bus_reserved_regions={},
        csr_data_width=csr_data_width,
        csr_address_width=csr_address_width,
        csr_paging=csr_paging,
        csr_ordering=csr_ordering,
        csr_reserved_csrs=self.csr_map,
        irq_n_irqs=irq_n_irqs,
        irq_reserved_irqs={},
    )

    # Attributes.
    self.mem_regions = self.bus.regions
    self.clk_freq = self.sys_clk_freq
    self.mem_map = self.mem_map
    self.config = {}

    # Parameters management --------------------------------------------------------------------

    # CPU.
    cpu_type = None if cpu_type == "None" else cpu_type
    cpu_reset_address = None if cpu_reset_address == "None" else cpu_reset_address

    self.cpu_type = cpu_type
    self.cpu_variant = cpu_variant

    # ROM.
    # Initialize ROM from binary file when provided.
    if isinstance(integrated_rom_init, str):
        integrated_rom_init = get_mem_data(
            integrated_rom_init,
            endianness="little",  # FIXME: Depends on CPU.
            data_width=bus_data_width,
        )
        integrated_rom_size = 4 * len(integrated_rom_init)

    # Disable ROM when no CPU/hard-CPU.
    if cpu_type in [None, "zynq7000", "zynqmp", "eos_s3"]:
        integrated_rom_init = []
        integrated_rom_size = 0
    self.integrated_rom_size = integrated_rom_size
    self.integrated_rom_initialized = integrated_rom_init != []

    # SRAM.
    self.integrated_sram_size = integrated_sram_size

    # MAIN RAM.
    self.integrated_main_ram_size = integrated_main_ram_size

    # CSRs.
    self.csr_data_width = csr_data_width

    # Wishbone Slaves.
    self.wb_slaves = {}

    # Parameters check validity ----------------------------------------------------------------

    # FIXME: Move to soc.py?

    if with_uart:
        # crossover+uartbone is kept as backward compatibility
        if uart_name == "crossover+uartbone":
            self.logger.warning(
                "{} UART: is deprecated {}".format(
                    colorer(uart_name, color="yellow"),
                    colorer(
                        'please use --uart-name="crossover" --with-uartbone',
                        color="red",
                    ),
                )
            )
            time.sleep(2)
            # Already configured.
            self._uartbone = True
            uart_name = "crossover"

        # JTAGBone and jtag_uart can't be used at the same time.
        assert not (with_jtagbone and uart_name == "jtag_uart")

        # UARTBone and serial can't be used at the same time.
        assert not (with_uartbone and uart_name == "serial")

    # Modules instances ------------------------------------------------------------------------

    # Add SoCController.
    if with_ctrl:
        self.add_controller("ctrl")

    # Add CPU.
    self.add_cpu(
        name=str(cpu_type),
        variant="standard" if cpu_variant is None else cpu_variant,
        reset_address=None if integrated_rom_size else cpu_reset_address,
        cfu=cpu_cfu,
        cxus=cxus,
    )

    # Add User's interrupts.
    if self.irq.enabled:
        for name, loc in self.interrupt_map.items():
            self.irq.add(name, loc)

    # Add integrated ROM.
    if integrated_rom_size:
        self.add_rom(
            "rom",
            origin=self.cpu.reset_address,
            size=integrated_rom_size,
            contents=integrated_rom_init,
            mode=integrated_rom_mode,
        )

    # Add integrated SRAM.
    if integrated_sram_size:
        self.add_ram(
            "sram",
            origin=self.mem_map["sram"],
            size=integrated_sram_size,
        )

    # Add integrated MAIN_RAM (only useful when no external SRAM/SDRAM is available).
    if integrated_main_ram_size:
        self.add_ram(
            "main_ram",
            origin=self.mem_map["main_ram"],
            size=integrated_main_ram_size,
            contents=integrated_main_ram_init,
        )

    # Add Identifier.
    if ident != "":
        self.add_identifier(
            "identifier", identifier=ident, with_build_time=ident_version
        )

    # Add UARTBone.
    if with_uartbone:
        self.add_uartbone(
            baudrate=uart_baudrate, with_dynamic_baudrate=uart_with_dynamic_baudrate
        )

    # Add UART.
    if with_uart:
        self.add_uart(
            name="uart",
            uart_name=uart_name,
            uart_pads=uart_pads,
            baudrate=uart_baudrate,
            fifo_depth=uart_fifo_depth,
            with_dynamic_baudrate=uart_with_dynamic_baudrate,
        )

    # Add JTAGBone.
    if with_jtagbone:
        self.add_jtagbone(chain=jtagbone_chain)

    # Add Timer.
    if with_timer:
        self.add_timer(name="timer0")
        if timer_uptime:
            self.timer0.add_uptime()

    # Add Watchdog.
    if with_watchdog:
        self.add_watchdog(
            name="watchdog0", width=watchdog_width, reset_delay=watchdog_reset_delay
        )


def add_cpu(
    self, name="vexriscv", variant="standard", reset_address=None, cfu=None, cxus=None
):
    import os
    import sys
    import math
    import time
    import logging
    import argparse
    import datetime

    # from migen import *
    from litex.gen import colorer
    from litex.gen import LiteXModule, LiteXContext
    from litex.gen.genlib.misc import WaitTimer
    from litex.gen.fhdl.hierarchy import LiteXHierarchyExplorer

    # from litex.compat.soc_core import *

    # from litex.soc.interconnect.csr import *
    # from litex.soc.interconnect.csr_eventmanager import *
    from litex.soc.interconnect import csr_bus
    from litex.soc.interconnect import stream
    from litex.soc.interconnect import wishbone
    from litex.soc.interconnect import axi
    from litex.soc.interconnect import ahb
    from litex.soc.integration.soc import SoCIORegion
    from litex.soc.cores import cpu

    print("##############################PATCHED ADD CPU##############################")

    # Check that CPU is supported.
    if name not in cpu.CPUS.keys():
        supported_cpus = []
        cpu_name_length = max([len(cpu_name) for cpu_name in cpu.CPUS.keys()])
        for cpu_name in sorted(cpu.CPUS.keys()):
            cpu_cls = cpu.CPUS[cpu_name]
            cpu_desc = f"{cpu_cls.family}\t/ {cpu_cls.category}"
            supported_cpus += [
                f"- {cpu_name}{' '*(cpu_name_length - len(cpu_name))} ({cpu_desc})"
            ]
        self.logger.error(
            "{} CPU {}, supported are: \n{}".format(
                colorer(name),
                colorer("not supported", color="red"),
                colorer("\n".join(supported_cpus)),
            )
        )
        raise SoCError()

    # Add CPU.
    cpu_cls = cpu.CPUS[name]
    if (variant not in cpu_cls.variants) and (cpu_cls is not cpu.CPUNone):
        self.logger.error(
            "{} CPU variant {}, supported are: \n - {}".format(
                colorer(variant),
                colorer("not supported", color="red"),
                colorer("\n - ".join(sorted(cpu_cls.variants))),
            )
        )
        raise SoCError()
    self.check_if_exists("cpu")
    if cpu_cls is cpu.CPUNone:
        self.cpu = cpu_cls(self.bus.data_width, self.bus.address_width)
    else:
        self.cpu = cpu_cls(self.platform, variant)
    self.logger.info(
        "CPU {} {}.".format(
            colorer(name, color="underline"), colorer("added", color="green")
        )
    )

    # Add optional CFU plugin.
    if "cfu" in variant and hasattr(self.cpu, "add_cfu"):
        self.cpu.add_cfu(cfu_filename=cfu)

    # Add optional CXU plugin.
    if "cxu" in variant and hasattr(self.cpu, "add_cxus"):
        self.cpu.add_cxus(cxus=cxus)

    # Update SoC with CPU constraints.
    # IO regions.
    for n, (origin, size) in enumerate(self.cpu.io_regions.items()):
        self.logger.info(
            "CPU {} {} IO Region {} at {} (Size: {}).".format(
                colorer(name, color="underline"),
                colorer("adding", color="cyan"),
                colorer(n),
                colorer(f"0x{origin:08x}"),
                colorer(f"0x{size:08x}"),
            )
        )
        self.bus.add_region(
            "io{}".format(n), SoCIORegion(origin=origin, size=size, cached=False)
        )
    # Mapping.
    if isinstance(self.cpu, cpu.CPUNone):
        # With CPUNone, give priority to User's mapping.
        self.mem_map = {**self.cpu.mem_map, **self.mem_map}
        # With CPUNone, disable IO regions check.
        self.bus.io_regions_check = False
    else:
        # Override User's mapping with CPU constrainted mapping (and warn User).
        for n, origin in self.cpu.mem_map.items():
            if n in self.mem_map.keys() and self.mem_map[n] != self.cpu.mem_map[n]:
                self.logger.info(
                    "CPU {} {} {} mapping from {} to {}.".format(
                        colorer(name, color="underline"),
                        colorer("overriding", color="cyan"),
                        colorer(n),
                        colorer(f"0x{self.mem_map[n]:08x}"),
                        colorer(f"0x{self.cpu.mem_map[n]:08x}"),
                    )
                )
        self.mem_map.update(self.cpu.mem_map)

    # Add Bus Masters/CSR/IRQs.
    if not isinstance(self.cpu, cpu.CPUNone):
        # Reset Address.
        if reset_address is None:
            reset_address = self.mem_map["rom"]
        self.logger.info(
            "CPU {} {} reset address to {}.".format(
                colorer(name, color="underline"),
                colorer("setting", color="cyan"),
                colorer(f"0x{reset_address:08x}"),
            )
        )
        self.cpu.set_reset_address(reset_address)

        # Bus Masters.
        self.logger.info(
            "CPU {} {} Bus Master(s).".format(
                colorer(name, color="underline"), colorer("adding", color="cyan")
            )
        )
        for n, cpu_bus in enumerate(self.cpu.periph_buses):
            self.bus.add_master(name="cpu_bus{}".format(n), master=cpu_bus)

        # Interrupts.
        if hasattr(self.cpu, "interrupt"):
            self.logger.info(
                "CPU {} {} Interrupt(s).".format(
                    colorer(name, color="underline"), colorer("adding", color="cyan")
                )
            )
            self.irq.enable()
            if hasattr(self.cpu, "reserved_interrupts"):
                self.cpu.interrupts.update(self.cpu.reserved_interrupts)
            for irq_name, loc in self.cpu.interrupts.items():
                self.irq.add(irq_name, loc)
            self.add_config("CPU_HAS_INTERRUPT")

        # Create optional DMA Bus (for Cache Coherence).
        if hasattr(self.cpu, "dma_bus"):
            if isinstance(self.cpu.dma_bus, wishbone.Interface):
                dma_bus_standard = "wishbone"
            elif isinstance(self.cpu.dma_bus, axi.AXILiteInterface):
                dma_bus_standard = "axi_lite"
            elif isinstance(self.cpu.dma_bus, axi.AXIInterface):
                dma_bus_standard = "axi"
            else:
                raise NotImplementedError
            self.logger.info(
                "CPU {} {} DMA Bus.".format(
                    colorer(name, color="underline"), colorer("adding", color="cyan")
                )
            )
            self.dma_bus = SoCBusHandler(
                name="SoCDMABusHandler",
                standard=dma_bus_standard,
                data_width=self.cpu.dma_bus.data_width,
                address_width=self.cpu.dma_bus.address_width,
                bursting=self.cpu.dma_bus.bursting,
            )
            self.dma_bus.add_slave(
                name="dma",
                slave=self.cpu.dma_bus,
                region=SoCRegion(origin=0x00000000, size=0x100000000),
            )  # FIXME: covers lower 4GB only

        # Connect SoCController's reset to CPU reset.
        if hasattr(self, "ctrl"):
            self.comb += self.cpu.reset.eq(
                # Reset the CPU on...
                getattr(self.ctrl, "soc_rst", 0)  # Full SoC Reset command...
                | getattr(self.ctrl, "cpu_rst", 0)  # or on CPU Reset command.
            )
        self.add_config("CPU_RESET_ADDR", reset_address)

    # Add CPU's SoC components (if any).
    if hasattr(self.cpu, "add_soc_components"):
        self.logger.info(
            "CPU {} {} SoC components.".format(
                colorer(name, color="underline"), colorer("adding", color="cyan")
            )
        )
        self.cpu.add_soc_components(soc=self)

    # Add constants.
    self.add_config(f"CPU_TYPE_{name}")
    self.add_config(f"CPU_VARIANT_{str(variant.split('+')[0])}")
    self.add_config("CPU_FAMILY", getattr(self.cpu, "family", "Unknown"))
    self.add_config("CPU_NAME", getattr(self.cpu, "name", "Unknown"))
    self.add_config("CPU_HUMAN_NAME", getattr(self.cpu, "human_name", "Unknown"))
    if hasattr(self.cpu, "nop"):
        self.add_config("CPU_NOP", self.cpu.nop)


# SocBoard Definition ---------------------------------------------------------------------------------


class SocBoard:
    soc_kwargs = {
        "integrated_rom_size": 0x10000,
        "integrated_sram_size": 0x1800,
        "l2_size": 0,
    }

    def __init__(self, soc_cls=None, soc_capabilities={}, soc_constants={}):
        from litex.soc.integration.soc_core import SoCCore

        setattr(SoCCore, "__init__", patched_init)
        setattr(soc_cls, "add_cpu", add_cpu)
        self.soc_cls = soc_cls
        self.soc_capabilities = soc_capabilities
        self.soc_constants = soc_constants

    def load(self, filename):
        prog = self.platform.create_programmer()
        prog.load_bitstream(filename)

    def flash(self, filename):
        prog = self.platform.create_programmer()
        prog.flash(0, filename)


# ---------------------------------------------------------------------------------------------------
# Xilinx SocBoards
# ---------------------------------------------------------------------------------------------------

# Acorn support ------------------------------------------------------------------------------------


class Acorn(SocBoard):
    soc_kwargs = {"uart_name": "jtag_uart", "sys_clk_freq": int(150e6)}

    def __init__(self):
        from litex_boards.targets import sqrl_acorn

        SocBoard.__init__(
            self,
            sqrl_acorn.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "sata",
            },
        )


# Acorn PCIe support -------------------------------------------------------------------------------


class AcornPCIe(SocBoard):
    soc_kwargs = {"uart_name": "crossover", "sys_clk_freq": int(125e6)}

    def __init__(self):
        from litex_boards.targets import sqrl_acorn

        SocBoard.__init__(
            self,
            sqrl_acorn.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "pcie",
            },
        )

    def flash(self, filename):
        prog = self.platform.create_programmer()
        prog.flash(0, filename.replace(".bin", "_fallback.bin"))


# Arty support -------------------------------------------------------------------------------------


class Arty(SocBoard):
    def __init__(self):
        from litex_boards.targets import digilent_arty

        SocBoard.__init__(
            self,
            digilent_arty.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
                # Storage
                "spiflash",
                "sdcard",
                # GPIOs
                "leds",
                "rgb_led",
                "switches",
                # Buses
                "spi",
                "i2c",
            },
        )


class ArtyA7(Arty):
    pass


class ArtyS7(SocBoard):
    def __init__(self):
        from litex_boards.targets import digilent_arty_s7

        SocBoard.__init__(
            self,
            digilent_arty_s7.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "spiflash",
                # GPIOs
                "leds",
                "rgb_led",
                "switches",
                # Buses
                "spi",
                "i2c",
            },
        )


# NeTV2 support ------------------------------------------------------------------------------------


class NeTV2(SocBoard):
    def __init__(self):
        from litex_boards.targets import kosagi_netv2

        SocBoard.__init__(
            self,
            kosagi_netv2.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
                # Storage
                "sdcard",
                # GPIOs
                "leds",
                # Video
                "framebuffer",
            },
        )


# Genesys2 support ---------------------------------------------------------------------------------


class Genesys2(SocBoard):
    def __init__(self):
        from litex_boards.targets import digilent_genesys2

        SocBoard.__init__(
            self,
            digilent_genesys2.BaseSoC,
            soc_capabilities={
                # Communication
                "usb_fifo",
                "ethernet",
                # Storage
                "sdcard",
            },
        )


# KC705 support ---------------------------------------------------------------------------------


class KC705(SocBoard):
    def __init__(self):
        from litex_boards.targets import xilinx_kc705

        SocBoard.__init__(
            self,
            xilinx_kc705.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
                # Storage
                "sdcard",
                # "sata",
                # GPIOs
                "leds",
            },
        )


# VC707 support ---------------------------------------------------------------------------------


class VC707(SocBoard):
    def __init__(self):
        from litex_boards.targets import xilinx_vc707

        SocBoard.__init__(
            self,
            xilinx_vc707.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
                # Storage
                "sdcard",
                # GPIOs
                "leds",
            },
        )


# KCU105 support -----------------------------------------------------------------------------------


class KCU105(SocBoard):
    def __init__(self):
        from litex_boards.targets import xilinx_kcu105

        SocBoard.__init__(
            self,
            xilinx_kcu105.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
                # Storage
                "sdcard",
            },
        )


# AESKU40 support -----------------------------------------------------------------------------------


class AESKU40(SocBoard):
    soc_kwargs = {"uart_baudrate": 115.2e3}

    def __init__(self):
        from litex_boards.targets import avnet_aesku40

        SocBoard.__init__(
            self,
            avnet_aesku40.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
                # Storage
                "sdcard",
            },
        )


# ZCU104 support -----------------------------------------------------------------------------------


class ZCU104(SocBoard):
    def __init__(self):
        from litex_boards.targets import xilinx_zcu104

        SocBoard.__init__(
            self,
            xilinx_zcu104.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
            },
        )


# Nexys4DDR support --------------------------------------------------------------------------------


class Nexys4DDR(SocBoard):
    def __init__(self):
        from litex_boards.targets import digilent_nexys4ddr

        SocBoard.__init__(
            self,
            digilent_nexys4ddr.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
                # Storage
                "sdcard",
                # Video
                "framebuffer",
            },
        )


# NexysVideo support -------------------------------------------------------------------------------


class NexysVideo(SocBoard):
    def __init__(self):
        from litex_boards.targets import digilent_nexys_video

        SocBoard.__init__(
            self,
            digilent_nexys_video.BaseSoC,
            soc_capabilities={
                # Communication
                "usb_fifo",
                # Storage
                "sdcard",
                # Video
                "framebuffer",
            },
        )


# MiniSpartan6 support -----------------------------------------------------------------------------


class MiniSpartan6(SocBoard):
    soc_kwargs = {"l2_size": 2048}  # Use Wishbone and L2 for memory accesses.

    def __init__(self):
        from litex_boards.targets import scarabhardware_minispartan6

        SocBoard.__init__(
            self,
            scarabhardware_minispartan6.BaseSoC,
            soc_capabilities={
                # Communication
                "usb_fifo",
                # Storage
                "sdcard",
                # Video
                "framebuffer",
            },
        )


# Pipistrello support ------------------------------------------------------------------------------


class Pipistrello(SocBoard):
    soc_kwargs = {"l2_size": 2048}  # Use Wishbone and L2 for memory accesses.

    def __init__(self):
        from litex_boards.targets import saanlima_pipistrello

        SocBoard.__init__(
            self,
            saanlima_pipistrello.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
            },
        )


# XCU1525 support ----------------------------------------------------------------------------------


class XCU1525(SocBoard):
    def __init__(self):
        from litex_boards.targets import sqrl_xcu1525

        SocBoard.__init__(
            self,
            sqrl_xcu1525.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "sata",
            },
        )


# AlveoU280 (ES1) support -------------------------------------------------------------------------------


class AlveoU280(SocBoard):
    soc_kwargs = {"with_hbm": True, "sys_clk_freq": 250e6}  # Use HBM @ 250MHz (Min).

    def __init__(self):
        from litex_boards.targets import xilinx_alveo_u280

        SocBoard.__init__(
            self,
            xilinx_alveo_u280.BaseSoC,
            soc_capabilities={
                # Communication
                "serial"
            },
        )


# AlveoU250 support -------------------------------------------------------------------------------


class AlveoU250(SocBoard):
    def __init__(self):
        from litex_boards.targets import xilinx_alveo_u250

        SocBoard.__init__(
            self,
            xilinx_alveo_u250.BaseSoC,
            soc_capabilities={
                # Communication
                "serial"
            },
        )


# SDS1104X-E support -------------------------------------------------------------------------------


class SDS1104XE(SocBoard):
    soc_kwargs = {"l2_size": 8192}  # Use Wishbone and L2 for memory accesses.

    def __init__(self):
        from litex_boards.targets import siglent_sds1104xe

        SocBoard.__init__(
            self,
            siglent_sds1104xe.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
                # Video
                "framebuffer",
            },
        )

    def load(self, filename):
        prog = self.platform.create_programmer()
        prog.load_bitstream(filename, device=1)


# QMTECH WuKong support ---------------------------------------------------------------------------


class Qmtech_WuKong(SocBoard):
    def __init__(self):
        from litex_boards.targets import qmtech_wukong

        SocBoard.__init__(
            self,
            qmtech_wukong.BaseSoC,
            soc_capabilities={
                "leds",
                # Communication
                "serial",
                "ethernet",
                # Video
                "framebuffer",
            },
        )


# MNT RKX7 support ---------------------------------------------------------------------------------


class MNT_RKX7(SocBoard):
    def __init__(self):
        from litex_boards.targets import mnt_rkx7

        SocBoard.__init__(
            self,
            mnt_rkx7.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "spisdcard",
            },
        )


# STLV7325 -----------------------------------------------------------------------------------------


class STLV7325(SocBoard):
    def __init__(self):
        from litex_boards.targets import sitlinv_stlv7325_v1

        SocBoard.__init__(
            self,
            sitlinv_stlv7325_v1.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "sdcard",
            },
        )


class STLV7325_v2(SocBoard):
    def __init__(self):
        from litex_boards.targets import sitlinv_stlv7325_v2

        SocBoard.__init__(
            self,
            sitlinv_stlv7325_v2.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "sdcard",
            },
        )


# Decklink Quad HDMI Recorder ----------------------------------------------------------------------


class DecklinkQuadHDMIRecorder(SocBoard):
    soc_kwargs = {"uart_name": "crossover", "sys_clk_freq": int(125e6)}

    def __init__(self):
        from litex_boards.targets import decklink_quad_hdmi_recorder

        SocBoard.__init__(
            self,
            decklink_quad_hdmi_recorder.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "pcie",
            },
        )


# HSEDA XC7A35T -----------------------------------------------------------------------------------
class HSEDA_xc7a35t(SocBoard):
    soc_kwargs = {"sys_clk_freq": int(80e6)}

    def __init__(self):
        from litex_boards.targets import hseda_xc7a35t

        SocBoard.__init__(
            self,
            hseda_xc7a35t.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
            },
        )


# ---------------------------------------------------------------------------------------------------
# Lattice SocBoards
# ---------------------------------------------------------------------------------------------------

# Versa ECP5 support -------------------------------------------------------------------------------


class VersaECP5(SocBoard):
    def __init__(self):
        from litex_boards.targets import lattice_versa_ecp5

        SocBoard.__init__(
            self,
            lattice_versa_ecp5.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
            },
        )


# ULX3S support ------------------------------------------------------------------------------------


class ULX3S(SocBoard):
    soc_kwargs = {"l2_size": 2048}  # Use Wishbone and L2 for memory accesses.

    def __init__(self):
        from litex_boards.targets import radiona_ulx3s

        SocBoard.__init__(
            self,
            radiona_ulx3s.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "sdcard",
                # Video,
                "framebuffer",
            },
        )


# ULX4M-LD-V2 support ------------------------------------------------------------------------------------
class ULX4M_LD_V2(SocBoard):
    soc_kwargs = {
        "uart_name": "serial",
        "sys_clk_freq": int(50e6),
        "l2_size": 2048,
    }  # 2048 } #32768} # Use Wishbone and L2 for memory accesse$

    def __init__(self):
        from litex_boards.targets import radiona_ulx4m_ld_v2

        SocBoard.__init__(
            self,
            radiona_ulx4m_ld_v2.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "sdcard",
                # Video,
                "framebuffer",
                "video_terminal",
            },
        )


# HADBadge support ---------------------------------------------------------------------------------


class HADBadge(SocBoard):
    soc_kwargs = {"l2_size": 2048}  # Use Wishbone and L2 for memory accesses.

    def __init__(self):
        from litex_boards.targets import hackaday_hadbadge

        SocBoard.__init__(
            self,
            hackaday_hadbadge.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
            },
        )

    def load(self, filename):
        os.system("dfu-util --alt 2 --download {} --reset".format(filename))


# OrangeCrab support -------------------------------------------------------------------------------


class OrangeCrab(SocBoard):
    soc_kwargs = {
        "sys_clk_freq": int(64e6)
    }  # Increase sys_clk_freq to 64MHz (48MHz default).

    def __init__(self):
        from litex_boards.targets import gsd_orangecrab

        SocBoard.__init__(
            self,
            gsd_orangecrab.BaseSoC,
            soc_capabilities={
                # Communication
                "usb_acm",
                # Buses
                "i2c",
                # Storage
                "sdcard",
            },
        )


# Butterstick support ------------------------------------------------------------------------------


class ButterStick(SocBoard):
    soc_kwargs = {"uart_name": "jtag_uart"}

    def __init__(self):
        from litex_boards.targets import gsd_butterstick

        SocBoard.__init__(
            self,
            gsd_butterstick.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
            },
        )


# Cam Link 4K support ------------------------------------------------------------------------------


class CamLink4K(SocBoard):
    def __init__(self):
        from litex_boards.targets import camlink_4k

        SocBoard.__init__(
            self,
            camlink_4k.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
            },
        )

    def load(self, filename):
        os.system("camlink configure {}".format(filename))


# TrellisSocBoard support -----------------------------------------------------------------------------


class TrellisSocBoard(SocBoard):
    def __init__(self):
        from litex_boards.targets import trellisboard

        SocBoard.__init__(
            self,
            trellisboard.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "sdcard",
            },
        )


# ECPIX5 support -----------------------------------------------------------------------------------


class ECPIX5(SocBoard):
    def __init__(self):
        from litex_boards.targets import lambdaconcept_ecpix5

        SocBoard.__init__(
            self,
            lambdaconcept_ecpix5.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
                # Storage
                "sdcard",
            },
        )


# Colorlight i5 support ----------------------------------------------------------------------------


class Colorlight_i5(SocBoard):
    soc_kwargs = {"l2_size": 2048}  # Use Wishbone and L2 for memory accesses.

    def __init__(self):
        from litex_boards.targets import colorlight_i5

        SocBoard.__init__(
            self,
            colorlight_i5.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "ethernet",
            },
        )


# Icesugar Pro support -----------------------------------------------------------------------------


class IcesugarPro(SocBoard):
    soc_kwargs = {"l2_size": 2048}  # Use Wishbone and L2 for memory accesses.

    def __init__(self):
        from litex_boards.targets import muselab_icesugar_pro

        SocBoard.__init__(
            self,
            muselab_icesugar_pro.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "spiflash",
                "sdcard",
            },
        )


# Schoko support -----------------------------------------------------------------------------------


class Schoko(SocBoard):
    soc_kwargs = {"l2_size": 8192}

    def __init__(self):
        from litex_boards.targets import machdyne_schoko

        SocBoard.__init__(
            self,
            machdyne_schoko.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "usb_host",
                # Storage
                "spiflash",
                # "sdcard",
                "spisdcard",
                # Video,
                "framebuffer",
            },
        )


# Konfekt support -----------------------------------------------------------------------------------


class Konfekt(SocBoard):
    soc_kwargs = {"l2_size": 0}

    def __init__(self):
        from litex_boards.targets import machdyne_konfekt

        SocBoard.__init__(
            self,
            machdyne_konfekt.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "usb_host",
                # Storage
                # "spiflash",
                "spisdcard",
                # "sdcard",
                # Video,
                "framebuffer",
            },
        )


# Noir support -----------------------------------------------------------------------------------


class Noir(SocBoard):
    soc_kwargs = {"l2_size": 8192}

    def __init__(self):
        from litex_boards.targets import machdyne_noir

        SocBoard.__init__(
            self,
            machdyne_noir.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "usb_host",
                # Storage
                "spiflash",
                "spisdcard",
                # "sdcard",
                # Video,
                "framebuffer",
            },
        )


# ---------------------------------------------------------------------------------------------------
# Intel SocBoards
# ---------------------------------------------------------------------------------------------------

# De10Nano support ---------------------------------------------------------------------------------


class De10Nano(SocBoard):
    soc_kwargs = {
        "with_mister_sdram": True,  # Add MiSTer SDRAM extension.
        "l2_size": 2048,  # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000,  # Power of 2 so Quartus infers it properly.
    }

    def __init__(self):
        from litex_boards.targets import terasic_de10nano

        SocBoard.__init__(
            self,
            terasic_de10nano.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "sdcard",
                # GPIOs
                "leds",
                "switches",
            },
        )


# De0Nano support ----------------------------------------------------------------------------------


class De0Nano(SocBoard):
    soc_kwargs = {
        "l2_size": 2048,  # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000,  # Power of 2 so Quartus infers it properly.
    }

    def __init__(self):
        from litex_boards.targets import terasic_de0nano

        SocBoard.__init__(
            self,
            terasic_de0nano.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
            },
        )


# De1-SoC support ----------------------------------------------------------------------------------


class De1SoC(SocBoard):
    soc_kwargs = {
        "l2_size": 2048,  # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000,  # Power of 2 so Quartus infers it properly.
    }

    def __init__(self):
        from litex_boards.targets import terasic_de1soc

        SocBoard.__init__(
            self,
            terasic_de1soc.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # GPIOs
                "leds",
                "switches",
            },
        )


# QMTECH EP4CE15 support ---------------------------------------------------------------------------


class Qmtech_EP4CE15(SocBoard):
    soc_kwargs = {
        "variant": "ep4ce15",
        "l2_size": 2048,  # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000,  # Power of 2 so Quartus infers it properly.
    }

    def __init__(self):
        from litex_boards.targets import qmtech_ep4cex5

        SocBoard.__init__(
            self,
            qmtech_ep4cex5.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
            },
        )


# ... and its bigger brother


class Qmtech_EP4CE55(SocBoard):
    soc_kwargs = {
        "variant": "ep4ce55",
        "l2_size": 2048,  # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000,  # Power of 2 so Quartus infers it properly.
    }

    def __init__(self):
        from litex_boards.targets import qmtech_ep4cex5

        SocBoard.__init__(
            self,
            qmtech_ep4cex5.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
            },
        )


# QMTECH 5CEFA2 support
# It is possible to build the SoC --cpu-count=2 for this chip
class Qmtech_5CEFA2(SocBoard):
    soc_kwargs = {
        "variant": "5cefa2",
        "l2_size": 2048,  # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000,  # Power of 2 so Quartus infers it properly.
    }

    def __init__(self):
        from litex_boards.targets import qmtech_5cefa2

        SocBoard.__init__(
            self,
            qmtech_5cefa2.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
            },
        )


# ---------------------------------------------------------------------------------------------------
# Efinix SocBoards
# ---------------------------------------------------------------------------------------------------


class TrionT120BGA576DevKit(SocBoard):
    soc_kwargs = {"l2_size": 2048}  # Use Wishbone and L2 for memory accesses.

    def __init__(self):
        from litex_boards.targets import efinix_trion_t120_bga576_dev_kit

        SocBoard.__init__(
            self,
            efinix_trion_t120_bga576_dev_kit.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # GPIOs
                "leds",
            },
        )


class TitaniumTi60F225DevKit(SocBoard):
    soc_kwargs = {
        "with_hyperram": True,
        "sys_clk_freq": 300e6,
    }

    def __init__(self):
        from litex_boards.targets import efinix_titanium_ti60_f225_dev_kit

        SocBoard.__init__(
            self,
            efinix_titanium_ti60_f225_dev_kit.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                # Storage
                "sdcard",
                # GPIOs
                "leds",
            },
        )


# ---------------------------------------------------------------------------------------------------
# Gowin SocBoards
# ---------------------------------------------------------------------------------------------------

# Sipeed Tang Nano 20K support ---------------------------------------------------------------------


class Sipeed_tang_nano_20k(SocBoard):
    soc_kwargs = {"l2_size": 2048}  # Use Wishbone and L2 for memory accesses.

    def __init__(self):
        from litex_boards.targets import sipeed_tang_nano_20k

        SocBoard.__init__(
            self,
            sipeed_tang_nano_20k.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "sdcard",
            },
        )


# Sipeed Tang Primer 20K support -------------------------------------------------------------------


class Sipeed_tang_primer_20k(SocBoard):
    soc_kwargs = {"l2_size": 512}  # Use Wishbone and L2 for memory accesses.

    def __init__(self):
        from litex_boards.targets import sipeed_tang_primer_20k

        SocBoard.__init__(
            self,
            sipeed_tang_primer_20k.BaseSoC,
            soc_capabilities={
                # Communication
                "serial",
                "spisdcard",
            },
        )
