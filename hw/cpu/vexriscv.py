import os
import subprocess

from litex.soc.cores.cpu.vexriscv_smp import VexRiscvSMP


class VexRiscvSMPCustom(VexRiscvSMP):
    def __init__(self, *args, **kwargs):
        VexRiscvSMP.__init__(self, *args, **kwargs)

    def add_sources(self, platform):
        # vdir = get_data_mod("cpu", "vexriscv_smp").data_location
        vdir = os.path.join(os.path.dirname(__file__), "verilog")
        print(f"VexRiscv cluster : {self.cluster_name}")
        if not os.path.exists(os.path.join(vdir, self.cluster_name + ".v")):
            self.generate_netlist()

        # Add RAM.

        # By default, use Generic RAM implementation.
        ram_filename = "Ram_1w_1rs_Generic.v"
        # On Altera/Intel platforms, use specific implementation.
        from litex.build.altera import AlteraPlatform

        if isinstance(platform, AlteraPlatform):
            ram_filename = "Ram_1w_1rs_Intel.v"
            # define SYNTHESIS verilog name to avoid issues with unsupported
            # functions
            platform.toolchain.additional_qsf_commands.append(
                'set_global_assignment -name VERILOG_MACRO "SYNTHESIS=1"'
            )
        # On Efinix platforms, use specific implementation.
        from litex.build.efinix import EfinixPlatform

        if isinstance(platform, EfinixPlatform):
            ram_filename = "Ram_1w_1rs_Efinix.v"
        platform.add_source(os.path.join(vdir, ram_filename), "verilog")

        # Add Cluster.
        cluster_filename = os.path.join(vdir, self.cluster_name + ".v")

        def add_synthesis_define(filename):
            """Add SYNTHESIS define to verilog for toolchains requiring it, ex Gowin"""
            synthesis_define = "`define SYNTHESIS\n"
            # Read file.
            with open(filename, "r") as f:
                lines = f.readlines()
            # Modify file.
            with open(filename, "w") as f:
                if lines[0] != synthesis_define:
                    f.write(synthesis_define)
                for line in lines:
                    f.write(line)

        add_synthesis_define(cluster_filename)
        platform.add_source(cluster_filename, "verilog")

    @staticmethod
    def generate_netlist():
        print(f"Generating cluster netlist")
        # vdir = get_data_mod("cpu", "vexriscv_smp").data_location
        vdir = os.path.join(os.path.dirname(__file__), "verilog")
        gen_args = []
        if VexRiscvSMP.coherent_dma:
            gen_args.append("--coherent-dma")
        gen_args.append(f"--cpu-count={VexRiscvSMP.cpu_count}")
        # gen_args.append(f"--reset-vector={VexRiscvSMP.reset_vector}")
        gen_args.append(f"--ibus-width={VexRiscvSMP.icache_width}")
        gen_args.append(f"--dbus-width={VexRiscvSMP.dcache_width}")
        gen_args.append(f"--dcache-size={VexRiscvSMP.dcache_size}")
        gen_args.append(f"--icache-size={VexRiscvSMP.icache_size}")
        gen_args.append(f"--dcache-ways={VexRiscvSMP.dcache_ways}")
        gen_args.append(f"--icache-ways={VexRiscvSMP.icache_ways}")
        gen_args.append(f"--litedram-width={VexRiscvSMP.litedram_width}")
        gen_args.append(f"--aes-instruction={VexRiscvSMP.aes_instruction}")
        gen_args.append(f"--expose-time={VexRiscvSMP.expose_time}")
        gen_args.append(f"--out-of-order-decoder={VexRiscvSMP.out_of_order_decoder}")
        gen_args.append(f"--privileged-debug={VexRiscvSMP.privileged_debug}")
        gen_args.append(f"--hardware-breakpoints={VexRiscvSMP.hardware_breakpoints}")
        gen_args.append(f"--wishbone-memory={VexRiscvSMP.wishbone_memory}")
        if VexRiscvSMP.wishbone_force_32b:
            gen_args.append(f"--wishbone-force-32b={VexRiscvSMP.wishbone_force_32b}")
        gen_args.append(f"--fpu={VexRiscvSMP.with_fpu}")
        gen_args.append(f"--cpu-per-fpu={VexRiscvSMP.cpu_per_fpu}")
        gen_args.append(f"--rvc={VexRiscvSMP.with_rvc}")
        gen_args.append(f"--netlist-name={VexRiscvSMP.cluster_name}")
        gen_args.append(f"--netlist-directory={vdir}")
        gen_args.append(f"--dtlb-size={VexRiscvSMP.dtlb_size}")
        gen_args.append(f"--itlb-size={VexRiscvSMP.itlb_size}")
        # gen_args.append(f"--jtag-tap={VexRiscvSMP.jtag_tap}")

        cmd = 'cd {path} && sbt "runMain vexriscv.demo.smp.VexRiscvLitexSmpClusterCmdGen {args}"'.format(
            path=os.path.join(vdir, "ext", "VexRiscv"), args=" ".join(gen_args)
        )
        subprocess.check_call(cmd, shell=True)
