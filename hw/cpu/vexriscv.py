from litex.soc.cores.cpu.vexriscv_smp import VexRiscvSMP


class VexRiscvSMPCustom(VexRiscvSMP):
    def __init__(self, **kwkargs):
        VexRiscvSMP.__init__(self, **kwargs)

    def add_sources(self, platform):
        vdir = get_data_mod("cpu", "vexriscv_smp").data_location
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
