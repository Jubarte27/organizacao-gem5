from MyO3CPU import MyO3CPU

class CPUBase(MyO3CPU):
    fetchWidth    = 4
    decodeWidth   = 4
    renameWidth   = 4
    dispatchWidth = 4
    issueWidth    = 4
    wbWidth       = 4
    commitWidth   = 4

    LQEntries = 48
    SQEntries = 32

    numIQEntries     = 64

    numPhysIntRegs   = 144
    numPhysFloatRegs = 144