import json
import os
import random
import re
import shutil
import subprocess
import sys
from makegem5experiment import VARIABLES, map_to_gem5_schema
from makegem5test import parse_and_generate_cpus
from run_ga_optimization import run_generation

fixed_config: dict[str, int | float | str] = {
    "name": "baseline",
    "pipelineWidth": 4,
    "numROBEntries": 128,
    "numIQEntries": 64,

    "intAluCount": 4,
    "fpAluCount": 2,

    "memPortsCount": 1,
    "memLat": 1,

    "numPhysIntRegs": 96,
    "numPhysFloatRegs": 96,

    "sizeL1": 32,
    "assoc": 8,
}

def main():
    WorseMem = fixed_config.copy()
    WorseMem["memLat"] = 8
    WorseMem["name"] = "WorseMem"

    MoreInt = fixed_config.copy()
    MoreInt["intAluCount"] = 8
    MoreInt["name"] = "MoreInt"

    MoreFp = fixed_config.copy()
    MoreFp["fpAluCount"] = 8
    MoreFp["name"] = "MoreFp"

    raw_configs = [fixed_config, WorseMem, MoreInt, MoreFp]

    run_generation(raw_configs, 1)

    # formatted_cpus = map_to_gem5_schema(raw_configs)
    
    # output_filename = sys.argv[1] if len(sys.argv) > 1 else "cpus.json"
    # with open(output_filename, "w", encoding="utf-8") as f:
    #     json.dump(formatted_cpus, f, indent=2)

    # parse_and_generate_cpus(output_filename)



if __name__ == "__main__":
    main()
