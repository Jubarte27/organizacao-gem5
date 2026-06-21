cmake_minimum_required(VERSION 3.5)
set(CMAKE_C_COMPILER gcc)

project(PerformanceBenchmarks C)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O0 -mfpmath=sse -msse2 -funroll-loops")
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0 -mfpmath=sse -msse2")
# Ensure standard C configuration
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# 1. Handle the output directory ($run_dir)
if(NOT RUN_DIR)
    set(RUN_DIR "${CMAKE_BINARY_DIR}/run_dir")
endif()

# Setting this globally ensures BOTH executables drop into $run_dir
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${RUN_DIR}")

link_directories("${CMAKE_CURRENT_SOURCE_DIR}/ext/lib")
# deveria ser CMAKE_CURRENT_SOURCE_DIR ao inves de CMAKE_RUNTIME_OUTPUT_DIRECTORY, mas fica mais fácil de testar assim
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/ext/include" "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")

add_executable(radix radix.c)
set_target_properties(radix PROPERTIES LINK_FLAGS "-static")

add_executable(black black.c)
target_link_libraries(black PRIVATE m)
set_target_properties(radix PROPERTIES LINK_FLAGS "-static")

add_executable(chud chud.c)
target_link_libraries(chud PRIVATE gmp)
set_target_properties(chud PROPERTIES LINK_FLAGS "-static")

file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/beemovie.fodase" DESTINATION "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")
file(RENAME "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/beemovie.fodase" "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/cha.in")
file(COPY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/cha.in" DESTINATION "${CMAKE_CURRENT_BINARY_DIR}")

add_executable(cha cha.c)
set_target_properties(cha PROPERTIES LINK_FLAGS "-static")