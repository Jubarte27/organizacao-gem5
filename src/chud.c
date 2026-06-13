#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <gmp.h>
#include <stdint.h>

// economiza 1 if por iteracao
// everything fits in uint64_t as long as k < 219,000 (+-)
#define gambiarra do { \
        uint64_t num = 24 * (6 * k - 5) * (2 * k - 1) * (6 * k - 1); \
        uint64_t hehe = k * k * k; \
        uint64_t C = 262537412640768000;\
        uint64_t term_mult = 13591409 + 545140134 * k; \
        mpn_mul_1(P, P, N, num); \
        mpn_divrem_1(term, 0, P, N, hehe); \
        mpn_divrem_1(P, 0, term, N, C); \
        mpn_mul_1(term, P, N, term_mult); \
    } while (0)


void chud(uint32_t digits) {
    float floaty_bits = digits * log2(10);
    uint32_t bits = floaty_bits + 5;
    int N = floaty_bits / 64 + 3;

    mp_limb_t P[N];
    mp_limb_t sum[N];
    mp_limb_t term[N];

    for (int i = 0; i < N - 1; i++) {P[i] = 0; sum[i] = 0;}

    P[N - 1] = 1;
    sum[N - 1] = 13591409;

    uint64_t iterations = digits / 14 + 1;
    for (uint64_t k = 1; k <= iterations; k++) {
        gambiarra;
        mpn_sub_n(sum, sum, term, N);

        k++;
        if (k > iterations) break; 

        gambiarra;
        mpn_add_n(sum, sum, term, N);
    }

    mpz_t z_sum;
    mpz_roinit_n(z_sum, sum, N);

    mpf_t f_sum;
    mpf_init2(f_sum, bits);
    mpf_set_z(f_sum, z_sum);
    mpf_div_2exp(f_sum, f_sum, 64 * (N - 1));

    mpf_t constant;
    mpf_init2(constant, bits);
    mpf_sqrt_ui(constant, 10005);
    mpf_div_ui(constant, constant, 4270934400);
    mpf_mul(f_sum, f_sum, constant);
    mpf_clear(constant);

    mpf_t pi;
    mpf_init2(pi, bits);
    mpf_ui_div(pi, 1, f_sum);
    mpf_clear(f_sum);

    //1 extra porque a desgraça me arredonda
    char pi_size = 1 + digits + sizeof("3."); // 3.{$digits}\0
    char pi_str[pi_size]; 
    gmp_snprintf(pi_str, pi_size, "%.*Ff", digits + 1, pi);
    mpf_clear(pi);

    pi_str[pi_size - 2] = '\0';
    printf("pi: %s\n", pi_str);
}


int main(int argc, char** argv) {
    int digits = argc > 1 ? atoi(argv[1]) : 1000;
    chud(digits);
    return 0;
}