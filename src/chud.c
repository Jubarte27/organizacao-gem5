#include "chud.h"

# define omp_get_thread_num()  0
# define omp_get_num_threads() 1
# define omp_get_num_procs()   1

char   *prog_name;
double bs1_time=0.0, bs2_time=0.0, div_time=0.0;
double total_cputime = 0.0, total_wallclock = 0.0;

mpz_t  *pstack, *qstack, *gstack;

#define pi pstack[i]
#define qi qstack[i]
#define gi gstack[i]
#define pk pstack[k]
#define qk qstack[k]
#define gk gstack[k]

void sum (uint_t i, uint_t k, int gflag)
{
  double t = wall_clock();

  mpz_mul(qk, qk, gi);

  if (gflag)
    mpz_mul(gi, gi, gk);

  mpz_clear(gk);

  mpz_mul(qi, qi, pk);
  mpz_add(qi, qi, qk);
  mpz_clear(qk);

  mpz_mul(pi, pi, pk);
  mpz_clear(pk);

  bs2_time += wall_clock()-t;
}

void bs_init (uint_t a, uint_t b, uint_t terms, uint_t level, uint_t i, uint_t depth)
{
  fac_t fp1, fg1, ftmp, fmul; mpz_t gcd;
  uint_t j;

  fac_init(fp1), fac_init(ftmp), mpz_init(gcd);
  fac_init(fg1), fac_init(fmul);

  tmp_t *tmp = (tmp_t *) malloc(sizeof(tmp_t) * (depth - 1));

  for (j = 0; j < depth - 1; j++) {
    mpz_init(tmp[j].p),  mpz_init(tmp[j].q),  mpz_init(tmp[j].g);
    fac_init(tmp[j].fp), fac_init(tmp[j].fg), tmp[j].cleared = 0;
  }

  bs(pi, qi, gi, fp1, fg1, a, b, terms, level, gcd, ftmp, fmul, tmp, 0, 1);

  for (j = 0; j < depth - 1; j++) {
    if (!tmp[j].cleared) {
      mpz_clear(tmp[j].p),  mpz_clear(tmp[j].q),  mpz_clear(tmp[j].g);
      fac_clear(tmp[j].fp), fac_clear(tmp[j].fg);
    }
  }

  free(tmp);

  fac_clear(fp1), fac_clear(ftmp), mpz_clear(gcd);
  fac_clear(fg1), fac_clear(fmul);
}

void display_time (char *desc, double cputime, double wallclock)
{
  if (cputime < wallclock)
    cputime = wallclock;

  if (cputime > 0.0 && wallclock > 0.0) {
    fprintf(stderr,
      "  %-8s  cputime = %9.2fs  wallclock = %8.2fs  factor = %5.1f\n",
      desc, cputime, wallclock, cputime / wallclock);

  } else {
    cputime = wallclock = (cputime > 0.0) ? cputime : 0.0;

    fprintf(stderr,
      "  %-8s  cputime = %9.2fs  wallclock = %8.2fs  factor = %5.1f\n",
      desc, cputime, wallclock, 1.0);
  }

  if (strncmp(desc, "total", 5) == 0) {
    fprintf(stderr, "%21s %9.2fm %12s %8.2fm\n",
      "", cputime / 60.0, "", wallclock / 60.0);
  } else {
    total_cputime += cputime;
    total_wallclock += wallclock;
  }

  fflush(stderr);
}

#undef pi
#undef qi
#undef gi

