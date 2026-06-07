#!/bin/env bash

main() {
    set_log_depth 0

    run_docker gcc src/chud.c -lgmp -lm -static -o chud

    EXEC="$GEM_5_DIR/build/X86/gem5.opt"

    run_docker $EXEC orgb_configs/simulate.py run-benchmark -c chud 1000000 5

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

run_docker()        { docker run --rm -v "$PROJECT_DIR:/data" -w /data $IMAGE_NAME "${@}";}



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
