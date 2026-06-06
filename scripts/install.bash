#!/bin/env bash

main() {
    set_log_depth 0

    if ! pyenv --version > /dev/null 2>&1 ; then log_error "no pyenv $?"; fi
    pyenv install --skip-existing 3.12
    pyenv local 3.12

    GEM_5_DIR="$PROJECT_DIR/gem5"
    VENV_DIR="$PROJECT_DIR/.venv"
    MAX_THREAD="$(nproc --ignore 2)"

    if ! [ -d "$VENV_DIR" ]; then python3 -m venv "$VENV_DIR"; fi
    if ! [ -d "$GEM_5_DIR" ]; then git clone https://github.com/gem5/gem5 "$GEM_5_DIR"; fi

    # shellcheck source=../.venv/bin/activate
    source "$VENV_DIR/bin/activate"
    pip install -r "$PROJECT_DIR/requirements.txt"

    ensure cd "$GEM_5_DIR"
    scons build/ALL/gem5.opt -j "$MAX_THREAD"
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
