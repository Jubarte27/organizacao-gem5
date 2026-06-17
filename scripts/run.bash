#!/bin/bash
set -e
shopt -s nullglob

main() {
    set_log_depth 0
    mkdir -p "$HOST_DIR/src/build"
    local algorithms=(cha chud radix)

    cp -r "$HOST_DIR/orgb_configs" "$HOST_RUN_DIR/orgb_configs"
    run_on_target "$TARGET_DIR/compile.sh" "$TARGET_RUN_DIR"

    for algo in "${algorithms[@]}"; do prepare "$algo"; done

    
    # for cpu in CPUBase; do
    for cpu in CPUBase CPUMoreMem CPUMoreFloat CPUBigROB; do
        mkdir -p "$HOST_RUN_DIR/$cpu"
        for algo in "${algorithms[@]}"; do
            run "$cpu" "$algo" &
        done
    done
    wait
    echo "done"

}

run() {
    local cpu=$1
    local algo=$2
    echo "starting $algo on $cpu"
    algorithm_cmd cmd "$algo"
    gem5 --outdir="$TARGET_RUN_DIR/$cpu/$algo.m5out" "$TARGET_RUN_DIR/orgb_configs/simulate.py" --cpu "$cpu" run-benchmark -c "${cmd[@]}" > "$HOST_RUN_DIR/$cpu/$algo.txt" 2>&1
    echo "finished $algo on $cpu"
}

gem5() {
    local exec;
    case "$RUN_METHOD" in
        vm)     exec=$VM_GEM5 ;;
        docker) exec=$DOCKER_GEM5 ;;
        *)      log_error "Run set_env before calling me" ;;
    esac
    run_on_target $exec "$@"
}

run_on_target() {
    case "$RUN_METHOD" in
        vm)     "$@" ;;
        docker) run_docker "$@" ;;
        *)      log_error "Run set_env before calling me" ;;
    esac
}

algorithm_cmd() {
    local -n _cmd=$1
    case "$2" in
        cha)   _cmd=("$TARGET_RUN_DIR/cha") ;;
        chud)  _cmd=("$TARGET_RUN_DIR/chud" -o "100") ;;
        radix) _cmd=("$TARGET_RUN_DIR/radix") ;;
        *)     log_error "Don't know $2" ;;
    esac
}

prepare() {
    case "$1" in
        cha)   ;;
        chud)  ;;
        radix) python3 "$HOST_DIR/src/make_data.py" 8 10 "$HOST_RUN_DIR/radix.big_array.h" ;;
        *)     log_error "Don't know $1" ;;
    esac
}

run_docker()        { docker run --rm -v "${DATA_DIR:-"$(pwd)"}:/data" -w /data $IMAGE_NAME "${@}"; }
run_docker_orgb()   { docker run --rm -v "${DATA_DIR:-"$(pwd)"}:/data" -w /data orgb:latest "${@}"; }


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
        {
            docker image ls --filter reference="$IMAGE_NAME" --format "{{.Repository}}:{{.Tag}}" | grep --line-regexp -q "$IMAGE_NAME"
        } > /dev/null 2>&1
    } && { run_docker [ -f "$DOCKER_GEM5" ]; }
}

set_env() {
    IMAGE_NAME=orgb:latest
    DOCKER_GEM5="/opt/gem5/build/X86/gem5.opt"
    VM_GEM5="/home/orgb/gem5/build/X86/gem5.opt"

    RUN_DIR="$(next_dir .run)"
    HOST_DIR=$PROJECT_DIR
    HOST_RUN_DIR="$HOST_DIR/$RUN_DIR"

    mkdir -p "$HOST_RUN_DIR"

    if [ -f "$VM_GEM5" ] ; then
        TARGET_DIR="$PROJECT_DIR"
        RUN_METHOD=vm
    elif docker_exists; then
        TARGET_DIR="/data"
        RUN_METHOD=docker
    else
        log_error "Couldn't find gem5.opt"
    fi
    TARGET_RUN_DIR="$TARGET_DIR/$RUN_DIR"
}



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

SCRIPT_DIR=$(dirname "$(readlink -e "${BASH_SOURCE[0]}")") && source "$SCRIPT_DIR/util.bash"
set_env
_setConfigArgs "$@"
main "$@"
