#!/usr/bin/env python3

#
# This file is part of Linux-on-LiteX-VexRiscv
#
# Copyright (c) 2019-2024, Linux-on-LiteX-VexRiscv Developers
# SPDX-License-Identifier: BSD-2-Clause

# SocBoard Definition ---------------------------------------------------------------------------------

class SocBoard:
    soc_kwargs = {
        "integrated_rom_size"  : 0x10000,
        "integrated_sram_size" : 0x1800,
        "l2_size"              : 0
    }
    def __init__(self, soc_cls=None, soc_capabilities={}, soc_constants={}):
        self.soc_cls          = soc_cls
        self.soc_capabilities = soc_capabilities
        self.soc_constants    = soc_constants

    def load(self, filename):
        prog = self.platform.create_programmer()
        prog.load_bitstream(filename)

    def flash(self, filename):
        prog = self.platform.create_programmer()
        prog.flash(0, filename)

#---------------------------------------------------------------------------------------------------
# Xilinx SocBoards
#---------------------------------------------------------------------------------------------------

# Acorn support ------------------------------------------------------------------------------------

class Acorn(SocBoard):
    soc_kwargs = {"uart_name": "jtag_uart", "sys_clk_freq": int(150e6)}
    def __init__(self):
        from litex_boards.targets import sqrl_acorn
        SocBoard.__init__(self, sqrl_acorn.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "sata",
        })

# Acorn PCIe support -------------------------------------------------------------------------------

class AcornPCIe(SocBoard):
    soc_kwargs = {"uart_name": "crossover", "sys_clk_freq": int(125e6)}
    def __init__(self):
        from litex_boards.targets import sqrl_acorn
        SocBoard.__init__(self, sqrl_acorn.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "pcie",
        })

    def flash(self, filename):
        prog = self.platform.create_programmer()
        prog.flash(0, filename.replace(".bin", "_fallback.bin"))

# Arty support -------------------------------------------------------------------------------------

class Arty(SocBoard):
    def __init__(self):
        from litex_boards.targets import digilent_arty
        SocBoard.__init__(self, digilent_arty.BaseSoC, soc_capabilities={
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
        })

class ArtyA7(Arty): pass

class ArtyS7(SocBoard):
    def __init__(self):
        from litex_boards.targets import digilent_arty_s7
        SocBoard.__init__(self, digilent_arty_s7.BaseSoC, soc_capabilities={
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
        })

# NeTV2 support ------------------------------------------------------------------------------------

class NeTV2(SocBoard):
    def __init__(self):
        from litex_boards.targets import kosagi_netv2
        SocBoard.__init__(self, kosagi_netv2.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "ethernet",
            # Storage
            "sdcard",
            # GPIOs
            "leds",
            # Video
            "framebuffer",
        })

# Genesys2 support ---------------------------------------------------------------------------------

class Genesys2(SocBoard):
    def __init__(self):
        from litex_boards.targets import digilent_genesys2
        SocBoard.__init__(self, digilent_genesys2.BaseSoC, soc_capabilities={
            # Communication
            "usb_fifo",
            "ethernet",
            # Storage
            "sdcard",
        })

# KC705 support ---------------------------------------------------------------------------------

class KC705(SocBoard):
    def __init__(self):
        from litex_boards.targets import xilinx_kc705
        SocBoard.__init__(self, xilinx_kc705.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "ethernet",
            # Storage
            "sdcard",
            #"sata",
            # GPIOs
            "leds",
        })

# VC707 support ---------------------------------------------------------------------------------

class VC707(SocBoard):
    def __init__(self):
        from litex_boards.targets import xilinx_vc707
        SocBoard.__init__(self, xilinx_vc707.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "ethernet",
            # Storage
            "sdcard",
            # GPIOs
            "leds",
        })

# KCU105 support -----------------------------------------------------------------------------------

class KCU105(SocBoard):
    def __init__(self):
        from litex_boards.targets import xilinx_kcu105
        SocBoard.__init__(self, xilinx_kcu105.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "ethernet",
            # Storage
            "sdcard",
        })

