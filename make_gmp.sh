#!/bin/bash
set -e

IMAGE_NAME=orgb:latest
run_docker()        { docker run --rm -v "$(pwd):/data" -w /data $IMAGE_NAME "${@}"; }

cd gem5/gmp/
./.bootstrap
./configure --prefix="$(realpath "../../src/ext")" --disable-assembly --disable-shared
make -j 4
make -j 4 install