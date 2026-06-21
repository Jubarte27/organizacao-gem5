import json
import os
import random
import re
import shutil
import subprocess
import sys
from makegem5experiment import VARIABLES, map_to_gem5_schema
from makegem5test import parse_and_generate_cpus
from run_ga_optimization import simulate_generation

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

## horrível, mas fica assim por enquanto
def vary_cache(config: dict[str, int | float | str], value: int | float | str):
    varied_cache = config.copy()
    varied_cache["sizeL1"] = value
    return varied_cache

def vary_name(config: dict[str, int | float | str], name: str):
    varied = config.copy()
    varied["name"] = name
    return varied

def main():
    raw_configs = [fixed_config,
                   *(vary_name(vary_cache(fixed_config, f'{n}B'), f"VaryCache{n}B") for n in (512, 1024)),
                   *(vary_name(vary_cache(fixed_config, n), f"VaryCache{n}kB") for n in (2, 4, 8, 16, 32))
    ]

    simulate_generation(raw_configs)

if __name__ == "__main__":
    main()
