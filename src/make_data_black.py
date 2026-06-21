import random
import sys
from pathlib import Path
import struct
from math import floor
import numpy as np

num_steps = int(sys.argv[1]) if len(sys.argv) > 1 else 100
num_steps -= 1
if len(sys.argv) > 2:
    target = sys.argv[2]
else:
    target = Path(__file__).resolve().parent.joinpath("black.in.h").as_posix()

def generate_gbm_stock_prices(S0: float = 100.0, mu: float = 0.05, sigma: float = 0.20, T: float = 0.5) -> list:
    dt = T / num_steps
    drift = (mu - 0.5 * sigma**2) * dt
    shocks = sigma * np.random.normal(0, np.sqrt(dt), num_steps)
    increments = np.exp(drift + shocks)
    prices = [S0]
    for inc in increments:
        prices.append(round(prices[-1] * inc, 2))
    return prices

doubles = generate_gbm_stock_prices()

stride = 4

def float2hex(x: float):
    return f"{x.hex()}"


def hex_line(start):
    return ", ".join(map(float2hex, doubles[start : start + stride]))


def lines():
    return f",\n  ".join(map(hex_line, range(0, len(doubles), stride)))


with open(target, "w") as f:
    print(f"""\
#ifndef __BLACK_IN_H__
#define __BLACK_IN_H__

static const double input[] = {{
  {lines()}
}};

const unsigned int input_len = {len(doubles)};

#endif // __BLACK_IN_H__
""", file=f, end="")
