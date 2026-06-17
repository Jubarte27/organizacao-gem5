import m5
from m5.objects import *
from MyO3CPU import My_SIMD_Unit, MyIntALU, MyIntMultDiv, MyMemUnit, My_FP_ALU, My_FP_MultDiv
from CPUBase import CPUBase

class MoreMem_MemUnit(FUDesc):
    opList = [ OpDesc(opClass='MemRead', opLat = 1),
               OpDesc(opClass='MemWrite', opLat = 1),
               OpDesc(opClass='IprAccess', opLat = 1) ]
    count = 1

class MoreIntALU(FUDesc):
    opList = [ OpDesc(opClass='IntAlu', opLat=1) ]
    count = 8

class More_SIMD_Unit(FUDesc):
    opList = [ OpDesc(opClass='SimdAdd',          opLat=1),
               OpDesc(opClass='SimdAddAcc',       opLat=2),
               OpDesc(opClass='SimdAlu',          opLat=2),
               OpDesc(opClass='SimdCmp',          opLat=2),
               OpDesc(opClass='SimdCvt',          opLat=2),
               OpDesc(opClass='SimdMisc',         opLat=2),
               OpDesc(opClass='SimdMult',         opLat=2),
               OpDesc(opClass='SimdMultAcc',      opLat=2),
               OpDesc(opClass='SimdShift',        opLat=1),
               OpDesc(opClass='SimdShiftAcc',     opLat=2),
               OpDesc(opClass='SimdSqrt',         opLat=2),
               OpDesc(opClass='SimdFloatAdd',     opLat=2),
               OpDesc(opClass='SimdFloatAlu',     opLat=2),
               OpDesc(opClass='SimdFloatCmp',     opLat=2),
               OpDesc(opClass='SimdFloatCvt',     opLat=2),
               OpDesc(opClass='SimdFloatDiv',     opLat=2),
               OpDesc(opClass='SimdFloatMisc',    opLat=2),
               OpDesc(opClass='SimdFloatMult',    opLat=2),
               OpDesc(opClass='SimdFloatMultAcc', opLat=2),
               OpDesc(opClass='SimdFloatSqrt',    opLat=2) ]
    count = 4

class MoreSIMDFUPool(FUPool):
    FUList = [ MoreIntALU(), MyIntMultDiv(), My_FP_ALU(),
               My_FP_MultDiv(), More_SIMD_Unit(),
               MoreMem_MemUnit() ]

class CPUBigROB(CPUBase):
    fuPool = MoreSIMDFUPool()