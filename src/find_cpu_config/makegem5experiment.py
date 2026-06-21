import sys
import json
from scipy.stats import qmc
from futypes import FUTypes
from math import log2, ceil

VARIABLES = {
    # "intLat": (1, 4),
    # "fpLat": (1, 4),
    "pipelineWidth": [2, 4, 8],
    "numROBEntries": [64, 128, 256, 512],
    "numIQEntries": [32, 64, 96],
    "intAluCount": [2, 4, 8, 16],
    "intAluLat": [1],
    "SIMDCount": [1, 2, 4, 8],
    "SIMDLat": [2],
    "fpAluCount": [1, 2, 4, 8],
    "fpLat": [2],
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

def is_integer(something):
    try:
        int(something)
        return True
    except ValueError:
        return False

def map_to_gem5_schema(configs: list[dict]) -> list[dict]:
    def getConfig(key: str, default): return config[key] if key in config else default

    cpu_json_list = []
    
    for idx, config in enumerate(configs):
        width = getConfig("pipelineWidth", 2)
        assoc = getConfig('assoc', 8)
        assoc = getConfig('assoc', 8)
        assoc = getConfig('assoc', 8)

        strSizeL1 = getConfig('sizeL1', 32)
        if is_integer(strSizeL1):
            sizeL1 = int(strSizeL1)
            strSizeL1 = f'{sizeL1}kB'
            tag_latency = ceil(0.4*log2(sizeL1)+0.3*log2(assoc)+1)
            data_latency = ceil(0.5*log2(sizeL1)+0.5*log2(assoc)+1)
        else:
            tag_latency = 1
            data_latency = 2

        tag_latency = getConfig('tagLatency', tag_latency)
        data_latency = getConfig('dataLatency', data_latency)
        response_latency = getConfig('responseLatency', 2)

        cpu_entry = {
            "name": f"CPU{idx + 1}",
            "cache": {
                "size": f'{strSizeL1}',
                "assoc": str(assoc),
                "tag_latency": tag_latency,
                "data_latency": data_latency,
                "response_latency": response_latency,
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
            },
            "fuPool": []
        }

        def addFU(type, count: int | str, opList):
            c = int(count) if is_integer(count) else int(config[count])
            cpu_entry["fuPool"].append({"type": type, "count": c, "opList": opList})

        def addAttrIfExists(name):
            if name in config:
                cpu_entry["attributes"][name] = str(config[name])

        addAttrIfExists("numROBEntries")
        addAttrIfExists("numIQEntries")
        addAttrIfExists("numPhysIntRegs")
        addAttrIfExists("numPhysFloatRegs")

        if "SIMDCount" in config:
            SIMDLat = getConfig("SIMDLat", 2)
            addFU(FUTypes.SIMDUnit, "SIMDCount", [
                { "name": 'SimdAdd', "lat": SIMDLat},
                { "name": 'SimdAddAcc', "lat": SIMDLat},
                { "name": 'SimdAlu', "lat": SIMDLat},
                { "name": 'SimdCmp', "lat": SIMDLat},
                { "name": 'SimdCvt', "lat": SIMDLat},
                { "name": 'SimdMisc', "lat": SIMDLat},
                { "name": 'SimdMult', "lat": SIMDLat},
                { "name": 'SimdMultAcc', "lat": SIMDLat},
                { "name": 'SimdShift', "lat": SIMDLat},
                { "name": 'SimdShiftAcc', "lat": SIMDLat},
                { "name": 'SimdSqrt', "lat": SIMDLat},
                { "name": 'SimdFloatAdd', "lat": SIMDLat},
                { "name": 'SimdFloatAlu', "lat": SIMDLat},
                { "name": 'SimdFloatCmp', "lat": SIMDLat},
                { "name": 'SimdFloatCvt', "lat": SIMDLat},
                { "name": 'SimdFloatDiv', "lat": SIMDLat},
                { "name": 'SimdFloatMisc', "lat": SIMDLat},
                { "name": 'SimdFloatMult', "lat": SIMDLat},
                { "name": 'SimdFloatMultAcc', "lat": SIMDLat},
                { "name": 'SimdFloatSqrt', "lat": SIMDLat}
            ])
        if "intAluCount" in config:
            intAluLat = getConfig("intAluLat", 2)
            addFU(FUTypes.IntALU, "intAluCount",[
                { "name": "IntAlu", "lat": intAluLat, "pipelined": True }
            ])
        if "fpAluCount" in config:
            fpLat = getConfig("fpLat", 2)
            addFU(FUTypes.FPAlu, "fpAluCount", [
                { "name": "FloatAdd", "lat": fpLat, "pipelined": True },
                { "name": "FloatCmp", "lat": fpLat, "pipelined": True },
                { "name": "FloatCvt", "lat": fpLat, "pipelined": True },
            ])
            
        if "intMultDivCount" in config:
            intMultDivLat = getConfig("intMultDivLat", 3)
            addFU(FUTypes.FPMultDiv, "intMultDivCount", [ 
                {"name":'IntMult', "lat": intMultDivLat, "pipelined":True},
                {"name":'IntDiv', "lat": 1, "pipelined":False},
            ])
        
        if "fpMultDivCount" in config:
            fpMultDivLat = getConfig("fpMultDivLat", 4)
            addFU(FUTypes.FPMultDiv, "fpMultDivCount", [ 
                {"name":'FloatMult', "lat": fpMultDivLat, "pipelined":True},
                {"name":'FloatDiv', "lat": fpMultDivLat * 3, "pipelined":False},
                {"name":'FloatSqrt', "lat": fpMultDivLat * 6, "pipelined":False},
            ])

        if any(k in config for k in ("memLat", "memPortsCount","MemReadLat","MemWriteLat")):
            memLat = getConfig("memLat", "default")
            memCount = int(getConfig("memPortsCount", 1))
            memReadLat = getConfig("MemReadLat", memLat)
            memWriteLat = getConfig("memWriteLat", memLat)
            addFU(FUTypes.MemUnit, memCount, [
                { "name": "MemRead", "lat": memReadLat, "pipelined": True },
                { "name": "MemWrite", "lat": memWriteLat, "pipelined": True },
                { "name": "IprAccess", "lat": memLat, "pipelined": True }
            ])
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