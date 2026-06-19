import json
import os
from pathlib import Path
import re
import sys
from futypes import FUTypes

def sanitize_identifier(name):
    clean = re.sub(r'[^a-zA-Z0-9_]', '', name)
    if clean and clean[0].isdigit():
        clean = "_" + clean
    return clean if clean else "GeneratedIdentifier"

def format_attribute_value(val):
    if isinstance(val, (bool, int, float)): return str(val)
    
    val_str = str(val).strip()

    if val_str.lower() == 'true': return 'True'
    if val_str.lower() == 'false': return 'False'

    try:
        int(val_str)
        return val_str
    except ValueError:
        pass
    try:
        float(val_str)
        return val_str
    except ValueError:
        pass

    if re.match(r'^[a-zA-Z0-9_]+\(.*\)$', val_str):
        return val_str

    return f"'{val_str}'"

def make_cpu(cpu, idx, target_dir):
    attributes = cpu.get("attributes", {})
    fu_pool = cpu.get("fuPool", [])

    lines = ["""\
import m5
from m5.objects import *
from MyO3CPU import MyO3CPU, MyIntALU, MyIntMultDiv, My_FP_ALU, My_FP_MultDiv, My_SIMD_Unit, MyMemUnit
""",
    ]

    fu_class_names: list[str] = []
    overwritten_types: set[FUTypes] = set()
    for fu_idx, fu in enumerate(fu_pool):
        fu_class_name = f"FU_{fu_idx}"
        fu_class_names.append(fu_class_name)
        overwritten_types.add(FUTypes(fu.get("type")))

        lines.append(f"class {fu_class_name}(FUDesc):")
        lines.append("    opList = [")
        for op in fu.get("opList", []):
            op_name = op.get("name")
            op_lat = op.get("lat", 1)
            op_pipelined = "True" if op.get("pipelined", True) else "False"
            lines.append(f"        OpDesc(opClass='{op_name}', opLat={op_lat}, pipelined={op_pipelined}),")
        lines.append("    ]")
        lines.append(f"    count = {fu.get('count', 1)}\n")

    pool_class_name = f"FUPool{idx}"
    lines.append(f"class {pool_class_name}(FUPool):")
    lines.append("    FUList = [")
    lines.extend(f"        {fu_type}()," for fu_type in FUTypes if fu_type not in overwritten_types)
    lines.extend(f"        {f_name}()," for f_name in fu_class_names)
    lines.append("    ]\n")

    lines.append(f"class CPUBase(MyO3CPU):")

    if attributes:
        for attr_key, attr_val in attributes.items():
            sanitized_key = sanitize_identifier(attr_key)
            formatted_val = format_attribute_value(attr_val)
            lines.append(f"    {sanitized_key} = {formatted_val}")
    
    # Assign the compiled functional unit pool to the CPU
    lines.append(f"    fuPool = {pool_class_name}()")

    # Create a clean, snake_case filename 
    
    target_path = Path(target_dir).joinpath("CPUBase.py")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with open(target_path.as_posix(), 'w', encoding='utf-8') as out_file:
        out_file.write("\n".join(lines) + "\n")

def make_cache(cpu, idx, target_dir):
    lines = ["""\
from m5.objects import Cache

class BasicL1ICache(Cache):

    size = '32kB'
    assoc = 8
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 4
    tgts_per_mshr = 16

    def __init__(self, options=None):
        super(BasicL1ICache, self).__init__()        
        pass

class BasicL1DCache(Cache):

""",
    ]
    lines.extend((f"    {sanitize_identifier(attr_key)} = {format_attribute_value(attr_val)}") for attr_key, attr_val in cpu.get("cache", {}).items())
    lines.append("""

    def __init__(self, latency):
        super(BasicL1DCache, self).__init__()
        
        self.data_latency = latency
        pass

class BasicL2Cache(Cache):

    size = '256kB'
    assoc = 8
    tag_latency = 8
    data_latency = 12
    response_latency = 4
    mshrs = 16
    tgts_per_mshr = 16

    def __init__(self, options=None):
        super(BasicL2Cache, self).__init__()
        pass


class BasicL3Cache(Cache):

    size = '2MB'
    assoc = 16
    tag_latency = 12
    data_latency = 36
    response_latency = 4
    mshrs = 16
    tgts_per_mshr = 16

    def __init__(self, options=None):
        super(BasicL3Cache, self).__init__()
        pass
""")

    target_path = Path(target_dir).joinpath("basic_caches.py")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with open(target_path.as_posix(), 'w', encoding='utf-8') as out_file:
        out_file.write("\n".join(lines) + "\n")

def parse_and_generate_cpus(json_filepath='cpus.json', target_dir=''):
    if not os.path.exists(json_filepath):
        print(f"Error: The configuration file '{json_filepath}' was not found.")
        return

    with open(json_filepath, 'r', encoding='utf-8') as f:
        try:
            cpu_list = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
            return

    for idx, cpu in enumerate(cpu_list):
        name = sanitize_identifier(cpu.get("name", f"CPU_{idx}"))
        p = Path(target_dir).joinpath(name)
        p.mkdir(parents=True, exist_ok=True)

        make_cpu(cpu, idx, p.as_posix())
        make_cache(cpu, idx, p.as_posix())
        

if __name__ == "__main__":
    parse_and_generate_cpus(sys.argv[1] if len(sys.argv) > 1 else "cpus.json", sys.argv[2] if len(sys.argv) > 2 else os.getcwd())