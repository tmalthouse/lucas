#! /bin/sh -x

clang bifurcation.c gnuplot_i.o -lm -O3 -obifurc

if [ "$1" == "run" ]; then
    ./bifurc
fi