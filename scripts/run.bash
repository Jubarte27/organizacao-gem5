#!/bin/bash
set -e

adjectives=("happy" "brave" "clever" "bright" "calm" "jolly" "kind" "silly" "witty" "cozy")
animals=("panda" "koala" "otter" "fox" "badger" "hedgehog" "dolphin" "penguin" "owl" "rabbit")

main() {
    set_log_depth 0
    ensure cd "$PROJECT_DIR"

    local build_dir="src/build"
    mkdir -p "$build_dir"

    local gem5=("${EXEC_PREFIX[@]}" "$EXEC")
    local compile_exec=("${EXEC_PREFIX[@]}" "$TARGET_DIR/compile.sh")

    python3 "$PROJECT_DIR/src/make_data.py" 8 10
    cp "$PROJECT_DIR/src/big_array.h" "$HOST_RUN_DIR/radix.big_array.h"
    "${compile_exec[@]}" "$TARGET_RUN_DIR"

    cp -r "$PROJECT_DIR/orgb_configs" "$HOST_RUN_DIR/orgb_configs"
    cp "$PROJECT_DIR/src/cha.c" "$HOST_RUN_DIR/cha.in"

    ensure cd "$HOST_RUN_DIR"
    "${gem5[@]}" --outdir=chud.m5out orgb_configs/simulate.py run-benchmark -c chud -o "100" 2>&1 | tee "chud.txt"
    "${gem5[@]}" --outdir=radix.m5out orgb_configs/simulate.py run-benchmark -c radix 2>&1 | tee "radix.txt"
    "${gem5[@]}" --outdir=cha.m5out orgb_configs/simulate.py run-benchmark -c cha 2>&1 | tee "cha.txt"
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

docker_exists() {
    {
        { docker image ls --filter reference="$IMAGE_NAME" --format "{{.Repository}}:{{.Tag}}" | grep --line-regexp -q "$IMAGE_NAME"; } > /dev/null 2>&1
    } && { run_docker [ -f "$DOCKER_GEM5" ]; }
}

set_env() {
    IMAGE_NAME=orgb:latest
    DOCKER_GEM5="/opt/gem5/build/X86/gem5.opt"
    VM_GEM5="/home/orgb/gem5/build/X86/gem5.opt"
    EXEC_PREFIX=()

    run_adj=${adjectives[$RANDOM % ${#adjectives[@]}]}
    run_anim=${animals[$RANDOM % ${#animals[@]}]}
    run_uuid=$(cat /proc/sys/kernel/random/uuid)

    RUN_DIR=".run/$run_adj-$run_anim-$run_uuid"
    HOST_RUN_DIR="$PROJECT_DIR/$RUN_DIR"
    mkdir -p "$RUN_DIR"
    echo i live on "$RUN_DIR"

    if [ -f "$VM_GEM5" ] ; then
        EXEC="$VM_GEM5"
        TARGET_DIR="$PROJECT_DIR"
        TARGET_RUN_DIR="$HOST_RUN_DIR"
    elif docker_exists; then
        EXEC="$DOCKER_GEM5"
        TARGET_DIR="/data"
        TARGET_RUN_DIR="/data/$RUN_DIR"
        EXEC_PREFIX+=("run_docker")
    else
        log_error "Couldn't find gem5.opt"
    fi
}

SCRIPT_DIR=$(dirname "$(readlink -e "${BASH_SOURCE[0]}")") && source "$SCRIPT_DIR/util.bash"
set_env
_setConfigArgs "$@"
main "$@"
