#!/bin/sh
rm -fr src/build && mkdir -p src/build
cd src/build && cmake -DRUN_DIR="$1" .. && cmake --build .
