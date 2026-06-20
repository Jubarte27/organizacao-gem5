import m5
from m5.objects import *
from MyO3CPU import My_SIMD_Unit, MyIntALU, MyIntMultDiv, MyMemUnit, My_FP_ALU, My_FP_MultDiv
from CPUBase import CPUBase, MoreFPALU, MoreFPMultDiv, MoreSIMDUnit



class MoreFloatFUPool(FUPool):
    FUList = [ MyIntALU(), MyIntMultDiv(), MoreFPALU(),
               MoreFPMultDiv(), MoreSIMDUnit(),
               MyMemUnit() ]

class CPUMoreFloat(CPUBase):
    fuPool = MoreFloatFUPool()