# AESKU40 support -----------------------------------------------------------------------------------

class AESKU40(SocBoard):
    soc_kwargs = {"uart_baudrate": 115.2e3} 
    def __init__(self):
        from litex_boards.targets import avnet_aesku40
        SocBoard.__init__(self, avnet_aesku40.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "ethernet",
            # Storage
            "sdcard",
        })

# ZCU104 support -----------------------------------------------------------------------------------

class ZCU104(SocBoard):
    def __init__(self):
        from litex_boards.targets import xilinx_zcu104
        SocBoard.__init__(self, xilinx_zcu104.BaseSoC, soc_capabilities={
            # Communication
            "serial",
        })

# Nexys4DDR support --------------------------------------------------------------------------------

class Nexys4DDR(SocBoard):
    def __init__(self):
        from litex_boards.targets import digilent_nexys4ddr
        SocBoard.__init__(self, digilent_nexys4ddr.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "ethernet",
            # Storage
            "sdcard",
            # Video
            "framebuffer",
        })

# NexysVideo support -------------------------------------------------------------------------------

class NexysVideo(SocBoard):
    def __init__(self):
        from litex_boards.targets import digilent_nexys_video
        SocBoard.__init__(self, digilent_nexys_video.BaseSoC, soc_capabilities={
            # Communication
            "usb_fifo",
            # Storage
            "sdcard",
            # Video
            "framebuffer",
        })

# MiniSpartan6 support -----------------------------------------------------------------------------

class MiniSpartan6(SocBoard):
    soc_kwargs = {"l2_size" : 2048} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from litex_boards.targets import scarabhardware_minispartan6
        SocBoard.__init__(self, scarabhardware_minispartan6.BaseSoC, soc_capabilities={
            # Communication
            "usb_fifo",
            # Storage
            "sdcard",
            # Video
            "framebuffer",
        })

# Pipistrello support ------------------------------------------------------------------------------

class Pipistrello(SocBoard):
    soc_kwargs = {"l2_size" : 2048} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from litex_boards.targets import saanlima_pipistrello
        SocBoard.__init__(self, saanlima_pipistrello.BaseSoC, soc_capabilities={
            # Communication
            "serial",
        })

# XCU1525 support ----------------------------------------------------------------------------------

class XCU1525(SocBoard):
    def __init__(self):
        from litex_boards.targets import sqrl_xcu1525
        SocBoard.__init__(self, sqrl_xcu1525.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "sata",
        })

# AlveoU280 (ES1) support -------------------------------------------------------------------------------

class AlveoU280(SocBoard):
    soc_kwargs = {
        "with_hbm"     : True, # Use HBM @ 250MHz (Min).
        "sys_clk_freq" : 250e6
    }
    def __init__(self):
        from litex_boards.targets import xilinx_alveo_u280
        SocBoard.__init__(self, xilinx_alveo_u280.BaseSoC, soc_capabilities={
            # Communication
            "serial"
        })

# AlveoU250 support -------------------------------------------------------------------------------

class AlveoU250(SocBoard):
    def __init__(self):
        from litex_boards.targets import xilinx_alveo_u250
        SocBoard.__init__(self, xilinx_alveo_u250.BaseSoC, soc_capabilities={
            # Communication
            "serial"
        })

# SDS1104X-E support -------------------------------------------------------------------------------

class SDS1104XE(SocBoard):
    soc_kwargs = {"l2_size" : 8192} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from litex_boards.targets import siglent_sds1104xe
        SocBoard.__init__(self, siglent_sds1104xe.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "ethernet",
            # Video
            "framebuffer",
        })

    def load(self, filename):
        prog = self.platform.create_programmer()
        prog.load_bitstream(filename, device=1)

# QMTECH WuKong support ---------------------------------------------------------------------------

class Qmtech_WuKong(SocBoard):
    def __init__(self):
        from litex_boards.targets import qmtech_wukong
        SocBoard.__init__(self, qmtech_wukong.BaseSoC, soc_capabilities={
            "leds",
            # Communication
            "serial",
            "ethernet",
            # Video
            "framebuffer",
        })


