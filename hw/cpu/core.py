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

from litex.soc.cores.cpu.naxriscv import NaxRiscv

from litex.soc.cores.cpu.vexiiriscv import VexiiRiscv


class VexiiRiscvCustom(VexiiRiscv):
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

        if args.cpu_variant in ["linux", "debian"]:
            VexiiRiscv.with_opensbi = True
            VexiiRiscv.vexii_args += " --with-rva --with-supervisor"
            VexiiRiscv.vexii_args += (
                " --fetch-l1-ways=4 --fetch-l1-mem-data-width-min=64"
            )
            VexiiRiscv.vexii_args += " --lsu-l1-ways=4 --lsu-l1-mem-data-width-min=64"

        if args.cpu_variant in ["debian"]:
            VexiiRiscv.vexii_args += " --xlen=64 --with-rvc --with-rvf --with-rvd --fma-reduced-accuracy --fpu-ignore-subnormal"

        if args.cpu_variant in ["linux", "debian"]:
            VexiiRiscv.vexii_args += " --with-btb --with-ras --with-gshare"

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
