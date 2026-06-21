import json
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import cast
from makegem5experiment import map_to_gem5_schema
from makegem5test import make_cpu, make_cache
from makegem5experiment import VARIABLES as _VARIABLES, getDefault

# =========================================================================
# GA HYPERPARAMETERS & SEARCH SPACE
# =========================================================================
POPULATION_SIZE = 20
GENERATIONS = 20
MUTATION_RATE = 0.1

def find_type(v) -> str:
    if isinstance(v, list):
        return "list"
    if isinstance(v, tuple):
        t = cast(tuple, v)
        if isinstance(t[0], float): return "float"
        if isinstance(t[0], int): return "int"

    raise TypeError("Errado")

VARIABLES = {k: {"type": find_type(v), "range": v} for k, v in _VARIABLES.items()}

# Directories
HERE: Path = Path(__file__).parent
WORKSPACE: Path = Path(sys.argv[1]) if len(sys.argv)  > 1 else HERE.joinpath("./ga_workspace")
CPUS_JSON_PATH: Path = WORKSPACE.joinpath("cpus.json")


def generate_random_individual() -> dict[str, int | float]:
    ind: dict[str, int | float] = {}
    for var, cfg in VARIABLES.items():
        if cfg["type"] == "int":
            ind[var] = random.randint(*cfg["range"])
        elif cfg["type"] == "float":
            ind[var] = random.uniform(*cfg["range"])
        elif cfg["type"] == "list":
            ind[var] = random.choice(cfg["range"])
    return ind

def crossover(parent1, parent2):
    child = {}
    for var in VARIABLES.keys():
        child[var] = parent1[var] if random.random() > 0.5 else parent2[var]
    return child

def mutate(individual):
    for var, cfg in VARIABLES.items():
        if random.random() < MUTATION_RATE:
            if cfg["type"] == "int":
                individual[var] = random.randint(*cfg["range"])
            elif cfg["type"] == "float":
                individual[var] = random.uniform(*cfg["range"])
            elif cfg["type"] == "list":
                individual[var] = random.choice(cfg["range"])
    return individual

def build_cpus_json(population: list[dict[str, int | float | str]]):
    cpu_json_list = map_to_gem5_schema(population)
        
    with open(CPUS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(cpu_json_list, f, indent=2)

def calculate_fitness(run_dir: Path, config):
    algos    = ("radix"  , "cha"    , "chud")
    baseline = (0.379127 , 0.909584 , 0.276885)
    
    stats_files: list[Path] = [run_dir.joinpath(f"{algo}.m5out/stats.txt") for algo in  algos] # Adjust if gem5 outputs to m5out/stats.txt
    IPC = 0 # Default near-zero fitness if simulation fails
    # Extract IPC from stats.txt
    for base, stats_file in zip(baseline, stats_files):
        ipc = -0.0001
        with open(stats_file, 'r') as f:
            for line in f:
                match = re.match(r'^\s*system\.cpu\.ipc\s+([0-9\.]+)', line)
                if match:
                    ipc = float(match.group(1))
                    break
        if ipc < 0:
            raise ValueError("Morri aaaaaaaa")
        IPC += ipc
    IPC /= len(algos)
    print(IPC)

    weights = 10 + 1 + 1 + 10 + 10 + 10 + 0.5 + 0.5 + 10 + 10

    cost = (
        (getDefault(config, "pipelineWidth", 2) * 10) +
        (getDefault(config, "numROBEntries", 96) * 1) +
        (getDefault(config, "numIQEntries", 32) * 1) +
        (getDefault(config, "intAluCount", 2) * 10) +
        (getDefault(config, "fpAluCount", 1) * 10) + 
        (getDefault(config, "memPortsCount", 1) * 10) +
        (getDefault(config, "numPhysIntRegs", 96) * 0.5) +
        (getDefault(config, "numPhysFloatRegs", 96) * 0.5) +
        ((1 << (int(getDefault(config, "sizeL1", 32)) // 32)) * 10) +
        ((1 << (int(getDefault(config, "assoc", 8)) // 8)) * 10)
    )
    
    return (weights * (IPC ** 2)) / cost, IPC

# population: list[dict[str, int | float | str]]
def run_generation(population, gen_num: int) -> tuple[list[float], list[float]]:
    """Executes the full pipeline for the current generation."""
    print(f"\n========== GENERATION {gen_num} ==========")
    
    if os.path.exists(WORKSPACE):
        shutil.rmtree(WORKSPACE)
    os.makedirs(WORKSPACE)

    names = [pop["name"] if "name" in pop else f"CPU{idx + 1}" for idx, pop in enumerate(population)]
    
    build_cpus_json(population)

    subprocess.run(["python3", HERE.joinpath("makegem5test.py").absolute().as_posix(), CPUS_JSON_PATH.as_posix(), WORKSPACE.as_posix()])
    subprocess.run([HERE.joinpath("../../scripts/run_test_best_config.bash").absolute().as_posix(), WORKSPACE.as_posix()])
    
    fitness_scores: list[float] = []
    ipcs: list[float] = []
    for i, config in enumerate(population):
        run_name = f"CPU{i + 1}" 
        run_dir = WORKSPACE.joinpath("run", run_name)
        
        fit_score, ipc = calculate_fitness(run_dir, config)
        fitness_scores.append(fit_score)
        ipcs.append(ipc)
        print(f"Ind {i} | IPC: {ipc:.4f} | Fitness: {fit_score:.6f}")

        # print(run_dir, run_dir.parent.joinpath(names[i]))
        run_dir.rename(run_dir.parent.joinpath(names[i]))
        
    return fitness_scores, ipcs

if __name__ == "__main__":
    population = [generate_random_individual() for _ in range(POPULATION_SIZE)]
    
    best_config_overall = None
    best_fitness_overall = -1
    
    for generation in range(GENERATIONS):
        fitness_scores, ipcs = run_generation(population, generation)
        
        gen_best_idx = fitness_scores.index(max(fitness_scores))
        gen_best_fitness = fitness_scores[gen_best_idx]
        
        if gen_best_fitness > best_fitness_overall:
            best_fitness_overall = gen_best_fitness
            best_config_overall = population[gen_best_idx]
            
        print(f"\n--> Best of Gen {generation}: IPC={ipcs[gen_best_idx]:.4f}, Fit={gen_best_fitness:.6f}")
        
        new_population = []
        new_population.append(population[gen_best_idx])
        
        while len(new_population) < POPULATION_SIZE:
            tourney = random.sample(list(enumerate(fitness_scores)), 2)
            parent1_idx = max(tourney, key=lambda item: item[1])[0]
            
            tourney = random.sample(list(enumerate(fitness_scores)), 2)
            parent2_idx = max(tourney, key=lambda item: item[1])[0]
            
            child = crossover(population[parent1_idx], population[parent2_idx])
            child = mutate(child)
            new_population.append(child)
            
        population = new_population

    print("\n================ SEARCH COMPLETE ================")
    print(f"Best Configuration Found (Fitness: {best_fitness_overall:.6f}):")
    print(json.dumps(best_config_overall, indent=2))
