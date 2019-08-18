#include <math.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <math.h>
#include "darray.h"
#include "array.h"
#include "bifurcation.h"
#include "gnuplot_i.h"

double next_point_interval = 2;





double exec_partial_tau(partial_tau *p, double s) {
    return p->tau_fn(
        s,
        p->tau_goal,
        p->params
    );
}


// Beautiful hacks
darray_type_header(double);
darray_type(double)




dpair rootsearch(partial_tau *f, double a, double b, double dx) {
    double x_1 = a;
    double f1 = exec_partial_tau(f, x_1);

    double x_2 = a + dx;
    double f2 = exec_partial_tau(f, x_2);

    while (f1 * f2 > 0) {
        // printf("%f\n", x_1);
        if (x_1 >= b) {
            return (dpair){.invalid=true};
        }

        x_1 = x_2;
        f1 = f2;

        x_2 = x_1 + dx;
        f2 = exec_partial_tau(f,x_2);
    }

    return (dpair){
        .x1 = x_1,
        .x2 = x_2,
    };
}


maybe_double bisect(partial_tau *f, double x_1, double x_2, bool flag, double eps) {
    double f1 = exec_partial_tau(f,x_1);
    if (f1 == 0) {
        return (maybe_double){x_1};
    }

    double f2 = exec_partial_tau(f,x_2);
    if (f2 == 0) {
        return (maybe_double){x_2};
    }

    if (f1 * f2 > 0) {
        printf("Root is not bracketed!\n");
        return (maybe_double){.invalid=true};
    }

    int n = (int)ceil(
        log(fabs(x_2 - x_1)/eps)/log(2.0)
    );

    for (int i=0; i<n; i++) {
        double x_3 = 0.5 * (x_1 + x_2);
        double f3 = exec_partial_tau(f,x_3);
        if (flag && (fabs(f3) > fabs(f1)) && (fabs(f3) > fabs(f2))) {
            return (maybe_double){.invalid=true};
        }

        if (f3 == 0) {
            return (maybe_double){x_3};
        }

        if (f2 * f3 < 0) {
            x_1 = x_3;
            f1 = f3;
        } else {
            x_2 = x_3;
            f2 = f3;
        }

    }

    return (maybe_double){(x_1 + x_2) / 2.0};
}





double roots(partial_tau *f, double a, double b, double eps) {
    // printf("The roots on the interval [%f, %f] are:\n", a, b);

    Darray_double *found_roots = new_darray_double(64);
    int root_count = 0;
    while (1) {
        dpair roots = rootsearch(f, a, b, eps);

        if (!roots.invalid) {
            a = roots.x2;
            maybe_double root = bisect(f, roots.x1, roots.x2, true, eps);

            if (!root.invalid) {
                // Every other "root" is actually a pole (but looks like one since the sign changes there)
                // We don't care about poles, though.
                if (root_count % 2 != 0) {
                    darray_append_double(found_roots, root.val);
                }
                root_count++;
            }
        } else {
            break;
        }
    }

    printf("len=%d\n", found_roots->len);
    print_array(found_roots);
    double lowest_root = 0;

    // Return the first non-zero root
    for (int i=0; lowest_root < 1e-6 && i < found_roots->len; i++) {
        lowest_root = found_roots->data[i];
        printf("i=%d, lr=%f\n", i, lowest_root);
    }
    printf("lr=%f\n", lowest_root);

    free_darray_double(found_roots);
    return lowest_root;
}


double tau_s(double s, double tau_goal, params par) {
    double w0_sqr = par.w0 * par.w0;
    double r = par.r;
    double xi = par.xi;
    double phi = par.phi;

    double newfac = 1 - r*sin(phi - xi * s + s) / sin(s);

    return ((s/(2*w0_sqr)) * (
        newfac * tan(s) +
        sqrt(pow(newfac * tan(s), 2) + 4*w0_sqr)
    )) - tau_goal;
}


double gamma_s(double s, params p) {
    double w0_sqr = p.w0 * p.w0;
    double r = p.r;
    double xi = p.xi;
    double phi = p.phi;

    double newfac = 1 - r*cos(phi - xi*s);
    return newfac / cos(s);
}


int main(int argc, char **argv) {
    int resolution = 64;

    array taus = linspace(1e-6, 2, resolution);
    array s = array_zeros(resolution);
    array gammas = array_zeros(resolution);

    double a = 0, b=100;
    params unc_par = default_params();
    printf("Starting sweep...\n");
    for (int i=0; i<taus.len; i++) {
        printf("\r[%d/%d]", i, (int)taus.len);
        fflush(stdout);
        partial_tau infunc = {
            .params = unc_par,
            .tau_goal = taus.vals[i],
            .tau_fn = tau_s,
        };

        double lowestroot = roots(&infunc, a, b, 1e-6);
        // a = lowestroot - next_point_interval;
        // a = a<0 ? 0 : a;
        // b = lowestroot + next_point_interval;
        s.vals[i] = lowestroot;
        gammas.vals[i] = gamma_s(lowestroot, unc_par);
        // exit(1);
    }

    gnuplot_ctrl *plt = gnuplot_init();
    gnuplot_write_xy_csv("bifurcation_data.csv", taus.vals, gammas.vals, taus.len, NULL);
    gnuplot_set_xlabel(plt, "τ/T_0");
    gnuplot_set_ylabel(plt, "γ_sf");
    gnuplot_setstyle(plt, "lines");
    gnuplot_plot_xy(plt, taus.vals, s.vals, taus.len, "Uncoupled Curves");
    printf("\nPress [enter] to close\n");
    getchar();
    gnuplot_close(plt);
}