# MNT RKX7 support ---------------------------------------------------------------------------------

class MNT_RKX7(SocBoard):
    def __init__(self):
        from litex_boards.targets import mnt_rkx7
        SocBoard.__init__(self, mnt_rkx7.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "spisdcard",
        })

# STLV7325 -----------------------------------------------------------------------------------------

class STLV7325(SocBoard):
    def __init__(self):
        from litex_boards.targets import sitlinv_stlv7325_v1
        SocBoard.__init__(self, sitlinv_stlv7325_v1.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "sdcard",
        })

class STLV7325_v2(SocBoard):
    def __init__(self):
        from litex_boards.targets import sitlinv_stlv7325_v2
        SocBoard.__init__(self, sitlinv_stlv7325_v2.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "sdcard",
        })

# Decklink Quad HDMI Recorder ----------------------------------------------------------------------

class DecklinkQuadHDMIRecorder(SocBoard):
    soc_kwargs = {"uart_name": "crossover",  "sys_clk_freq": int(125e6)}
    def __init__(self):
        from litex_boards.targets import decklink_quad_hdmi_recorder
        SocBoard.__init__(self, decklink_quad_hdmi_recorder.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "pcie",
        })

# HSEDA XC7A35T -----------------------------------------------------------------------------------
class HSEDA_xc7a35t(SocBoard):
    soc_kwargs = {"sys_clk_freq": int(80e6)}
    def __init__(self):
        from litex_boards.targets import hseda_xc7a35t
        SocBoard.__init__(self, hseda_xc7a35t.BaseSoC, soc_capabilities={
            # Communication
            "serial",
        })

#---------------------------------------------------------------------------------------------------
# Lattice SocBoards
#---------------------------------------------------------------------------------------------------

# Versa ECP5 support -------------------------------------------------------------------------------

class VersaECP5(SocBoard):
    def __init__(self):
        from litex_boards.targets import lattice_versa_ecp5
        SocBoard.__init__(self, lattice_versa_ecp5.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "ethernet",
        })

# ULX3S support ------------------------------------------------------------------------------------

class ULX3S(SocBoard):
    soc_kwargs = {"l2_size" : 2048} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from litex_boards.targets import radiona_ulx3s
        SocBoard.__init__(self, radiona_ulx3s.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "sdcard",
            # Video,
            "framebuffer",
        })

# ULX4M-LD-V2 support ------------------------------------------------------------------------------------
class ULX4M_LD_V2(SocBoard):
    soc_kwargs = {"uart_name": "serial", "sys_clk_freq": int(50e6), "l2_size" : 2048} #2048 } #32768} # Use Wishbone and L2 for memory accesse$
    def __init__(self):
        from litex_boards.targets import radiona_ulx4m_ld_v2
        SocBoard.__init__(self, radiona_ulx4m_ld_v2.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "sdcard",
            # Video,
            "framebuffer",
            "video_terminal",
        })
        
# HADBadge support ---------------------------------------------------------------------------------

class HADBadge(SocBoard):
    soc_kwargs = {"l2_size" : 2048} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from litex_boards.targets import hackaday_hadbadge
        SocBoard.__init__(self, hackaday_hadbadge.BaseSoC, soc_capabilities={
            # Communication
            "serial",
        })

    def load(self, filename):
        os.system("dfu-util --alt 2 --download {} --reset".format(filename))

# OrangeCrab support -------------------------------------------------------------------------------

class OrangeCrab(SocBoard):
    soc_kwargs = {"sys_clk_freq" : int(64e6) } # Increase sys_clk_freq to 64MHz (48MHz default).
    def __init__(self):
        from litex_boards.targets import gsd_orangecrab
        SocBoard.__init__(self, gsd_orangecrab.BaseSoC, soc_capabilities={
            # Communication
            "usb_acm",
            # Buses
            "i2c",
            # Storage
            "sdcard",
        })

