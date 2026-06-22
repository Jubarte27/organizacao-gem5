#!/bin/bash
set -e
shopt -s nullglob
SCRIPT_DIR=$(dirname "$(readlink -e "${BASH_SOURCE[0]}")") && source "$SCRIPT_DIR/util.bash"
source "$SCRIPT_DIR/run.bash"

main() {
    set_log_depth 0
    local algorithms=(cha chud radix)

    mkdir -p "$RUN_DIR"
    mkdir -p "$RUN_DIR/build"
    for algo in "${algorithms[@]}"; do prepare "$algo"; done
    run_on_target "$TARGET_DIR/compile.sh" "$TARGET_DIR/$(realpath --relative-to="$PROJECT_DIR" "$RUN_DIR/build")"

    for dir in "$CPUS_DIR"/CPU*/; do
        current_run_dir="$RUN_DIR/$(basename "$dir")"
        
        mkdir -p "$current_run_dir"

        cp -r "$RUN_DIR/build/." "$current_run_dir/"
        cp -r "$HOST_DIR/orgb_configs_orig" "$current_run_dir/orgb_configs_orig"

        cp "$dir/CPUBase.py" "$current_run_dir/orgb_configs_orig/systems/cpus/CPUBase.py"
        cp "$dir/basic_caches.py" "$current_run_dir/orgb_configs_orig/systems/caches/basic_caches.py"

        run "$(realpath --relative-to="$PROJECT_DIR" "$current_run_dir")"
    done

    echo "wating..."
    if ! wait; then
        echo "Error: One or more child processes failed!"
        exit 1
    fi
    echo "done."

    # run_on_target chown -R
}

run_algo() {
    local algo=$1
    local relative_dir=$2

    echo "starting $algo on $relative_dir"
    local cmd
    algorithm_cmd cmd "$algo" "$TARGET_DIR/$relative_dir"

    gem5 --outdir="$TARGET_DIR/$relative_dir/$algo.m5out" "$relative_dir/orgb_configs_orig/simulate.py" --cpu "CPUBase" run-benchmark -c "${cmd[@]}" > "$PROJECT_DIR/$relative_dir/$algo.txt" 2>&1
    echo "finished $algo on $dir"
}

run() {
    local relative_dir=$1
    for algo in radix chud cha; do
        run_algo "$algo" "$relative_dir" &
    done
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
    CPUS_DIR=$1
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

set_env() {
    IMAGE_NAME=orgb:latest
    DOCKER_GEM5="/opt/gem5/build/X86/gem5.opt"
    VM_GEM5="/home/orgb/gem5/build/X86/gem5.opt"

    RUN_DIR="$CPUS_DIR/run"
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

_setConfigArgs "$@"
set_env
main "$@"
