#ifndef ARRAY_H
#define ARRAY_H

#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include "bifurcation.h"

typedef struct {
    double *vals;
    size_t len;
} array;

static array linspace(double a, double b, int len) {
    double *arr = calloc(len, sizeof(double));

    double step = (b-a) / ((float)len);

    for (int i=0; i<len; i++) {
        arr[i] = a + i*step;
    }

    return (array){arr, len};
}

static array array_zeros(int len) {
    array out = {};
    out.vals = calloc(sizeof(double), len);
    out.len = len;
    return out;
}

// static array array_map(array in, partial_fn *f) {
//     array out = array_zeros(in.len);

//     for (int i=0; i<out.len; i++) {
//         out.vals[i] = f(in.vals[i]);
//     }
//     return out;
// }

static void print_array(array *a) {
    printf("len=%d\n", a->len);
    printf(" [ ");
    for (int i=0; i<a->len; i++) {
        printf("%f ", a->vals[i]);
    }
    printf("]\n");
}



#endif