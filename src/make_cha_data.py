import random
import sys
from pathlib import Path

if len(sys.argv) > 1:
    big_array_path = sys.argv[1]
else:
    big_array_path = Path(__file__).resolve().parent.joinpath("cha.in.h").as_posix()

with open(Path(__file__).resolve().parent.joinpath(sys.argv[2] if len(sys.argv) > 2 else "beemovie.fodase").as_posix(), "rb") as file:
    cha_bytes = file.read()

stride = 16


def int2hex(x: int):
    return f"0x{x:02X}"


def hex_line(start):
    return ", ".join(map(int2hex, cha_bytes[start : start + stride]))


def lines():
    return f",\n  ".join(map(hex_line, range(0, len(cha_bytes), stride)))


with open(big_array_path, "w") as f:
    print(f"""\
#ifndef __CHA_IN_H__
#define __CHA_IN_H__

static unsigned char cha_input[] = {{
  {lines()}
}};

unsigned int cha_input_len = {len(cha_bytes)};

#endif // __CHA_IN_H__
""", file=f, end="")