int main (int argc, char *argv[])
{
  mpf_t pi, qi, ci;

  uint64_t digits=100;
  int      out=0, threads=1, ncpus=omp_get_num_procs(), nthrs;
  uint_t   terms, i, k, mid, depth, cores_depth, cores_size;
  uint_t   psize, qsize;
  double   wbegin, wend;

  time_t now; struct tm *localtm;


  prog_name = argv[0];

  if (argc == 1) {
    fprintf(stderr,"\n");
    fprintf(stderr,"SYNOPSIS\n");
    fprintf(stderr,"    %s <digits> [ <option> <threads> ]\n", prog_name);
    fprintf(stderr,"\n");
    fprintf(stderr,"    <digits>  digits of Pi to output\n");
    fprintf(stderr,"\n");
    fprintf(stderr,"    <option>  0 - just run (default)\n");
    fprintf(stderr,"              1 - output digits only\n");
    fprintf(stderr,"              2 - output digits (2 columns)\n");
    fprintf(stderr,"              3 - output digits (3 columns)\n");
    fprintf(stderr,"              N - output digits (N columns, max 14)\n");
    fprintf(stderr,"\n");
    fprintf(stderr,"    <threads> number of threads (default 1)\n");
    fprintf(stderr,"              specify 'auto' to run on all cores\n");
    fprintf(stderr,"\n");
    fprintf(stderr,"EXAMPLES\n");
    fprintf(stderr,"    %s 10000000 1 auto | md5sum\n", prog_name);
    fprintf(stderr,"        bc3234ae2e3f6ec7737f037b375eabec  -\n");
    fprintf(stderr,"\n");
    fprintf(stderr,"    %s 100000000 1 auto | md5sum\n", prog_name);
    fprintf(stderr,"        969bfe295b67da45b68086eb05a8b031  -\n");
    fprintf(stderr,"\n");
    fprintf(stderr,"    %s 100000000 5 auto > pi.txt\n", prog_name);
    fprintf(stderr,"\n");

    exit(1);
  }

  if (argc > 1)
    digits = strtoull(argv[1], NULL, 10);
  if (argc > 2)
    out = atoi(argv[2]);
  if (argc > 3)
    threads = (strncmp(argv[3], "auto", 4) == 0) ? ncpus : atoi(argv[3]);

  if (digits > MAX_DIGITS) {
    fprintf(stderr,"Number of digits reset from %s to %llu\n",
      argv[1], (unsigned long long) MAX_DIGITS);
    digits = MAX_DIGITS;
  }

  terms = digits/DIGITS_PER_ITER;

  if (threads < 1 || (terms <= 0 && threads > 1)) {
    fprintf(stderr,"Number of threads reset from %d to 1\n", threads);
    threads = 1;
  }
  else if (terms > 0 && terms < threads && threads <= ncpus) {
    fprintf(stderr,"Number of threads reset from %d to %lu\n",
      threads, (unsigned long) terms);
    threads = terms;
  }
  else if (threads > ncpus) {
    fprintf(stderr,"Number of threads reset from %d to %d\n", threads, ncpus);
    threads = ncpus;
  }

  cores_depth = 0; while ((1L << cores_depth) < threads) cores_depth++;
  depth       = 0; while ((1L << depth) < terms) depth++;

  cores_size  = pow(2, cores_depth);
  depth++;

  now = time(0), localtm = localtime(&now);

  fprintf(stderr,"# start date = %s", asctime(localtm));
  fprintf(stderr,"# terms = %lu, depth = %lu, threads = %d, logical cores = %d\n",
    (unsigned long) terms, (unsigned long) depth, threads, ncpus);

  /* allocate sieve */
  wbegin = wall_clock();

  if (terms > 0) {
    sieve_size = max(3*5*23*29+1, terms*6);
    sieve = (sieve_t *) malloc(sizeof(sieve_t)*sieve_size/2);
    build_sieve(sieve_size, sieve);
  }

  wend = wall_clock();
  display_time("sieve", wend-wbegin, wend-wbegin);
  wbegin = wall_clock();

  /* allocate stacks */
  pstack = malloc(sizeof(mpz_t)*threads);
  qstack = malloc(sizeof(mpz_t)*threads);
  gstack = malloc(sizeof(mpz_t)*threads);

  mpz_init(pstack[0]);
  mpz_init(qstack[0]);
  mpz_init(gstack[0]);

  /* begin binary splitting process */
  if (terms <= 0) {
    mpz_set_ui(pstack[0],1);
    mpz_set_ui(qstack[0],0);
    mpz_set_ui(gstack[0],1);

    wend = wall_clock();
    display_time("bs", wend-wbegin, wend-wbegin);
    wbegin = wall_clock();

    display_time("sum", 0.0, 0.0);

  } else {
    mid = terms / threads; 

    for (i = 1; i < threads; i++) {
      mpz_init(pstack[i]);
      mpz_init(qstack[i]);
      mpz_init(gstack[i]);
    }

    nthrs = (threads < ncpus) ? threads : ncpus;

    for (i = 0; i < threads; i++) {
      double t = wall_clock();

      if (i < (threads-1))
        bs_init(i*mid, (i+1)*mid, terms, cores_depth, i, depth);
      else
        bs_init(i*mid, terms, terms, cores_depth, i, depth);

      bs1_time += wall_clock()-t;
    }

    /* important, free sieve before computing sum */
    free(sieve);

    wend = wall_clock();
    display_time("bs", bs1_time, wend-wbegin);
    wbegin = wall_clock();


    for (k = 1; k < cores_size; k *= 2) {
      for (i = 0; i < threads; i = i+2*k) {
        if (i+k < threads) {
          int gflag = (i+2*k < threads) ? 1 : 0;
          sum(i, i+k, gflag);
        }
      }
    }

    wend = wall_clock();
    display_time("sum", bs2_time, wend-wbegin);
  }

  mpz_clear(gstack[0]); free(gstack);

  /* prepare to convert integers to floats */
  mpf_set_default_prec((mp_bitcnt_t)(digits * BITS_PER_DIGIT + 16));

  /*
	  p*(C/D)*sqrt(C)
    pi = -----------------
	     (q+A*p)
  */
  psize = mpz_sizeinbase(pstack[0],10);
  qsize = mpz_sizeinbase(qstack[0],10);

  mpz_addmul_ui(qstack[0], pstack[0], A);
  mpz_mul_ui(pstack[0], pstack[0], C/D);

  mpf_init(pi), mpf_set_z(pi, pstack[0]);
  mpz_clear(pstack[0]);
  free(pstack);

  mpf_init(qi), mpf_set_z(qi, qstack[0]);
  mpz_clear(qstack[0]);
  free(qstack);

  /* final step */

  wbegin = wall_clock();
  nthrs = (threads > 1) ? 2 : 1;


    int tid = omp_get_thread_num();

    if (tid == 0) {
      double t = wall_clock();
      my_div(qi, pi, qi);
      mpf_clear(pi);
      div_time += wall_clock()-t;
    }
    if (tid == 1 || omp_get_num_threads() < 2) {
      double t = wall_clock();
      mpf_init(ci);
      my_sqrt_ui(ci, C);
      div_time += wall_clock()-t;
    }


  wend = wall_clock();
  display_time("div/sqrt", div_time, wend-wbegin);
  wbegin = wall_clock();

  mpf_mul(qi, qi, ci);
  mpf_clear(ci);

  wend = wall_clock();
  display_time("mul", wend-wbegin, wend-wbegin);
  display_time("total", total_cputime, total_wallclock);

  fprintf(stderr,
    "# P size = %llu digits (%f)\n"
    "# Q size = %llu digits (%f)\n",
    (unsigned long long) psize, (double) psize/digits,
    (unsigned long long) qsize, (double) qsize/digits);

  now = time(0), localtm = localtime(&now);

  fprintf(stderr,"#   end date = %s\n", asctime(localtm));
  fflush(stderr);

  /* output Pi */

  if (out == 1) {
    mp_exp_t exp = 0; int i;
    char *str = malloc(digits+16+2);

    mpf_get_str(&(str[1]), &exp, 10, digits+16, qi);
    for (i = 0; i < exp; i++) str[i] = str[i+1];

    str[exp] = '.', str[digits+2] = 0;
    fwrite(str, sizeof(char), digits+2, stdout), fflush(stdout);
    fprintf(stderr, "\n"), fflush(stderr);

    free((void *) str);
  }
  else if (out >= 2 && out <= 14) {
    output_digits(qi, digits, out);
  }

  mpf_clear(qi);
  exit (0);
}
