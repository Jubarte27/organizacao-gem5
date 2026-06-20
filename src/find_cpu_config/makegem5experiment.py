import sys
import json
from scipy.stats import qmc
from futypes import FUTypes

VARIABLES = {
    # "intLat": (1, 4),
    # "fpLat": (1, 4),
    "pipelineWidth": [2, 4, 8],
    "numROBEntries": [64, 128, 256, 512],
    "numIQEntries": [32, 64, 96],
    "intAluCount": [2, 4, 8, 16],
    "fpAluCount": [1, 2, 4, 8],
    "memPortsCount": [1, 2, 3, 4],
    "numPhysIntRegs" : [96, 128, 144, 256],
    "numPhysFloatRegs": [96, 128, 256],

    "sizeL1": [32, 64, 128],
    "assoc": [2, 4, 8, 16],
}

NUM_EXPERIMENTS = 20

def generate_lhs_samples(variables: dict, num_samples: int) -> list[dict]:
    var_names = list(variables.keys())
    dimension = len(var_names)
    sampler = qmc.LatinHypercube(d=dimension)
    samples = sampler.random(n=num_samples)
    
    experimental_configs = []
    
    for row_idx in range(num_samples):
        config = {}
        for col_idx, var_name in enumerate(var_names):
            p = samples[row_idx, col_idx]
            bounds = variables[var_name]
            if isinstance(bounds, list):
                idx = int(p * len(bounds))
                idx = min(max(idx, 0), len(bounds) - 1)
                config[var_name] = bounds[idx]
            elif isinstance(bounds, tuple):
                if isinstance(bounds[0], int) and isinstance(bounds[1], int):
                    v_min, v_max = bounds
                    val = int(v_min + p * (v_max - v_min + 1))
                    val = min(max(val, v_min), v_max)
                    config[var_name] = val
                else:
                    v_min, v_max = bounds
                    val = v_min + p * (v_max - v_min)
                    config[var_name] = val
                    
        experimental_configs.append(config)
        
    return experimental_configs

def map_to_gem5_schema(configs: list[dict]) -> list[dict]:
    cpu_json_list = []
    
    for idx, config in enumerate(configs):
        width = config["pipelineWidth"]

        cache_latency = 1 << (VARIABLES["sizeL1"].index(config['sizeL1']) + VARIABLES["assoc"].index(config['assoc']))
        cpu_entry = {
            "name": f"CPU{idx + 1}",
            "cache": {
                "size": f'{config['sizeL1']}kB',
                "assoc": str(config['assoc']),
                "tag_latency": cache_latency,
                "data_latency": cache_latency,
                "response_latency": 1,
                "mshrs": 4,
                "tgts_per_mshr": 16,
            },
            "attributes": {
                "fetchWidth": str(width),
                "decodeWidth": str(width),
                "renameWidth": str(width),
                "dispatchWidth": str(width),
                "issueWidth": str(width),
                "wbWidth": str(width),
                "commitWidth": str(width),
                "numROBEntries": str(config["numROBEntries"]),
                "numIQEntries": str(config["numIQEntries"]),
                "numPhysIntRegs": str(config["numPhysIntRegs"]),
                "numPhysFloatRegs": str(config["numPhysFloatRegs"]),
            },
            "fuPool": [
                {
                    "type": FUTypes.IntALU,
                    "count": int(config["intAluCount"]),
                    "opList": [
                        { "name": "IntAlu", "lat": 1, "pipelined": True }
                    ]
                },
                {
                    "type": FUTypes.FPAlu,
                    "count": int(config["fpAluCount"]),
                    "opList": [
                        { "name": "FloatAdd", "lat": 2, "pipelined": True },
                        { "name": "FloatCmp", "lat": 2, "pipelined": True },
                        { "name": "FloatCvt", "lat": 2, "pipelined": True },
                    ]
                },
                {
                    "type": FUTypes.MemUnit,
                    "count": int(config["memPortsCount"]),
                    "opList": [
                        { "name": "MemRead", "lat": 1, "pipelined": True },
                        { "name": "MemWrite", "lat": 1, "pipelined": True },
                        { "name": "IprAccess", "lat": 1, "pipelined": True }
                    ]
                }
            ]
        }
        cpu_json_list.append(cpu_entry)
        
    return cpu_json_list

if __name__ == "__main__":
    print(f"Generating {NUM_EXPERIMENTS} variants using SciPy QMC Latin Hypercube Sampler...")
    
    raw_configs = generate_lhs_samples(VARIABLES, NUM_EXPERIMENTS)
    
    formatted_cpus = map_to_gem5_schema(raw_configs)
    
    output_filename = sys.argv[1] if len(sys.argv) > 1 else "cpus.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(formatted_cpus, f, indent=2)
        
    print(f"Successfully compiled and saved exploration matrix to '{output_filename}'")