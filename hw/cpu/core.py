#
# This file is part of LiteX.
#
# Copyright (c) 2020-2022 Florent Kermarrec <florent@enjoy-digital.fr>
# Copyright (c) 2020-2022 Dolu1990 <charles.papon.90@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os
import subprocess
import re
import hashlib

from migen import *

from litex.soc.cores.cpu.naxriscv import NaxRiscv

from litex.soc.cores.cpu.vexiiriscv import VexiiRiscv

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

        VexiiRiscv.vexii_args += (
            " --with-mul --with-div --allow-bypass-from=0 --performance-counters=0"
        )
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
            VexiiRiscv.vexii_args += " --with-rva --with-supervisor"
            VexiiRiscv.vexii_args += (
                " --fetch-l1-ways=4 --fetch-l1-mem-data-width-min=64"
            )
            VexiiRiscv.vexii_args += " --lsu-l1-ways=4 --lsu-l1-mem-data-width-min=64"

        if args.cpu_variant in ["debian", "debin_cfu"]:
            VexiiRiscv.vexii_args += " --xlen=64 --with-rvc --with-rvf --with-rvd --fma-reduced-accuracy --fpu-ignore-subnormal"

        if args.cpu_variant in [
            "linux",
            "debian",
            "linux_cfu",
            "debian_cfu",
            "linux_cxu",
            "debian_cxu",
        ]:
            VexiiRiscv.vexii_args += " --with-btb --with-ras --with-gshare"

        if args.cfu:
            VexiiRiscv.vexii_args += " --with-cfu"
            args.cpu_variant += "_cfu"
            args.cpu_cfu = args.cfu

        VexiiRiscv.vexii_args += f" --cxu-num {len(args.cxu)}"

        if len(args.cxu) > 0:
            args.cpu_variant += "_cxu"

        VexiiRiscv.jtag_tap = args.with_jtag_tap
        VexiiRiscv.jtag_instruction = args.with_jtag_instruction
        VexiiRiscv.with_dma = args.with_coherent_dma
        VexiiRiscv.with_axi3 = args.with_axi3
        VexiiRiscv.update_repo = args.update_repo
        VexiiRiscv.no_netlist_cache = args.no_netlist_cache
        VexiiRiscv.vexii_args += " " + args.vexii_args

        md5_hash = hashlib.md5()
        md5_hash.update(VexiiRiscv.vexii_args.encode("utf-8"))
        vexii_args_hash = md5_hash.hexdigest()
        ppath = os.path.join(vdir, str(vexii_args_hash) + ".py")
        if VexiiRiscv.no_netlist_cache or not os.path.exists(ppath):
            cmd = f"""cd {ndir} && sbt "runMain vexiiriscv.soc.litex.PythonArgsGen {VexiiRiscv.vexii_args} --python-file={str(ppath)}\""""
            subprocess.check_call(cmd, shell=True)
        with open(ppath) as file:
            exec(file.read())

        if VexiiRiscv.xlen == 64:
            VexiiRiscv.gcc_triple = CPU_GCC_TRIPLE_RISCV64
        VexiiRiscv.linker_output_format = f"elf{VexiiRiscv.xlen}-littleriscv"
        if args.cpu_count:
            VexiiRiscv.cpu_count = args.cpu_count
        if args.l2_bytes:
            VexiiRiscv.l2_bytes = args.l2_bytes
        VexiiRiscv.with_cpu_clk = args.with_cpu_clk
        if args.l2_ways:
            VexiiRiscv.l2_ways = args.l2_ways
        if args.l2_self_flush:
            VexiiRiscv.l2_self_flush = args.l2_self_flush
        VexiiRiscv.vexii_video = args.vexii_video
        VexiiRiscv.vexii_macsg = args.vexii_macsg

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
        gen_args.append(f"--cpu-count={VexiiRiscv.cpu_count}")
        gen_args.append(f"--l2-bytes={VexiiRiscv.l2_bytes}")
        if VexiiRiscv.with_cpu_clk:
            gen_args.append("--with-cpu-clk")
        gen_args.append(f"--l2-ways={VexiiRiscv.l2_ways}")
        if VexiiRiscv.l2_self_flush:
            gen_args.append(f"--l2-self-flush={VexiiRiscv.l2_self_flush}")
        gen_args.append(f"--litedram-width={VexiiRiscv.litedram_width}")
        # gen_args.append(f"--internal_bus_width={VexiiRiscv.internal_bus_width}")
        for region in VexiiRiscv.memory_regions:
            gen_args.append(
                f"--memory-region={region[0]},{region[1]},{region[2]},{region[3]}"
            )
        if VexiiRiscv.jtag_tap:
            gen_args.append(f"--with-jtag-tap")
        if VexiiRiscv.jtag_instruction:
            gen_args.append(f"--with-jtag-instruction")
        if VexiiRiscv.with_dma:
            gen_args.append(f"--with-dma")
        if VexiiRiscv.with_axi3:
            gen_args.append(f"--with-axi3")
        for arg in VexiiRiscv.vexii_video:
            gen_args.append(f"--video {arg}")
        for arg in VexiiRiscv.vexii_macsg:
            gen_args.append(f"--mac-sg {arg}")

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
        # Initialize cxu_params if it doesn't exist
        if not hasattr(self, "cxu_params"):
            self.cxu_params = []

        # Check CXU presence and add each CXU.
        for i, cxu_filename in enumerate(cxus):
            if not os.path.exists(cxu_filename):
                raise OSError(f"Unable to find VexRiscv CXU plugin {cxu_filename}.")

            # CXU:CPU Bus Layout (matching the Verilog interface in comments)
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
                                ("state_id", 3),
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
            ]

            # The CXU:CPU Bus.
            cxu_bus = Record(cxu_bus_layout)
            setattr(self, f"cxu_bus_{i}", cxu_bus)

            # Connect CXU to the CXU:CPU bus - UPDATE (not overwrite) cxu_params
            self.cxu_params.append(
                {
                    f"i_cmd_valid": cxu_bus.cmd.valid,
                    f"o_cmd_ready": cxu_bus.cmd.ready,
                    f"i_cmd_payload_function_id": cxu_bus.cmd.payload.function_id,
                    f"i_cmd_payload_inputs_0": cxu_bus.cmd.payload.inputs_0,
                    f"i_cmd_payload_inputs_1": cxu_bus.cmd.payload.inputs_1,
                    f"i_cmd_payload_state_id": cxu_bus.cmd.payload.state_id,
                    f"i_cmd_payload_cxu_id": cxu_bus.cmd.payload.cxu_id,
                    f"i_cmd_payload_ready": cxu_bus.cmd.payload.ready,
                    f"o_rsp_valid": cxu_bus.rsp.valid,
                    f"i_rsp_ready": cxu_bus.rsp.ready,
                    f"o_rsp_payload_outputs_0": cxu_bus.rsp.payload.outputs_0,
                    f"o_rsp_payload_ready": cxu_bus.rsp.payload.ready,
                    f"i_clk": ClockSignal("sys"),
                    f"i_reset": ResetSignal("sys") | self.reset,
                }
            )

            self.platform.add_source(cxu_filename)

            # Connect CPU to the CXU:CPU bus.
            self.cpu_params.update(
                {
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_valid": cxu_bus.cmd.valid,
                    f"i_vexiis_0_cxuBus_buses_{i}_node_cmd_ready": cxu_bus.cmd.ready,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_function_id": cxu_bus.cmd.payload.function_id,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_inputs_0": cxu_bus.cmd.payload.inputs_0,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_inputs_1": cxu_bus.cmd.payload.inputs_1,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_state_id": cxu_bus.cmd.payload.state_id,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_cxu_id": cxu_bus.cmd.payload.cxu_id,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_cmd_payload_ready": cxu_bus.cmd.payload.ready,
                    f"i_vexiis_0_cxuBus_buses_{i}_node_rsp_valid": cxu_bus.rsp.valid,
                    f"o_vexiis_0_cxuBus_buses_{i}_node_rsp_ready": cxu_bus.rsp.ready,
                    f"i_vexiis_0_cxuBus_buses_{i}_node_rsp_payload_outputs_0": cxu_bus.rsp.payload.outputs_0,
                    f"i_vexiis_0_cxuBus_buses_{i}_node_rsp_payload_ready": cxu_bus.rsp.payload.ready,
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
