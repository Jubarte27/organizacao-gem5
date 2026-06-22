import json
import os
import random
import re
import shutil
import subprocess
import sys
from makegem5experiment import VARIABLES, map_to_gem5_schema
from makegem5test import parse_and_generate_cpus
from run_ga_optimization import simulate_generation, HERE

fixed_config: dict[str, int | float | str] = {
    "name": "baseline",
    "pipelineWidth": 4,
    "numROBEntries": 128,
    "numIQEntries": 64,

    "intAluCount": 4,
    "fpAluCount": 2,

    "numPhysIntRegs": 96,
    "numPhysFloatRegs": 96,

    "tagLatency": 1,
    "dataLatency": 2,
    "sizeL1": 32,
    "assoc": 8,
}



def vary1(config: dict[str, int | float | str], what: str, value: int | float | str):
    varied = config.copy()
    varied[what] = value
    return varied

def vary(config: dict[str, int | float | str], **kargs):
    varied = config.copy()
    for k, v in kargs.items():
        varied[k] = v
    return varied

def main():
    simulate_generation([
        fixed_config,
        *(vary(fixed_config, sizeL1=f'{n}B', name=f"Cache{n}B") for n in (512,)),
        *(vary(fixed_config, sizeL1=n, name=f"Cache{n}kB") for n in (8, 16, 64, 128))
    ], HERE.joinpath("Cache"))

    simulate_generation([
        fixed_config,
        *(vary(fixed_config, MemReadLat=n, name=f"MemRead{n}") for n in (8, 16, 32))
    ], HERE.joinpath("MemRead"))

    simulate_generation([
        fixed_config,
        *(vary(fixed_config, numPhysIntRegs=n, name=f"IntRegs{n}") for n in (64, 128, 256))
    ], HERE.joinpath("IntRegs"))

if __name__ == "__main__":
    main()
