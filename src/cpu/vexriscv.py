from litex.soc.cores.cpu.vexriscv_smp import VexRiscvSMP


class VexRiscvSMPCustom(VexRiscvSMP):
    def __init__(self, **kwkargs):
        VexRiscvSMP.__init__(self, **kwargs)
