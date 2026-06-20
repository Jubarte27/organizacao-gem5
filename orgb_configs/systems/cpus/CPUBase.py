from MyO3CPU import MyO3CPU
from m5.objects import *
from MyO3CPU import My_SIMD_Unit, MyIntALU, MyIntMultDiv, MyMemUnit, My_FP_ALU, My_FP_MultDiv

class LittleMoreFPALU(My_FP_ALU):
    count = 2

class BaseFUPool(FUPool):
    FUList = [ MyIntALU(), MyIntMultDiv(), LittleMoreFPALU(),
               My_FP_MultDiv(), My_SIMD_Unit(),
               MyMemUnit() ]

class CPUBase(MyO3CPU):
    numROBEntries    =  64

    LQEntries = 48
    SQEntries = 32

    numIQEntries     = 32

    numPhysIntRegs   = 144
    numPhysFloatRegs = 144

    fuPool = BaseFUPool()


# used by the others

class MoreIntALU(MyIntALU):
    count = 8

class MoreFPALU(My_FP_ALU):
    count = 4

class MoreFPMultDiv(My_FP_MultDiv):
    count = 4

class MoreSIMDUnit(My_SIMD_Unit):
    count = 4

class MoreMemUnit(MyMemUnit):
    count = 4