# Butterstick support ------------------------------------------------------------------------------

class ButterStick(SocBoard):
    soc_kwargs = {"uart_name": "jtag_uart"}
    def __init__(self):
        from litex_boards.targets import gsd_butterstick
        SocBoard.__init__(self, gsd_butterstick.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "ethernet",
        })

# Cam Link 4K support ------------------------------------------------------------------------------

class CamLink4K(SocBoard):
    def __init__(self):
        from litex_boards.targets import camlink_4k
        SocBoard.__init__(self, camlink_4k.BaseSoC, soc_capabilities={
            # Communication
            "serial",
        })

    def load(self, filename):
        os.system("camlink configure {}".format(filename))

# TrellisSocBoard support -----------------------------------------------------------------------------

class TrellisSocBoard(SocBoard):
    def __init__(self):
        from litex_boards.targets import trellisboard
        SocBoard.__init__(self, trellisboard.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "sdcard",
        })

# ECPIX5 support -----------------------------------------------------------------------------------

class ECPIX5(SocBoard):
    def __init__(self):
        from litex_boards.targets import lambdaconcept_ecpix5
        SocBoard.__init__(self, lambdaconcept_ecpix5.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "ethernet",
            # Storage
            "sdcard",
        })

# Colorlight i5 support ----------------------------------------------------------------------------

class Colorlight_i5(SocBoard):
    soc_kwargs = {"l2_size" : 2048} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from litex_boards.targets import colorlight_i5
        SocBoard.__init__(self, colorlight_i5.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "ethernet",
        })

# Icesugar Pro support -----------------------------------------------------------------------------

class IcesugarPro(SocBoard):
    soc_kwargs = {"l2_size" : 2048} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from litex_boards.targets import muselab_icesugar_pro
        SocBoard.__init__(self, muselab_icesugar_pro.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "spiflash",
            "sdcard",
        })

# Schoko support -----------------------------------------------------------------------------------

class Schoko(SocBoard):
    soc_kwargs = {"l2_size" : 8192}
    def __init__(self):
        from litex_boards.targets import machdyne_schoko
        SocBoard.__init__(self, machdyne_schoko.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "usb_host",
            # Storage
            "spiflash",
            #"sdcard",
            "spisdcard",
            # Video,
            "framebuffer",
        })

# Konfekt support -----------------------------------------------------------------------------------

class Konfekt(SocBoard):
    soc_kwargs = {"l2_size" : 0}
    def __init__(self):
        from litex_boards.targets import machdyne_konfekt
        SocBoard.__init__(self, machdyne_konfekt.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "usb_host",
            # Storage
            #"spiflash",
            "spisdcard",
            #"sdcard",
            # Video,
            "framebuffer",
        })

# Noir support -----------------------------------------------------------------------------------

class Noir(SocBoard):
    soc_kwargs = {"l2_size" : 8192}
    def __init__(self):
        from litex_boards.targets import machdyne_noir
        SocBoard.__init__(self, machdyne_noir.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "usb_host",
            # Storage
            "spiflash",
            "spisdcard",
            #"sdcard",
            # Video,
            "framebuffer",
        })

#---------------------------------------------------------------------------------------------------
# Intel SocBoards
#---------------------------------------------------------------------------------------------------

# De10Nano support ---------------------------------------------------------------------------------

class De10Nano(SocBoard):
    soc_kwargs = {
        "with_mister_sdram" : True, # Add MiSTer SDRAM extension.
        "l2_size"           : 2048, # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000, # Power of 2 so Quartus infers it properly.
    }
    def __init__(self):
        from litex_boards.targets import terasic_de10nano
        SocBoard.__init__(self, terasic_de10nano.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "sdcard",
            # GPIOs
            "leds",
            "switches",
        })

# De0Nano support ----------------------------------------------------------------------------------

class De0Nano(SocBoard):
    soc_kwargs = {
        "l2_size" : 2048, # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000, # Power of 2 so Quartus infers it properly.
    }
    def __init__(self):
        from litex_boards.targets import terasic_de0nano
        SocBoard.__init__(self, terasic_de0nano.BaseSoC, soc_capabilities={
            # Communication
            "serial",
        })

