#!/bin/env bash

gem5 () {
    EXEC="$GEM_5_DIR/build/ALL/gem5.opt"
    ensure $EXEC "$@"
}

main() {
    set_log_depth 0

    GEM_5_DIR="$PROJECT_DIR/gem5"
    VENV_DIR="$PROJECT_DIR/.venv"
    MAX_THREAD="$(nproc --ignore 2)"

    # shellcheck source=../.venv/bin/activate
    source "$VENV_DIR/bin/activate"

    ensure cd "$GEM_5_DIR"
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


set_env() {
    :
}

PROJECT_DIR=..
SCRIPT_DIR=$(dirname "$(readlink -e "${BASH_SOURCE[0]}")") && source "$SCRIPT_DIR/util.bash"
set_env
_setConfigArgs "$@"
main "$@"
