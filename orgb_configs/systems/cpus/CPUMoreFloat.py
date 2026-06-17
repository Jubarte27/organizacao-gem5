import m5
from m5.objects import *
from MyO3CPU import My_SIMD_Unit, MyIntALU, MyIntMultDiv, MyMemUnit
from CPUBase import CPUBase

class MoreFloat_FP_ALU(FUDesc):
    opList = [ OpDesc(opClass='FloatAdd', opLat=2),
               OpDesc(opClass='FloatCmp', opLat=2),
               OpDesc(opClass='FloatCvt', opLat=2) ]
    count = 4

class MoreFloat_FP_MultDiv(FUDesc):
    opList = [ OpDesc(opClass='FloatMult', opLat=4),
               OpDesc(opClass='FloatDiv',  opLat=12, pipelined=False),
               OpDesc(opClass='FloatSqrt', opLat=24, pipelined=False) ]
    count = 4

class MoreFloatFUPool(FUPool):
    FUList = [ MyIntALU(), MyIntMultDiv(), MoreFloat_FP_ALU(),
               MoreFloat_FP_MultDiv(), My_SIMD_Unit(),
               MyMemUnit() ]

class CPUMoreFloat(CPUBase):
    fuPool = MoreFloatFUPool()