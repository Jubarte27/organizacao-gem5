from MyO3CPU import MyO3CPU

class CPUBase(MyO3CPU):
    fetchWidth    =  4 # Fetch width
    decodeWidth   =  4 # Decode width
    renameWidth   =  4 # Rename width
    dispatchWidth =  4 # Dispatch width
    issueWidth    =  4 # Issue width
    wbWidth       =  4 # Writeback width
    commitWidth   =  4 # Commit width
    squashWidth   = 32 # Squash width