#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <gmp.h>
#include <stdint.h>

void chud(int digits) {
    int N = (digits * 3.321928) / 64 + 3; // conta de padeiro, funciona pra poucos (3mi) digitos

    mp_limb_t P[N];
    mp_limb_t sum[N];
    mp_limb_t term[N];

    for (int i = 0; i < N - 1; i++) {P[i] = 0; sum[i] = 0;}

    P[N - 1] = 1;
    sum[N - 1] = 13591409;

    uint64_t iterations = digits / 14 + 1;
    for (uint64_t k = 1; k <= iterations; k++) {
        // everything fits in uint64_t as long as k < 219,000 (+-)
        uint64_t num = 24 * (6 * k - 5) * (2 * k - 1) * (6 * k - 1);
        uint64_t hehe = k * k * k;
        uint64_t C = 262537412640768000; // 640320^3
        uint64_t term_mult = 13591409 + 545140134 * k;

        mpn_mul_1(P, P, N, num);            // 1. P = P * num
        mpn_divrem_1(term, 0, P, N, hehe);  // 2. term = P / hehe
        mpn_divrem_1(P, 0, term, N, C);     // 3. P = term / C
        mpn_mul_1(term, P, N, term_mult);   // 4. term = P * term_mult

        if (k % 2 == 0) {
            mpn_add_n(sum, sum, term, N);
        } else {
            mpn_sub_n(sum, sum, term, N);
        }
    }

    mpz_t z_sum;
    mpz_roinit_n(z_sum, sum, N); // Bind the stack array to an mpz safely

    unsigned int bits = digits * log2(10) + 5;
    mpf_t f_sum, pi, constant;
    mpf_init2(f_sum, bits);
    mpf_init2(pi, bits);
    mpf_init2(constant, bits);

    mpf_set_z(f_sum, z_sum);
    mpf_div_2exp(f_sum, f_sum, 64 * (N - 1));

    mpf_sqrt_ui(constant, 10005);
    mpf_div_ui(constant, constant, 4270934400);

    mpf_mul(f_sum, f_sum, constant);
    mpf_ui_div(pi, 1, f_sum);

    gmp_printf("pi: %.*Ff\n", digits, pi);

    mpf_clears(f_sum, pi, constant, NULL);
}


int main(int argc, char** argv) {
    int digits = argc > 1 ? atoi(argv[1]) : 1000;
    chud(digits);
    return 0;
}