import m5
from m5.objects import *
from MyO3CPU import My_FP_ALU, My_SIMD_Unit, MyIntALU, MyIntMultDiv, My_FP_MultDiv
from CPUBase import CPUBase

class MoreMem_MemUnit(FUDesc):
    opList = [ OpDesc(opClass='MemRead', opLat = 1),
               OpDesc(opClass='MemWrite', opLat = 1),
               OpDesc(opClass='IprAccess', opLat = 1, pipelined = False) ]
    count = 10

class MoreMemFUPool(FUPool):
    FUList = [ MyIntALU(), MyIntMultDiv(), My_FP_ALU(),
               My_FP_MultDiv(), My_SIMD_Unit(),
               MoreMem_MemUnit() ]

class CPUMoreMem(CPUBase):
    fuPool = MoreMemFUPool()