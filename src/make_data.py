import random
import sys
from pathlib import Path
import struct

if len(sys.argv) > 3:
    target = sys.argv[3]
else:
    target = Path(__file__).resolve().parent.joinpath("big_array.h").as_posix()

max_int = 1 << (16 if len(sys.argv) <= 1 else int(sys.argv[1]))
n_bytes = 1 << (20 if len(sys.argv) <= 2 else int(sys.argv[2]))
ints = [random.randint(0, max_int) for _ in range(n_bytes >> 2)]

format_string = f"@{len(ints)}I" 
with open(f'{target.removesuffix(".h")}.bin', "wb") as f:
    f.write(struct.pack(format_string, *ints))

stride = 16

def int2hex(x: int):
    return f"0x{x:04X}"


def hex_line(start):
    return ", ".join(map(int2hex, ints[start : start + stride]))


def lines():
    return f",\n  ".join(map(hex_line, range(0, len(ints), stride)))


with open(target, "w") as f:
    print(f"""\
#ifndef __BIG_ARRAY_H__
#define __BIG_ARRAY_H__

static unsigned int big_array[] = {{
  {lines()}
}};

unsigned int big_array_len = {len(ints)};

#endif // __BIG_ARRAY_H__
""", file=f, end="")
