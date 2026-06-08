#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "big_array.h"

#define radix 10
#define arr big_array
#define n big_array_len
#define n_byte n * sizeof(int)

#define swap(a, b) do {__typeof__(a) _tmp = (a); a = b; b = _tmp;} while (0)

void counting_sort_by_digit(const int* src, int* dst, int exp);
void radix_sort();
int get_max();

int main() {
    radix_sort();
    FILE *f = NULL;
    f = fopen("radix.out", "w");
    for (int i = 0; i < n; i++) {
        fprintf(f, "%s%d", i==0?"":" ", arr[i]);
    }
    fprintf(f, "\n");

    return EXIT_SUCCESS;
}

void radix_sort() {
    int max = get_max();

    int* src = arr;
    int* dst_ = (int*)malloc(n_byte);
    int* dst = dst_;

    if (dst == NULL) {
        fprintf(stderr, "Unsuccessful memory allocation");
        exit(42);
    }

    for (int exp = 1; max / exp > 0; exp *= radix) {
        counting_sort_by_digit(src, dst, exp);
        swap(src, dst);
    }

    for (int i = 0; i < n; i++) {
        arr[i] = src[i];
    }

    free(dst_);
}

#define digit ((src[i] / exp) % radix)
void counting_sort_by_digit(const int* src, int* dst, int exp) {
    int count[radix] = { 0 };

    for (int i = 0; i < n; i++) {
        count[digit]++;
    }

    for (int i = 1; i < radix; i++) {
        count[i] += count[i - 1];
    }

    for (int i = n - 1; i >= 0; i--) {
        dst[--count[digit]] = src[i];
    }
}
int get_max() {
    int max = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > max) {
            max = arr[i];
        }
    }
    return max;
}
