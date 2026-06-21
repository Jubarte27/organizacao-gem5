#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "black.in.h"
// the builtins does not seem to work with gem5
double fast_exp(double x) {
    if (x > -1e-8 && x < 1e-8) return 1.0 + x;

    int k = (int)(x * 1.4426950408889634 + (x > 0 ? 0.5 : -0.5)); 
    double r = x - k * 0.6931471805599453; // ln(2)

    double r2 = r * r;
    double p = 1.0 + r + r2 * (0.5 + r * (0.16666666666 + r * (0.04166666666 + r * 0.00833333333)));

    union {
        double d;
        uint64_t i;
    } bit_hack;
    
    bit_hack.d = p;
    bit_hack.i += ((uint64_t)k << 52); 
    
    return bit_hack.d;
}

double fast_erf(double x) {
    int sign = (x < 0) ? -1 : 1;
    x = (x < 0) ? -x : x;

    const double p  = 0.3275911;
    const double a1 = 0.254829592;
    const double a2 = -0.284496736;
    const double a3 = 1.421413741;
    const double a4 = -1.453152027;
    const double a5 = 1.061405429;

    double t = 1.0 / (1.0 + p * x);

    double poly = t * (a1 + t * (a2 + t * (a3 + t * (a4 + t * a5))));

    double result = 1.0 - poly * fast_exp(-x * x);

    return sign * result;
}

double fast_log(double x) {
    // Don do that, i'll trust you
    // if (x <= 0.0) return 0.0 / 0.0; // Return NaN for invalid inputs

    union {
        double d;
        uint64_t i;
    } bit_hack;

    bit_hack.d = x;

    int E = ((bit_hack.i >> 52) & 0x7FF) - 1023;

    bit_hack.i = (bit_hack.i & 0x000FFFFFFFFFFFFFULL) | 0x3FF0000000000000ULL;
    double m = bit_hack.d;

    double f = m - 1.0;

    double f2 = f * f;
    double p = f - f2 * (0.5 - f * (0.33333333333 - f * (0.25 - f * 0.2)));

    return E * 0.6931471805599453 + p;
}

double normal_cdf(double x) { return 0.5 * (1.0 + erf(x / sqrt(2.0))); }

void black_scholes(double S, double K, double T, double r, double v,
                   double* restrict call_price, double* restrict put_price) {

  double d1 = (log(S / K) + (r + (v * v) * 0.5) * T) / (v * sqrt(T));

  double d2 = d1 - v * sqrt(T);

  double discount = exp(-r * T);

  *call_price = S * normal_cdf(d1) - K * discount * normal_cdf(d2);
  *put_price = K * discount * normal_cdf(-d2) - S * normal_cdf(-d1);
}

int main() {
  const double K = 100.0;
  const double T = 0.5;
  const double r = 0.05;
  const double v = 0.20;
  double call_price;
  double put_price;

  const double * end = input + input_len;
  for (const double *p = input; p < end; p++) {
    black_scholes(*p, K, T, r, v, &call_price, &put_price);
  }
  printf("last: %lf, %lf", call_price, put_price);
  return 0;
}