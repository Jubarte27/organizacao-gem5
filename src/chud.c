#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <gmp.h>
#include <stdint.h>


// funciona até uns k = 219 mil, depois disso tem que usar tudo em gmp mesmo 
void chud(uint32_t digits) {
    int N = ((digits * log2(10)) / 64) + 3;

    mp_limb_t P[N];
    mp_limb_t sum[N];
    mp_limb_t term[N];

    for (int i = 0; i < N - 1; i++) {P[i] = 0; sum[i] = 0;}

    P[N - 1] = 1;
    sum[N - 1] = 13591409;

    uint64_t iterations = digits / 14 + 1;
    for (uint64_t k = 1; k <= iterations; k++) {
        uint64_t num       = 24 * (6 * k - 5) * (2 * k - 1) * (6 * k - 1);
        uint64_t den1      = k * k * k;
        uint64_t C         = 262537412640768000; 
        uint64_t term_mult = 13591409 + 545140134 * k;

        mpn_mul_1(P, P, N, num);
        mpn_divrem_1(term, 0, P, N, den1);
        mpn_divrem_1(P, 0, term, N, C);
        mpn_mul_1(term, P, N, term_mult);

        if (k % 2 == 0) {
            mpn_add_n(sum, sum, term, N);
        } else {
            mpn_sub_n(sum, sum, term, N);
        }
    }
    
    mpz_t pi, z_sum, den;
    mpz_inits(pi, z_sum, den, NULL);

    mpz_set_ui(den, 10005);
    mpz_mul_2exp(den, den, 2 * 64 * N);
    mpz_sqrt(den, den); 

    mpz_roinit_n(z_sum, sum, N);
    mpz_mul(den, z_sum, den);


    mpz_set_ui(z_sum, 10);
    mpz_pow_ui(z_sum, z_sum, digits);
    mpz_mul_ui(z_sum, z_sum, 4270934400UL);
    mpz_mul_2exp(z_sum, z_sum, 64 * (2 * N - 1));

    mpz_tdiv_q(pi, z_sum, den);

    char *str = mpz_get_str(NULL, 10, pi);
    if (str) {
        printf("pi: %c.%s\n", str[0], str + 1);
        free(str);
    }

    mpz_clears(den, z_sum, pi, NULL);
}

int main(int argc, char** argv) {
    int digits = argc > 1 ? atoi(argv[1]) : 1000;
    chud(digits);
    return 0;
}