# De1-SoC support ----------------------------------------------------------------------------------

class De1SoC(SocBoard):
    soc_kwargs = {
        "l2_size" : 2048, # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000, # Power of 2 so Quartus infers it properly.
    }
    def __init__(self):
        from litex_boards.targets import terasic_de1soc
        SocBoard.__init__(self, terasic_de1soc.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # GPIOs
            "leds",
            "switches",
        })

# QMTECH EP4CE15 support ---------------------------------------------------------------------------

class Qmtech_EP4CE15(SocBoard):
    soc_kwargs = {
        "variant" : "ep4ce15",
        "l2_size" : 2048, # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000, # Power of 2 so Quartus infers it properly.
    }
    def __init__(self):
        from litex_boards.targets import qmtech_ep4cex5
        SocBoard.__init__(self, qmtech_ep4cex5.BaseSoC, soc_capabilities={
            # Communication
            "serial",
        })

# ... and its bigger brother 

class Qmtech_EP4CE55(SocBoard):
    soc_kwargs = {
        "variant" : "ep4ce55",
        "l2_size" :  2048, # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000, # Power of 2 so Quartus infers it properly.
    }
    def __init__(self):
        from litex_boards.targets import qmtech_ep4cex5
        SocBoard.__init__(self, qmtech_ep4cex5.BaseSoC, soc_capabilities={
            # Communication
            "serial",
        })


# QMTECH 5CEFA2 support
# It is possible to build the SoC --cpu-count=2 for this chip
class Qmtech_5CEFA2(SocBoard):
    soc_kwargs = {
        "variant" : "5cefa2",
        "l2_size" :  2048, # Use Wishbone and L2 for memory accesses.
        "integrated_sram_size": 0x1000, # Power of 2 so Quartus infers it properly.
    }
    def __init__(self):
        from litex_boards.targets import qmtech_5cefa2
        SocBoard.__init__(self, qmtech_5cefa2.BaseSoC, soc_capabilities={
            # Communication
            "serial",
        })

#---------------------------------------------------------------------------------------------------
# Efinix SocBoards
#---------------------------------------------------------------------------------------------------

class TrionT120BGA576DevKit(SocBoard):
    soc_kwargs = {"l2_size" : 2048} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from litex_boards.targets import efinix_trion_t120_bga576_dev_kit
        SocBoard.__init__(self, efinix_trion_t120_bga576_dev_kit.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # GPIOs
             "leds",
        })

class TitaniumTi60F225DevKit(SocBoard):
    soc_kwargs = {
        "with_hyperram" : True,
        "sys_clk_freq"  : 300e6,
    }
    def __init__(self):
        from litex_boards.targets import efinix_titanium_ti60_f225_dev_kit
        SocBoard.__init__(self, efinix_titanium_ti60_f225_dev_kit.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            # Storage
            "sdcard",
            # GPIOs
            "leds",
        })

#---------------------------------------------------------------------------------------------------
# Gowin SocBoards
#---------------------------------------------------------------------------------------------------

# Sipeed Tang Nano 20K support ---------------------------------------------------------------------

class Sipeed_tang_nano_20k(SocBoard):
    soc_kwargs = {"l2_size" : 2048} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from litex_boards.targets import sipeed_tang_nano_20k
        SocBoard.__init__(self, sipeed_tang_nano_20k.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "sdcard",
        })

# Sipeed Tang Primer 20K support -------------------------------------------------------------------

class Sipeed_tang_primer_20k(SocBoard):
    soc_kwargs = {"l2_size" : 512} # Use Wishbone and L2 for memory accesses.
    def __init__(self):
        from litex_boards.targets import sipeed_tang_primer_20k
        SocBoard.__init__(self, sipeed_tang_primer_20k.BaseSoC, soc_capabilities={
            # Communication
            "serial",
            "spisdcard",
        })
