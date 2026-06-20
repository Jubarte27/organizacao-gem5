import json
import os
import random
import re
import shutil
import subprocess
from makegem5experiment import VARIABLES
from run_ga_optimization import run_generation

best_overall_config: dict[str, int | float] = {
    "pipelineWidth": 4,
    "numROBEntries": 128,
    "numIQEntries": 64,
    "intAluCount": 4,
    "fpAluCount": 2,
    "memPortsCount": 1,
    "numPhysIntRegs": 96,
    "numPhysFloatRegs": 96,
    "sizeL1": 32,
    "assoc": 8
}

# best_overall_config: dict[str, int | float] = {
#     "pipelineWidth": 2,
#     "numROBEntries": 96,
#     "numIQEntries": 32,
#     "intAluCount": 2,
#     "fpAluCount": 1,
#     "memPortsCount": 1,
#     "numPhysIntRegs": 96,
#     "numPhysFloatRegs": 96,
#     "sizeL1": 32,
#     "assoc": 8
# }

def main():
    sensitivity_configs: dict[str, dict[str, int | float]] = {"CPUbaseline": best_overall_config}
    
    # Generate extreme permutations for every variable
    for var, ran in VARIABLES.items():
        low_val = ran[0]
        high_val = ran[-1]
        
        # LOW Variant
        low_config = best_overall_config.copy()
        low_config[var] = low_val
        sensitivity_configs[f"{var}_LOW"] = low_config
        
        # HIGH Variant
        high_config = best_overall_config.copy()
        high_config[var] = high_val
        sensitivity_configs[f"{var}_HIGH"] = high_config

    print(f"Dispatching Baseline + {len(sensitivity_configs)-1} Sensitivity Variants...")
    fitnesss, ipcs = run_generation(list(sensitivity_configs.values()), 0)
    sensitivity_results = {k:{"fitness": fitnesss[i], "ipc":ipcs[i] } for i, k in enumerate(sensitivity_configs)}


    baseline_fitness = sensitivity_results["CPUbaseline"]["fitness"]
    baseline_ipc = sensitivity_results["CPUbaseline"]["ipc"]
    
    report_data = []
    for name, data in sensitivity_results.items():
        if name == "CPUbaseline":
            continue
            
        delta_fitness = data["fitness"] - baseline_fitness
        delta_ipc = data["ipc"] - baseline_ipc
        
        report_data.append({
            "Variant": name,
            "Fitness": data["fitness"],
            "Delta_Fitness": delta_fitness,
            "IPC": data["ipc"],
            "Delta_IPC": delta_ipc
        })
        
    report_data.sort(key=lambda x: abs(x["Delta_Fitness"]), reverse=True)
    
    print(f"CPUbaseline | Fitness: {baseline_fitness:.6f} | IPC: {baseline_ipc:.4f}\n")
    print(f"{'Variant Name':<25} | {'Fitness':<10} | {'Δ Fitness':<12} | {'IPC':<8} | {'Δ IPC':<8}")
    print("-" * 75)
    
    for row in report_data:
        fit_sign = "+" if row["Delta_Fitness"] > 0 else ""
        ipc_sign = "+" if row["Delta_IPC"] > 0 else ""
        
        print(f"{row['Variant']:<25} | {row['Fitness']:<10.6f} | {fit_sign}{row['Delta_Fitness']:<11.6f} | {row['IPC']:<8.4f} | {ipc_sign}{row['Delta_IPC']:<8.4f}")

if __name__ == "__main__":
    main()