#!/bin/env bash
set -e

adjectives=("happy" "brave" "clever" "bright" "calm" "jolly" "kind" "silly" "witty" "cozy")
animals=("panda" "koala" "otter" "fox" "badger" "hedgehog" "dolphin" "penguin" "owl" "rabbit")

main() {
    set_log_depth 0

    run_adj=${adjectives[$RANDOM % ${#adjectives[@]}]}
    run_anim=${animals[$RANDOM % ${#animals[@]}]}
    run_uuid=$(cat /proc/sys/kernel/random/uuid)

    local docker_dir="/data"

    local run_dir=".run/$run_adj-$run_anim-$run_uuid"
    mkdir -p "$run_dir"
    echo i live on "$run_dir"

    local build_dir="src/build"
    mkdir -p "$build_dir"

    python3 "$PROJECT_DIR/src/make_data.py" 8 10
    cp "$PROJECT_DIR/src/big_array.h" "$run_dir/radix.big_array.h"
    cd "$PROJECT_DIR" && run_docker ./compile.sh "$docker_dir/$run_dir"
    EXEC="$GEM_5_DIR/build/X86/gem5.opt"

    cp -r orgb_configs "$run_dir/orgb_configs"
    cd "$PROJECT_DIR/$run_dir" || exit 1

    cp "$PROJECT_DIR/src/cha.c" "$PROJECT_DIR/$run_dir/cha.in"

    run_docker $EXEC --outdir=chud.m5out orgb_configs/simulate.py run-benchmark -c chud -o "100" 2>&1 | tee "$PROJECT_DIR/$run_dir/chud.txt"
    run_docker $EXEC --outdir=radix.m5out orgb_configs/simulate.py run-benchmark -c radix 2>&1 | tee "$PROJECT_DIR/$run_dir/radix.txt"
    run_docker $EXEC --outdir=cha.m5out orgb_configs/simulate.py run-benchmark -c cha 2>&1 | tee "$PROJECT_DIR/$run_dir/cha.txt"
}

build_if_not_exists() {
    if [[ "$(docker images -q "$1" 2> /dev/null)" == "" ]]; then
        echo "Image $1 does not exist. Building..."
        docker build --build-arg MAX_THREAD="$(nproc --ignore 2)" --force-rm --tag "$1" "$2"
        # make -C "$PROJECT_DIR" build
    else
        echo "Image $1 already exists. Skipping build."
    fi
}

run_docker()        { docker run --rm -v "$(pwd):/data" -w /data $IMAGE_NAME "${@}"; }
run_docker_orgb()   { docker run --rm -v "$(pwd):/data" -w /data orgb:latest "${@}"; }


_setConfigArgs() {
    while [ "${1:-}" != '' ]; do
        case "$1" in
            ## Options
            
            ## end of Options
            [!-]*)
                break
                ;;
            *)
                log "$WARN" "Unknown option \"$1\", ignoring" 0 
            ;;
        esac
        shift
    done
}


set_env() {
    IMAGE_NAME=orgb:latest
    GEM_5_DIR=/opt/gem5
}

SCRIPT_DIR=$(dirname "$(readlink -e "${BASH_SOURCE[0]}")") && source "$SCRIPT_DIR/util.bash"
set_env
_setConfigArgs "$@"
main "$@"
