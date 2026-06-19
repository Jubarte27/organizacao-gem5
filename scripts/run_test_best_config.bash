#!/bin/bash
set -e
shopt -s nullglob

main() {
    set_log_depth 0
    local algorithms=(cha chud radix)

    RUNS_ROOT="$CPUS_DIR/run"
    mkdir -p "$RUNS_ROOT"
    mkdir -p "$RUNS_ROOT/build"
    run_on_target "$TARGET_DIR/compile.sh" "$TARGET_DIR/$(realpath --relative-to="$PROJECT_DIR" "$RUNS_ROOT/build")"

    for dir in "$CPUS_DIR"/CPU*/; do
        current_run_dir="$RUNS_ROOT/$(basename "$dir")"
        
        mkdir -p "$current_run_dir"

        cp -r "$RUNS_ROOT/build/." "$current_run_dir/"
        cp -r "$HOST_DIR/orgb_configs" "$current_run_dir/orgb_configs"

        cp "$dir/CPUBase.py" "$current_run_dir/orgb_configs/systems/cpus/CPUBase.py"
        cp "$dir/basic_caches.py" "$current_run_dir/orgb_configs/systems/caches/basic_caches.py"

        for algo in "${algorithms[@]}"; do prepare "$algo"; done

        run "$(realpath --relative-to="$PROJECT_DIR" "$current_run_dir")" &
    done

    echo "wating..."
    if ! wait; then
        echo "Error: One or more child processes failed!"
        exit 1
    fi
    echo "done."
}

run() {
    local relative_dir=$1
    for algo in radix chud cha; do
        echo "starting $algo on $relative_dir"
        local cmd
        algorithm_cmd cmd "$algo" "$TARGET_DIR/$relative_dir"

        gem5 --outdir="$TARGET_DIR/$relative_dir/$algo.m5out" "$relative_dir/orgb_configs/simulate.py" --cpu "CPUBase" run-benchmark -c "${cmd[@]}" > "$PROJECT_DIR/$relative_dir/$algo.txt" 2>&1
        echo "finished $algo on $dir"
    done
}

gem5() {
    local exec;
    case "$RUN_METHOD" in
        vm)     exec=$VM_GEM5 ;;
        docker) exec=$DOCKER_GEM5 ;;
        *)      log_error "Run set_env before calling me" ;;
    esac
    ensure cd "$PROJECT_DIR"
    run_on_target $exec "$@"
}

run_on_target() {
    case "$RUN_METHOD" in
        vm)     if ! "$@"; then exit 1; fi ;;
        docker) if ! run_docker "$@"; then exit 1; fi ;;
        *)      log_error "Run set_env before calling me" ;;
    esac
}

algorithm_cmd() {
    local -n _cmd=$1
    case "$2" in
        cha)   _cmd=("${3:-$TARGET_RUN_DIR}/cha") ;;
        chud)  _cmd=("${3:-$TARGET_RUN_DIR}/chud" -o "100") ;;
        radix) _cmd=("${3:-$TARGET_RUN_DIR}/radix") ;;
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
    CPUS_DIR=$1
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
