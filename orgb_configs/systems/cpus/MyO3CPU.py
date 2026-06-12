# -*- coding: utf-8 -*-
######################################################################
######################################################################
##
## Arquivo de configuração da CPU
##
## Inicialmente, define uma série de classes que vão representar as
## unidades funcionais. Nessas classes, descreve-se o tipo de operação
## que aquela unidade funcional executa (opClass), a latência ou tempo
## que a operação leva para concluir (opLat), e a quantidade de
## unidades daquele tipo (count). Também é possível modelar se a
## unidade funcional opera em pipeline ou não (variável pipelined -
## que é True por padrão).
##
## A seguir, a classe MyO3CPU instancia o pool de unidades funcionais
## (MyFUPool), definidos antes, e define os demais parâmetros do
## processador. É possível mudar a largura dos estágios do pipeline
## (variáveis *Width), a latência de cada estágio (e.g.: variável
## fetchToDecodeDelay = 3 modela um pipeline com o Fetch dividido em 3
## estágios), a quantidade de posições nos buffers (*BufferSize,
## *QueueSize, *Entries).
##
## O fluxo de instruções entre os estágios do pipeline é:
##
## Fetch -> Decode -> Rename -> Dispatch,Issue,Execute,Writeback -> Commit.
##
## OBS: Os estágios Dispatch,Issue,Execute,Writeback são agrupados em um único
## estágio, chamado aqui de IEW.
##
######################################################################
######################################################################
import m5
from m5.objects import *

from m5.objects import DerivO3CPU

###############################################################################

## Unidades funcionais
##
## Cada classe especifica um tipo de unidade funcional.
##
## O campo opList especifica os tipos de operação que a FU executa e o campo
## count especifica a quantidade de unidades desse tipo.

###############################################################################

class MyIntALU(FUDesc):
    opList = [ OpDesc(opClass='IntAlu') ]
    count = 2

class MyIntMultDiv(FUDesc):
    opList = [ OpDesc(opClass='IntMult', opLat=3, pipelined=True),
               OpDesc(opClass='IntDiv', opLat=16, pipelined=False) ]

    # DIV and IDIV instructions in x86 are implemented using a loop which
    # issues division microops.  The latency of these microops should really be
    # one (or a small number) cycle each since each of these computes one bit
    # of the quotient.
    if buildEnv['TARGET_ISA'] in ('x86'):
        opList[1].opLat=1

    count = 1

class My_FP_ALU(FUDesc):
    opList = [ OpDesc(opClass='FloatAdd', opLat=2),
               OpDesc(opClass='FloatCmp', opLat=2),
               OpDesc(opClass='FloatCvt', opLat=2) ]
    count = 1

class My_FP_MultDiv(FUDesc):
    opList = [ OpDesc(opClass='FloatMult', opLat=4),
               OpDesc(opClass='FloatDiv',  opLat=12, pipelined=False),
               OpDesc(opClass='FloatSqrt', opLat=24, pipelined=False) ]
    count = 1

class My_SIMD_Unit(FUDesc):
    opList = [ OpDesc(opClass='SimdAdd',          opLat=2),
               OpDesc(opClass='SimdAddAcc',       opLat=2),
               OpDesc(opClass='SimdAlu',          opLat=2),
               OpDesc(opClass='SimdCmp',          opLat=2),
               OpDesc(opClass='SimdCvt',          opLat=2),
               OpDesc(opClass='SimdMisc',         opLat=2),
               OpDesc(opClass='SimdMult',         opLat=2),
               OpDesc(opClass='SimdMultAcc',      opLat=2),
               OpDesc(opClass='SimdShift',        opLat=2),
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
    count = 1

class MyMemUnit(FUDesc):
    opList = [ OpDesc(opClass='MemRead'),
               OpDesc(opClass='MemWrite'),
               OpDesc(opClass='IprAccess', opLat = 2, pipelined = False) ]
    count = 1

class MyFUPool(FUPool):
    FUList = [ MyIntALU(), MyIntMultDiv(), My_FP_ALU(),
               My_FP_MultDiv(), My_SIMD_Unit(),
               MyMemUnit() ]


############################################################

## Processador

############################################################

class MyO3CPU(DerivO3CPU):

############################################################
## Preditor de desvios
############################################################
    branchPred = TournamentBP() # Branch Predictor

############################################################
## Latências entre os diferentes estágios do pipeline.
## Pode ser usado para simular pipelines mais profundos.
############################################################
    #### Latências de avanço
    fetchToDecodeDelay   = 3 # Fetch to decode delay
    decodeToRenameDelay  = 2 # Decode to rename delay
    renameToIEWDelay     = 2 # Rename to Issue/Execute/Writeback delay
    renameToROBDelay     = 2 # Rename to reorder buffer delay
    issueToExecuteDelay  = 2 # Issue to execute delay internal to the IEW stage
    iewToCommitDelay     = 2 # Issue/Execute/Writeback to commit delay

    #### Latências de retorno
    decodeToFetchDelay   = 1 # Decode to fetch delay

    renameToFetchDelay   = 1 # Rename to fetch delay
    renameToDecodeDelay  = 1 # Rename to decode delay

    iewToFetchDelay      = 1 # Issue/Execute/Writeback to fetch delay
    iewToDecodeDelay     = 1 # Issue/Execute/Writeback to decode delay
    iewToRenameDelay     = 1 # Issue/Execute/Writeback to rename delay

    commitToFetchDelay   = 1 # Commit to fetch delay
    commitToDecodeDelay  = 1 # Commit to decode delay
    commitToRenameDelay  = 1 # Commit to rename delay
    commitToIEWDelay     = 1 # Commit to Issue/Execute/Writeback delay

############################################################
## Tamanho das estruturas do pipeline. Afetam a quantidade
## de instruções que podem ser armazenadas nos buffers.
############################################################

    fetchBufferSize  =  64 # Fetch buffer size in bytes
    fetchQueueSize   =  32 # Fetch queue size in micro-ops per thread
    numIQEntries     =  32 # Number of instruction queue entries
    numROBEntries    =  96 # Number of reorder buffer entries
    LQEntries        =  20 # Number of load queue entries
    SQEntries        =  12 # Number of store queue entries

    numPhysIntRegs   =  96 # Number of physical integer registers
    numPhysFloatRegs =  96 # Number of physical floating point registers

    numRobs          =  1 # Number of Reorder Buffers;

############################################################
## Largura das estruturas do pipeline. Afetam a quantidade
## de instruções processadas por ciclo em cada estágio.
############################################################

    fetchWidth    =  2 # Fetch width
    decodeWidth   =  2 # Decode width
    renameWidth   =  2 # Rename width
    dispatchWidth =  2 # Dispatch width
    issueWidth    =  2 # Issue width
    wbWidth       =  2 # Writeback width
    commitWidth   =  2 # Commit width
    squashWidth   = 16 # Squash width

    fuPool        = MyFUPool() # Functional Unit pool
