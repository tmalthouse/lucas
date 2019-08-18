#ifndef BIFURCATION_H
#define BIFURCATION_H
#include <math.h>



typedef struct {
    double x1;
    double x2;
    bool invalid;
} dpair;

typedef struct {
    double val;
    bool invalid;
} maybe_double;

typedef struct {
    double tau;
    double gamma;
    double w0;
    double ep;
    double THmax;
    double tau_sf;
    double r;
    double tau_c;
    double xi;
    double phi;
} params;

params default_params(void) {
    params ret = {};
    ret.tau = 0.01;
    ret.gamma = 1.01;
    ret.w0 = sqrt(3);
    ret.ep = 3;
    ret.THmax = 2*M_PI/ret.w0;
    ret.tau_sf = 1.084*2*M_PI/sqrt(3);
    ret.r = 0.25;
    ret.tau_c = ret.tau * ret.tau_sf;
    ret.xi = ret.tau_c/ret.tau_sf;
    ret.phi = 0;
    
    return ret;
}

// We need to mimic partial function application
typedef struct {
    params params;
    double tau_goal;
    double (*tau_fn)(double, double, params);
} partial_tau;
double exec_partial_tau(partial_tau *p, double s);

#endif