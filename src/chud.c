#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <gmp.h>

#define mp_init(type, args...) mp##type##_t args; mp##type##_inits(args, NULL)

void chud(int digits) {
    unsigned int bits = digits * log2(10) + 5;
    mpf_t pi, temp, constant;
    mpf_init2(pi, bits);
    mpf_init2(temp, bits);
    mpf_init2(constant, bits);
    mp_init(z, fac6, fac3, fac, top, bottom);
    mp_init(q, term);

    int iterations = digits / 14;

    mpf_sqrt_ui(constant, 10005);
    mpf_div_ui(constant, constant, 4270934400);


    for (int k = 0; k < iterations; k++) {
        mpz_fac_ui(fac6, 6*k);
        mpz_fac_ui(fac3, 3*k);

        mpz_fac_ui(fac, k);
        mpz_pow_ui(fac, fac, 3);

        mpz_set_ui(top, 545140134);
        mpz_mul_ui(top, top, k);
        mpz_add_ui(top, top, 13591409);

        mpz_mul(top, top, fac6);

        mpz_ui_pow_ui(bottom, 640320, 3*k);
        mpz_mul(bottom, bottom, fac3);
        mpz_mul(bottom, bottom, fac);

        mpq_set_num(term, top);
        mpq_set_den(term, bottom);

        mpf_set_q(temp, term);

        if (k % 2 == 0) {
            mpf_add(pi, pi, temp);
        } else {
            mpf_sub(pi, pi, temp);
        }
    }

    mpf_mul(pi, pi, constant);
    mpf_ui_div(pi, 1, pi);

    gmp_printf("pi: %.*Ff\n", digits, pi);

    mpf_clears(pi, temp, constant, NULL);
    mpz_clears(fac6, fac3, fac, top, bottom, NULL);
    mpq_clears(term, NULL);

}


int main(int argc, char** argv) {
    int digits = argc > 1 ? atoi(argv[1]) : 1000;
    chud(digits);
    return 0;
}