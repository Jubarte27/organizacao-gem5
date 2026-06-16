#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <gmp.h>

void chud(uint64_t digits) {
    mp_bitcnt_t bits = (digits) * ceil(log2(10)) + 5;
    uint64_t iterations = digits / 14 + 1;

    mpf_t P, sum, k6, abk;  // accumulators
    mpf_t x, y;             // auxiliary
    mpf_init2(P, bits);
    mpf_init2(sum, bits);
    mpf_init2(k6, bits);
    mpf_init2(abk, bits);

    mpf_init2(x, bits);
    mpf_init2(y, bits);

    uint64_t A = 13591409;
    uint64_t B = 545140134;
    uint64_t C = 262537412640768000; // 640320^3

    mpf_set_ui(sum, A);
    mpf_set_ui(P, 1);
    mpf_set_ui(k6, 6);
    mpf_set_ui(abk, A + B);

    for (uint64_t k = 1; k <= (uint64_t)iterations; k++) {
        //y = 6k-1
        mpf_set(y, k6);
        mpf_sub_ui(y, y, 1);

        //x = 6k-5
        mpf_set(x, k6);
        mpf_sub_ui(x, x, 5);

        //y = (6k-1) * (6k-5)
        mpf_mul(y, y, x);

        //x = (2*k-1) * 24
        mpf_set(x, k6);
        mpf_mul_ui(x, x, 8);
        mpf_sub_ui(x, x, 24);

        // P *= 24 * (6 * k - 5) * (2 * k - 1) * (6 * k - 1)
        mpf_mul(y, y, x);
        mpf_mul(P, P, y);

        // den = k * k * k (hehe)
        mpf_set_ui(y, k);
        mpf_pow_ui(y, y, 3);

        // P = P / (C * (k^3)
        mpf_mul_ui(x, y, C);
        mpf_div(P, P, x);

        // Apply alternating sign: (-1)^k
        mpf_neg(P, P);

        // accumulate
        mpf_mul(x, P, abk);
        mpf_add(sum, sum, x);
        mpf_add_ui(k6, k6, 6);
        mpf_add_ui(abk, abk, B);
    }

    // y = constant = sqrt(10005) / 4270934400
    mpf_sqrt_ui(y, 10005);
    mpf_set_ui(x, 4270934400);
    mpf_div(y, y, x);

    // sum = pi = 1 / (sum * constant)
    mpf_mul(sum, sum, y);
    mpf_ui_div(x, 1, sum);

    // Desgraça arredonda, não sei
    char* pi_str = malloc(digits + 5);
    gmp_snprintf(pi_str, digits + 5, "%.*Ff", digits + 1, x);
    printf("pi: %s\n", pi_str);
    free(pi_str);

    mpf_clears(x, y, k6, abk, P, sum, NULL);
}

int main(int argc, char** argv) {
    int digits = argc > 1 ? atoi(argv[1]) : 1000;
    chud(digits);
    return 0;
}