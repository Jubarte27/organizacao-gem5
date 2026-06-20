import m5
from m5.objects import *
from MyO3CPU import My_FP_ALU, My_SIMD_Unit, MyIntALU, MyMemUnit, MyIntMultDiv, My_FP_MultDiv
from CPUBase import CPUBase, MoreMemUnit


class MoreMemFUPool(FUPool):
    FUList = [ MyIntALU(), MyIntMultDiv(), My_FP_ALU(),
               My_FP_MultDiv(), My_SIMD_Unit(),
               MoreMemUnit() ]

class CPUMoreMem(CPUBase):
    fuPool = MoreMemFUPool()