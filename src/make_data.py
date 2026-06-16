import random
import sys
from pathlib import Path

if len(sys.argv) > 3:
    big_array_path = sys.argv[3]
else:
    big_array_path = Path(__file__).resolve().parent.joinpath("big_array.h").as_posix()

max_int = 1 << (16 if len(sys.argv) <= 1 else int(sys.argv[1]))
n_bytes = 1 << (20 if len(sys.argv) <= 2 else int(sys.argv[2]))
ints = [random.randint(0, max_int) for _ in range(n_bytes >> 2)]

stride = 16


def int2hex(x: int):
    return f"0x{x:04X}"


def hex_line(start):
    return ", ".join(map(int2hex, ints[start : start + stride]))


def lines():
    return f",\n  ".join(map(hex_line, range(0, len(ints), stride)))


with open(big_array_path, "w") as f:
    print(f"""\
#ifndef __BIG_ARRAY_H__
#define __BIG_ARRAY_H__

static unsigned int big_array[] = {{
  {lines()}
}};

unsigned int big_array_len = {len(ints)};

#endif // __BIG_ARRAY_H__
""", file=f, end="")
