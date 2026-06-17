#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#include "big_array.h"

#define radix 10
#define arr big_array
#define n big_array_len
#define n_byte n * sizeof(int)

#define swap(a, b) do {__typeof__(a) _tmp = (a); a = b; b = _tmp;} while (0)

void counting_sort_by_digit(const unsigned int* src, unsigned int* dst, int exp);
void radix_sort();
int get_max();


void fast_print_ints(FILE *stream) {
    char buffer[4096];
    int pos = 0;

    for (size_t i = 0; i < n; i++) {
        if (pos > sizeof(buffer) - 16) { 
            fwrite(buffer, 1, pos, stream);
            pos = 0;
        }
        pos += snprintf(buffer + pos, sizeof(buffer) - pos, "%d ", arr[i]);
    }
    if (pos > 0) {
        fwrite(buffer, 1, pos, stream);
    }
    fputc('\n', stream);
}

int main() {
    radix_sort();
    // Write to a file only when we need to verify. Printing takes as much time as sorting, so it defeats the purpose of tests (we're not trying to test printf)
    // FILE *f = fopen("radix.out", "w");
    // fast_print_ints(f);
    // fclose(f);
    return EXIT_SUCCESS;
}

void radix_sort() {
    int max = get_max();

    unsigned int* src = arr;
    unsigned int* dst_ = (unsigned int*)malloc(n_byte);
    unsigned int* dst = dst_;

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
void counting_sort_by_digit(const unsigned int* src, unsigned int* dst, int exp) {
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
