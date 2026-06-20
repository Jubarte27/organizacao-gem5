import m5
from m5.objects import *
from MyO3CPU import My_SIMD_Unit, MyIntALU, MyIntMultDiv, MyMemUnit, My_FP_ALU, My_FP_MultDiv
from CPUBase import CPUBase, MoreIntALU, MoreSIMDUnit

class MoreIntFUPool(FUPool):
    FUList = [ MoreIntALU(), MyIntMultDiv(), My_FP_ALU(),
               My_FP_MultDiv(), MoreSIMDUnit(),
               MyMemUnit() ]

class CPUMoreInt(CPUBase):
    fuPool = MoreIntFUPool()