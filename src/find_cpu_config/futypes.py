from enum import StrEnum

class FUTypes(StrEnum):
    IntALU = "MyIntALU"
    IntMultDiv = "MyIntMultDiv"
    FPAlu = "My_FP_ALU"
    FPMultDiv = "My_FP_MultDiv"
    SIMDUnit = "My_SIMD_Unit"
    MemUnit = "MyMemUnit"