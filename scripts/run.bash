#!/bin/bash
set -e
shopt -s nullglob

main() {
    set_log_depth 0
    mkdir -p "$(host_dir src/build)"
    local algorithms=(chud)

    local gem5=("${EXEC_PREFIX[@]}" "$EXEC")
    local compile_exec=("${EXEC_PREFIX[@]}" "$(target_dir compile.sh)")

    cp -r "$(host_dir orgb_configs)" "$(host_dir "$RUN_DIR/orgb_configs")"
    "${compile_exec[@]}" "$(target_dir "$RUN_DIR")"
    for algo in "${algorithms[@]}"; do "${algo}_prepare"; done


    # for cpu in CPUBase; do
    for cpu in CPUBase MyO3CPU; do
        ensure cd "$(host_dir)"
        local cpu_run_dir="$RUN_DIR/$cpu"
        mkdir -p "$(host_dir "$cpu_run_dir")"

        ensure cd "$(host_dir "$RUN_DIR")"
        for algo in "${algorithms[@]}"; do
            local -n cmd="${algo}_CMD"
            "${gem5[@]}" --outdir="$cpu/$algo.m5out" orgb_configs/simulate.py --cpu "$cpu" run-benchmark -c "${cmd[@]}" 2>&1 | tee "$cpu/$algo.txt"
        done
    done
}

cha_prepare()   { cp "$(host_dir src/cha.c)" "$(host_dir "$RUN_DIR/cha.in")"; }
chud_prepare()  { :; }
radix_prepare() { python3 "$(host_dir /src/make_data.py)" 8 10 "$(host_dir "$RUN_DIR/radix.big_array.h")"; }

build_if_not_exists() {
    if [[ "$(docker images -q "$1" 2> /dev/null)" == "" ]]; then
        echo "Image $1 does not exist. Building..."
        docker build --build-arg MAX_THREAD="$(nproc --ignore 2)" --force-rm --tag "$1" "$2"
    else
        echo "Image $1 already exists. Skipping build."
    fi
}

run_docker()        { docker run --rm -v "$(pwd):/data" -w /data $IMAGE_NAME "${@}"; }
run_docker_orgb()   { docker run --rm -v "$(pwd):/data" -w /data orgb:latest "${@}"; }


next_dir() {
    local PREFIX="run_"
    local TARGET_DIR="${1:-.}"

    local  max_num=0
    local  found_any=false

    for dir in "$TARGET_DIR"/"${PREFIX}"[0-9]*; do
        if [ -d "$dir" ]; then
            found_any=true
            local base_name;
            base_name=$(basename "$dir")
            
            local num="${base_name#"$PREFIX"}"
            
            if [[ "$num" =~ ^[0-9]+$ ]]; then
                local clean_num=$((10#$num))
                if ((clean_num > max_num)); then
                    max_num=$clean_num
                fi
            fi
        fi
    done

    if [ "$found_any" = false ] && [ ! -d "$TARGET_DIR/${PREFIX}0" ]; then
        next_num=1
    else
        next_num=$((max_num + 1))
    fi

    echo "${TARGET_DIR}/${PREFIX}${next_num}"
}

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

host_dir()   { echo "${PROJECT_DIR}${1+"/$1"}"; }
target_dir() { echo "${TARGET_DIR}${1+"/$1"}"; }

set_env() {
    IMAGE_NAME=orgb:latest
    DOCKER_GEM5="/opt/gem5/build/X86/gem5.opt"
    VM_GEM5="/home/orgb/gem5/build/X86/gem5.opt"
    EXEC_PREFIX=()

    RUN_DIR="$(next_dir .run)"
    mkdir -p "$RUN_DIR"
    echo i live on "$RUN_DIR"

    if [ -f "$VM_GEM5" ] ; then
        EXEC="$VM_GEM5"
        TARGET_DIR="$PROJECT_DIR"
    elif docker_exists; then
        EXEC="$DOCKER_GEM5"
        TARGET_DIR="/data"
        EXEC_PREFIX+=("run_docker")
    else
        log_error "Couldn't find gem5.opt"
    fi

    chud_CMD=(chud -o "100")
    radix_CMD=(radix)
    cha_CMD=("cha")
}

SCRIPT_DIR=$(dirname "$(readlink -e "${BASH_SOURCE[0]}")") && source "$SCRIPT_DIR/util.bash"
set_env
_setConfigArgs "$@"
main "$@"
