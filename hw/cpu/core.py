# This file is part of LiteX.
#
# Copyright (c) 2020-2022 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020-2022 Dolu1990 <charles.papon.90@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import subprocess
import re
import hashlib
from types import SimpleNamespace

from litex import get_data_mod
from migen import *
from litex.gen import *

from litex.soc.cores.cpu.naxriscv import NaxRiscv

from litex.soc.cores.cpu.vexiiriscv import VexiiRiscv

from litex.soc.interconnect import axi
from litex.soc.interconnect.csr import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.cores.cpu import CPU, CPU_GCC_TRIPLE_RISCV32, CPU_GCC_TRIPLE_RISCV64

CPU_VARIANTS = [
    "standard",
    "cached",
    "linux",
    "debian",
    "standard_cfu",
    "cached_cfu",
    "linux_cfu",
    "debian_cfu",
    "standard_cxu",
    "cached_cxu",
    "linux_cxu",
    "debian_cxu",
]


class VexiiRiscvCustom(VexiiRiscv):
    variants = CPU_VARIANTS

    @staticmethod
    def args_read(args):
        print(args)

        vdir = os.path.join(os.path.dirname(__file__), "verilog")
        ndir = os.path.join(vdir, "ext", "VexiiRiscv")

        NaxRiscv.git_setup(
            "VexiiRiscv",
            ndir,
            "https://github.com/pmozil/VexiiRiscv.git",
            "dev",
            "",
            # args.update_repo,
            "False",
        )

        if not args.cpu_variant:
            args.cpu_variant = "linux"

        if not args.io_map is None:
            VexiiRiscv.io_regions = {int(args.io_map[0], 0): int(args.io_map[1], 0)}
        VexiiRiscv.internal_mem_map.update({devinfo[0]: int(devinfo[1], 0) for devinfo in args.mem_map})

        VexiiRiscv.isa_map.update(args.isa)
        VexiiRiscv.isa_map.update(["m", "zihpm", "zicntr"])
        VexiiRiscv.vexii_args += " --with-mul --with-div --allow-bypass-from=0"
        VexiiRiscv.vexii_args += " --fetch-l1 --fetch-l1-ways=2"
        VexiiRiscv.vexii_args += " --lsu-l1 --lsu-l1-ways=2  --with-lsu-bypass"
        VexiiRiscv.vexii_args += " --relaxed-branch"

        if args.cpu_variant in [
            "linux",
            "debian",
            "linux_cfu",
            "debian_cfu",
            "linux_cxu",
            "debian_cxu",
        ]:
            VexiiRiscv.with_opensbi = True
            VexiiRiscv.with_supervisor = True
            VexiiRiscv.isa_map.update(["a", "s", "u"])
            VexiiRiscv.vexii_args += " --fetch-l1-ways=4 --fetch-l1-mem-data-width-min=64"
            VexiiRiscv.vexii_args += " --lsu-l1-ways=4 --lsu-l1-mem-data-width-min=64"

        if args.cpu_variant in ["debian", "debin_cfu"]:
            VexiiRiscv.isa_map.update(["c", "f", "d"])
            VexiiRiscv.vexii_args += " --xlen=64 --fma-reduced-accuracy --fpu-ignore-subnormal"

        if args.cpu_variant in [
            "linux",
            "debian",
            "linux_cfu",
            "debian_cfu",
            "linux_cxu",
            "debian_cxu",
        ]:
            VexiiRiscv.vexii_args += " --with-btb --with-ras --with-gshare"

        if args.with_aia or args.imsic_interrupt_number > 0:
            VexiiRiscv.isa_map.add("smaia")
            if "s" in VexiiRiscv.isa_map:
                VexiiRiscv.isa_map.add("ssaia")

        VexiiRiscv.vexii_args += " --with-isa=" + ",".join(VexiiRiscv.isa_map)

        if args.cfu:
            VexiiRiscv.vexii_args += " --with-cfu"
            args.cpu_variant += "_cfu"
            args.cpu_cfu = args.cfu

        VexiiRiscv.vexii_args += f" --cxu-num {len(args.cxu)}"

        if len(args.cxu) > 0:
            args.cpu_variant += "_cxu"

        VexiiRiscv.soc_args = SimpleNamespace(**{k:getattr(args,k) for k in VexiiRiscv.soc_keys})
        VexiiRiscv.no_netlist_cache = args.no_netlist_cache
        VexiiRiscv.vexii_args      += " " + args.vexii_args
        VexiiRiscv.update_repo      = args.update_repo

        md5_hash = hashlib.md5()
        md5_hash.update(VexiiRiscv.vexii_args.encode('utf-8'))
        vexii_args_hash = md5_hash.hexdigest()
        ppath = os.path.join(vdir, str(vexii_args_hash) + ".py")
        if VexiiRiscv.no_netlist_cache or not os.path.exists(ppath):
            cmd = f"""cd {ndir} && sbt "runMain vexiiriscv.soc.litex.PythonArgsGen {VexiiRiscv.vexii_args} --python-file={str(ppath)}\""""
            subprocess.check_call(cmd, shell=True)
        # Loads variables like VexiiRiscv.with_rvm, that set the RISC-V extensions.
        from litex.gen import Open

        with open(ppath) as file:
            exec(file.read())

        VexiiRiscv.gcc_triple = CPU_GCC_TRIPLE_RISCV32 if VexiiRiscv.xlen==32 else CPU_GCC_TRIPLE_RISCV64
        VexiiRiscv.linker_output_format = f"elf{VexiiRiscv.xlen}-littleriscv"


    def __init__(self, platform, variant):
        self.platform         = platform
        self.reset            = Signal()
        self.interrupt        = Signal(32)
        self.pbus             = pbus = axi.AXILiteInterface(address_width=32, data_width=32)

        self.periph_buses     = [pbus] # Peripheral buses (Connected to main SoC's bus).
        self.memory_buses     = []           # Memory buses (Connected directly to LiteDRAM).

        # # #

        self.tracer_valid = Signal()
        self.tracer_payload = Signal(8)

        # CPU Instance.
        self.cpu_params = dict(
            # Clk/Rst.
            i_litex_clk   = ClockSignal("sys"),
            i_litex_reset = ResetSignal("sys") | self.reset,

            o_debug=self.tracer_payload,

            # Patcher/Tracer.
            # o_patcher_tracer_valid   = self.tracer_valid,
            # o_patcher_tracer_payload = self.tracer_payload,

            # Interrupt.
            i_peripheral_externalInterrupts_port = self.interrupt,

            # Peripheral Memory Bus (AXI Lite Slave).
            o_pBus_awvalid = pbus.aw.valid,
            i_pBus_awready = pbus.aw.ready,
            o_pBus_awaddr  = pbus.aw.addr,
            o_pBus_awprot  = Open(),
            o_pBus_wvalid  = pbus.w.valid,
            i_pBus_wready  = pbus.w.ready,
            o_pBus_wdata   = pbus.w.data,
            o_pBus_wstrb   = pbus.w.strb,
            i_pBus_bvalid  = pbus.b.valid,
            o_pBus_bready  = pbus.b.ready,
            i_pBus_bresp   = pbus.b.resp,
            o_pBus_arvalid = pbus.ar.valid,
            i_pBus_arready = pbus.ar.ready,
            o_pBus_araddr  = pbus.ar.addr,
            o_pBus_arprot  = Open(),
            i_pBus_rvalid  = pbus.r.valid,
            o_pBus_rready  = pbus.r.ready,
            i_pBus_rdata   = pbus.r.data,
            i_pBus_rresp   = pbus.r.resp,
        )

        if VexiiRiscv.soc_args.with_cpu_clk:
            self.cpu_clk = Signal()
            self.cpu_params.update(
                i_cpu_clk = self.cpu_clk
            )

        if VexiiRiscv.soc_args.with_dma:
            self.dma_bus = dma_bus = axi.AXIInterface(data_width=VexiiRiscv.internal_bus_width, address_width=32, id_width=4)

            self.cpu_params.update(
                # DMA Bus.
                # --------
                # AW Channel.
                o_dma_bus_awready = dma_bus.aw.ready,
                i_dma_bus_awvalid = dma_bus.aw.valid,
                i_dma_bus_awid    = dma_bus.aw.id,
                i_dma_bus_awaddr  = dma_bus.aw.addr,
                i_dma_bus_awlen   = dma_bus.aw.len,
                i_dma_bus_awsize  = dma_bus.aw.size,
                i_dma_bus_awburst = dma_bus.aw.burst,
                i_dma_bus_awlock  = dma_bus.aw.lock,
                i_dma_bus_awcache = dma_bus.aw.cache,
                i_dma_bus_awprot  = dma_bus.aw.prot,
                i_dma_bus_awqos   = dma_bus.aw.qos,

                # W Channel.
                o_dma_bus_wready  = dma_bus.w.ready,
                i_dma_bus_wvalid  = dma_bus.w.valid,
                i_dma_bus_wdata   = dma_bus.w.data,
                i_dma_bus_wstrb   = dma_bus.w.strb,
                i_dma_bus_wlast   = dma_bus.w.last,

                # B Channel.
                i_dma_bus_bready  = dma_bus.b.ready,
                o_dma_bus_bvalid  = dma_bus.b.valid,
                o_dma_bus_bid     = dma_bus.b.id,
                o_dma_bus_bresp   = dma_bus.b.resp,

                # AR Channel.
                o_dma_bus_arready = dma_bus.ar.ready,
                i_dma_bus_arvalid = dma_bus.ar.valid,
                i_dma_bus_arid    = dma_bus.ar.id,
                i_dma_bus_araddr  = dma_bus.ar.addr,
                i_dma_bus_arlen   = dma_bus.ar.len,
                i_dma_bus_arsize  = dma_bus.ar.size,
                i_dma_bus_arburst = dma_bus.ar.burst,
                i_dma_bus_arlock  = dma_bus.ar.lock,
                i_dma_bus_arcache = dma_bus.ar.cache,
                i_dma_bus_arprot  = dma_bus.ar.prot,
                i_dma_bus_arqos   = dma_bus.ar.qos,

                # R Channel.
                i_dma_bus_rready  = dma_bus.r.ready,
                o_dma_bus_rvalid  = dma_bus.r.valid,
                o_dma_bus_rid     = dma_bus.r.id,
                o_dma_bus_rdata   = dma_bus.r.data,
                o_dma_bus_rresp   = dma_bus.r.resp,
                o_dma_bus_rlast   = dma_bus.r.last,
            )

        def add_io(direction, prefix, name, width, socgen_name=None):
            # direction: "i" or "o"
            # prefix: instance name (e.g. "mac0", "video0")
            # name: python/signal suffix (e.g. "tx_d", "hsync", "color_en")
            # socgen_name: optional override for the CPU param name (e.g. "hSync", "colorEn")
            composed = f"{prefix}_{name}"
            sig = Signal(width, name=composed)
            setattr(self, composed, sig)
            if socgen_name is None:
                socgen_name = name
            self.cpu_params[f"{direction}_{prefix}_{socgen_name}"] = sig
            return sig

        for video in VexiiRiscv.soc_args.video:
            args = {}
            for i, val in enumerate(video.split(",")):
                name, value = val.split("=")
                args.update({name: value})
            name = args["name"]
            add_io("o", name, "clk",      1, socgen_name="clk")
            add_io("o", name, "hsync",    1, socgen_name="hSync")
            add_io("o", name, "vsync",    1, socgen_name="vSync")
            add_io("o", name, "color_en", 1, socgen_name="colorEn")
            add_io("o", name, "color",   16, socgen_name="color")

        for macsg in VexiiRiscv.soc_args.mac_sg:
            args = {}
            for i, val in enumerate(macsg.split(",")):
                name, value = val.split("=")
                args.update({name: value})
            name = args["name"]
            add_io("i", name, "tx_ref_clk", 1)
            add_io("o", name, "tx_ctl", 2)
            add_io("o", name, "tx_d", 8)
            add_io("o", name, "tx_clk", 2)

            add_io("i", name, "rx_ctl", 2)
            add_io("i", name, "rx_d", 8)
            add_io("i", name, "rx_clk", 1)

    def set_reset_address(self, reset_address):
        VexiiRiscv.reset_address = reset_address
        VexiiRiscv.vexii_args += f" --reset-vector {reset_address}"

    # Cluster Name Generation.
    @staticmethod
    def generate_netlist_name():
        md5_hash = hashlib.md5()
        for k,v in vars(VexiiRiscv.soc_args).items():
            md5_hash.update(str(v).encode('utf-8'))
        md5_hash.update(str(VexiiRiscv.reset_address).encode('utf-8'))
        md5_hash.update(str(VexiiRiscv.litedram_width).encode('utf-8'))
        md5_hash.update(str(VexiiRiscv.xlen).encode('utf-8'))
        md5_hash.update(str(VexiiRiscv.memory_regions).encode('utf-8'))
        md5_hash.update(str(VexiiRiscv.vexii_args).encode('utf-8'))
        md5_hash.update(str(VexiiRiscv.with_opensbi).encode('utf-8'))
        md5_hash.update(str(VexiiRiscv.with_supervisor).encode('utf-8'))

        # md5_hash.update(str(VexiiRiscv.internal_bus_width).encode('utf-8'))


        digest = md5_hash.hexdigest()
        VexiiRiscv.netlist_name = "VexiiRiscvLitex_" + digest

    # Netlist Generation.
    @staticmethod
    def generate_netlist():
        vdir = os.path.join(os.path.dirname(__file__), "verilog")
        ndir = os.path.join(vdir, "ext", "VexiiRiscv")
        sdir = os.path.join(vdir, "ext", "SpinalHDL")

        gen_args = []
        gen_args.append(f"--netlist-name={VexiiRiscv.netlist_name}")
        gen_args.append(f"--netlist-directory={vdir}")
        gen_args.append(VexiiRiscv.vexii_args)
        if VexiiRiscv.litedram_width:
            gen_args.append(f"--litedram-width={VexiiRiscv.litedram_width}")
        # gen_args.append(f"--internal_bus_width={VexiiRiscv.internal_bus_width}")
        for region in VexiiRiscv.memory_regions:
            gen_args.append(f"--memory-region={region[0]},{region[1]},{region[2]},{region[3]}")
        for device, address in VexiiRiscv.internal_mem_map.items():
            gen_args.append(" --device-region:{}={}".format(device, address))
        for k,v in vars(VexiiRiscv.soc_args).items():
            if isinstance(v, bool):
                if v:
                    gen_args.append(f"--{k.replace('_','-')}")
            elif isinstance(v, int) or isinstance(v, str):
                gen_args.append(f"--{k.replace('_', '-')}={v}")
            elif isinstance(v, list):
                for arg_value in v:
                    gen_args.append(f"--{k.replace('_', '-')} {arg_value}")
            elif v == None:
                pass
            else:
                raise Exception(f"unimplemented: {type(v)}")

        cmd = f"""cd {ndir} && sbt "runMain vexiiriscv.soc.litex.SocGen {" ".join(gen_args)}\""""
        print("VexiiRiscv generation command :")
        print(cmd)
        subprocess.check_call(cmd, shell=True)

    def add_sources(self, platform):
        vdir = os.path.join(os.path.dirname(__file__), "verilog")
        print(f"VexiiRiscv netlist : {self.netlist_name}")

        if VexiiRiscv.no_netlist_cache or not os.path.exists(
            os.path.join(vdir, self.netlist_name + ".v")
        ):
            self.generate_netlist()

        # Add RAM.
        # By default, use Generic RAM implementation.
        ram_filename = "Ram_1w_1rs_Generic.v"
        lutram_filename = "Ram_1w_1ra_Generic.v"
        # On Altera/Intel platforms, use specific implementation.
        from litex.build.altera import AlteraPlatform

        if isinstance(platform, AlteraPlatform):
            ram_filename = "Ram_1w_1rs_Intel.v"
        # On Efinix platforms, use specific implementation.
        from litex.build.efinix import EfinixPlatform

        if isinstance(platform, EfinixPlatform):
            ram_filename = "Ram_1w_1rs_Efinix.v"
        platform.add_source(os.path.join(vdir, ram_filename), "verilog")
        platform.add_source(os.path.join(vdir, lutram_filename), "verilog")

        # Add Cluster.
        platform.add_source(os.path.join(vdir, self.netlist_name + ".v"), "verilog")

    def add_cfu(self, cfu_filename):
        # Check CFU presence.
        if not os.path.exists(cfu_filename):
            raise OSError(f"Unable to find VexRiscv CFU plugin {cfu_filename}.")

        # CFU:CPU Bus Layout.
        cfu_bus_layout = [
            (
                "cmd",
                [
                    ("valid", 1),
                    ("ready", 1),
                    (
                        "payload",
                        [
                            ("function_id", 10),
                            ("inputs_0", 32),
                            ("inputs_1", 32),
                        ],
                    ),
                ],
            ),
            (
                "rsp",
                [
                    ("valid", 1),
                    ("ready", 1),
                    (
                        "payload",
                        [
                            ("outputs_0", 32),
                        ],
                    ),
                ],
            ),
        ]

        # The CFU:CPU Bus.
        self.cfu_bus = cfu_bus = Record(cfu_bus_layout)

        # Connect CFU to the CFU:CPU bus.
        self.cfu_params = dict(
            i_cmd_valid=cfu_bus.cmd.valid,
            o_cmd_ready=cfu_bus.cmd.ready,
            i_cmd_payload_function_id=cfu_bus.cmd.payload.function_id,
            i_cmd_payload_inputs_0=cfu_bus.cmd.payload.inputs_0,
            i_cmd_payload_inputs_1=cfu_bus.cmd.payload.inputs_1,
            o_rsp_valid=cfu_bus.rsp.valid,
            i_rsp_ready=cfu_bus.rsp.ready,
            o_rsp_payload_outputs_0=cfu_bus.rsp.payload.outputs_0,
            i_clk=ClockSignal("sys"),
            i_reset=ResetSignal("sys") | self.reset,
        )
        self.platform.add_source(cfu_filename)

        # Connect CPU to the CFU:CPU bus.
        self.cpu_params.update(
            o_vexiis_0_cfuBus_node_cmd_valid=cfu_bus.cmd.valid,
            i_vexiis_0_cfuBus_node_cmd_ready=cfu_bus.cmd.ready,
            o_vexiis_0_cfuBus_node_cmd_payload_function_id=cfu_bus.cmd.payload.function_id,
            o_vexiis_0_cfuBus_node_cmd_payload_inputs_0=cfu_bus.cmd.payload.inputs_0,
            o_vexiis_0_cfuBus_node_cmd_payload_inputs_1=cfu_bus.cmd.payload.inputs_1,
            i_vexiis_0_cfuBus_node_rsp_valid=cfu_bus.rsp.valid,
            o_vexiis_0_cfuBus_node_rsp_ready=cfu_bus.rsp.ready,
            i_vexiis_0_cfuBus_node_rsp_payload_outputs_0=cfu_bus.rsp.payload.outputs_0,
        )

    def add_cxus(self, cxus: list[str]):
        if not hasattr(self, "cxu_params"):
            self.cxu_params = []

        for i, cxu_filename in enumerate(cxus):
            if not os.path.exists(cxu_filename):
                raise OSError(f"Unable to find VexRiscv CXU plugin {cxu_filename}.")
            CXU_INPUT_DATA_W = 32
            CXU_STATE_W = 64
            CXU_STATE_ADDR_W = (CXU_STATE_W - 1).bit_length()

            cxu_bus_layout = [
                (
                    "cmd",
                    [
                        ("valid", 1),
                        ("ready", 1),
                        (
                            "payload",
                            [
                                ("function_id", 3),
                                ("inputs_0", 32),
                                ("inputs_1", 32),
                                ("state_id", CXU_STATE_ADDR_W),
                                ("cxu_id", 4),
                                ("ready", 1),
                            ],
                        ),
                    ],
                ),
                (
                    "rsp",
                    [
                        ("valid", 1),
                        ("ready", 1),
                        (
                            "payload",
                            [
                                ("outputs_0", 32),
                                ("ready", 1),
                            ],
                        ),
                    ],
                ),
                (
                    "state",
                    [
                        # READ PORT
                        ("read_addr", CXU_STATE_ADDR_W),
                        ("read_data", CXU_INPUT_DATA_W),
                        # WRITE PORT
                        ("write_addr", CXU_STATE_ADDR_W),
                        ("write_data", CXU_INPUT_DATA_W),
                        ("write_en", 1),
                    ],
                ),
            ]

            cxu_bus = Record(cxu_bus_layout)
            setattr(self, f"cxu_bus_{i}", cxu_bus)

            self.cxu_params.append(
                {
                    # CMD
                    f"i_cmd_valid": cxu_bus.cmd.valid,
                    f"o_cmd_ready": cxu_bus.cmd.ready,
                    f"i_cmd_payload_function_id": cxu_bus.cmd.payload.function_id,
                    f"i_cmd_payload_inputs_0": cxu_bus.cmd.payload.inputs_0,
                    f"i_cmd_payload_inputs_1": cxu_bus.cmd.payload.inputs_1,
                    f"i_cmd_payload_state_id": cxu_bus.cmd.payload.state_id,
                    f"i_cmd_payload_cxu_id": cxu_bus.cmd.payload.cxu_id,
                    f"i_cmd_payload_ready": cxu_bus.cmd.payload.ready,
                    # RSP
                    f"o_rsp_valid": cxu_bus.rsp.valid,
                    f"i_rsp_ready": cxu_bus.rsp.ready,
                    f"o_rsp_payload_outputs_0": cxu_bus.rsp.payload.outputs_0,
                    f"o_rsp_payload_ready": cxu_bus.rsp.payload.ready,
                    # STATE (BRAM-style)
                    f"o_state_read_addr": cxu_bus.state.read_addr,
                    f"i_state_read_data": cxu_bus.state.read_data,
                    f"o_state_write_addr": cxu_bus.state.write_addr,
                    f"o_state_write_data": cxu_bus.state.write_data,
                    f"o_state_write_en": cxu_bus.state.write_en,
                    # Clock / Reset
                    f"i_clk": ClockSignal("sys"),
                    f"i_reset": ResetSignal("sys") | self.reset,
                }
            )

            self.platform.add_source(cxu_filename)

            self.cpu_params.update(
                {
                    # CMD
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_valid": cxu_bus.cmd.valid,
                    f"i_vexiis_0_cxuBus_buses_{i}_node_cmd_ready": cxu_bus.cmd.ready,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_function_id": cxu_bus.cmd.payload.function_id,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_inputs_0": cxu_bus.cmd.payload.inputs_0,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_inputs_1": cxu_bus.cmd.payload.inputs_1,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_state_id": cxu_bus.cmd.payload.state_id,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_cxu_id": cxu_bus.cmd.payload.cxu_id,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_ready": cxu_bus.cmd.payload.ready,
                    # RSP
                    f"i_vexiis_0_cxuBus_buses_{i}_node_rsp_valid": cxu_bus.rsp.valid,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_rsp_ready": cxu_bus.rsp.ready,
                    f"i_vexiis_0_cxuBus_buses_{i}_node_rsp_payload_outputs_0": cxu_bus.rsp.payload.outputs_0,
                    f"i_vexiis_0_cxuBus_buses_{i}_node_rsp_payload_ready": cxu_bus.rsp.payload.ready,
                    # STATE (BRAM interface)
                    f"i_vexiis_0_cxuBus_buses_{i}_cxu_state_read_addr": cxu_bus.state.read_addr,
                    f"o_vexiis_0_cxuBus_buses_{i}_cxu_state_read_data": cxu_bus.state.read_data,
                    f"i_vexiis_0_cxuBus_buses_{i}_cxu_state_write_addr": cxu_bus.state.write_addr,
                    f"i_vexiis_0_cxuBus_buses_{i}_cxu_state_write_data": cxu_bus.state.write_data,
                    f"i_vexiis_0_cxuBus_buses_{i}_cxu_state_write_en": cxu_bus.state.write_en,
                }
            )

    def do_finalize(self):
        assert hasattr(self, "reset_address")

        # Generate memory map from CPU perspective
        # vexiiriscv modes:
        # r,w,x,c  : readable, writeable, executable, caching allowed
        # io       : IO region (Implies P bus, preserve memory order, no dcache)
        # vexiiriscv bus:
        # p        : peripheral
        # m        : memory
        VexiiRiscv.memory_regions = []
        # for name, region in self.soc_bus.io_regions.items():
        #     VexiiRiscv.memory_regions.append( (region.origin, region.size, "io", "p") ) # IO is only allowed on the p bus
        for name, region in self.soc_bus.regions.items():
            if region.linker:  # Remove virtual regions.
                continue
            if len(self.memory_buses) and name == "main_ram":  # m bus
                bus = "m"
            else:
                bus = "p"
            mode = region.mode
            mode += "c" if region.cached else ""
            VexiiRiscv.memory_regions.append((region.origin, region.size, mode, bus))

        from litex.build.efinix import EfinixPlatform

        if isinstance(self.platform, EfinixPlatform):
            VexiiRiscv.vexii_args = "--mmu-sync-read " + VexiiRiscv.vexii_args

        self.generate_netlist_name()

        # Do verilog instance.
        self.specials += Instance(self.netlist_name, **self.cpu_params)

        # Add verilog sources.
        self.add_sources(self.platform)
        if hasattr(self, "cfu_params"):
            self.specials += Instance("Cfu", **self.cfu_params)
        # TODO: Add cxu instances
        if hasattr(self, "cxu_params"):
            for i, param in enumerate(self.cxu_params):
                print(param)
                self.specials += Instance(f"Cxu{i}", **param)
