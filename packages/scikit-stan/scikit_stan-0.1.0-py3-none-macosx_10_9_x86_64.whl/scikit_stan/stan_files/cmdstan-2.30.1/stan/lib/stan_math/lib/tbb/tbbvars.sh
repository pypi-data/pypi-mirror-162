#!/bin/bash
export TBBROOT="/Users/runner/work/scikit-stan/scikit-stan/build/lib.macosx-10.9-x86_64-cpython-37/scikit_stan/stan_files/cmdstan-2.30.1/stan/lib/stan_math/lib/tbb_2020.3" #
tbb_bin="/Users/runner/work/scikit-stan/scikit-stan/build/lib.macosx-10.9-x86_64-cpython-37/scikit_stan/stan_files/cmdstan-2.30.1/stan/lib/stan_math/lib/tbb" #
if [ -z "$CPATH" ]; then #
    export CPATH="${TBBROOT}/include" #
else #
    export CPATH="${TBBROOT}/include:$CPATH" #
fi #
if [ -z "$LIBRARY_PATH" ]; then #
    export LIBRARY_PATH="${tbb_bin}" #
else #
    export LIBRARY_PATH="${tbb_bin}:$LIBRARY_PATH" #
fi #
if [ -z "$DYLD_LIBRARY_PATH" ]; then #
    export DYLD_LIBRARY_PATH="${tbb_bin}" #
else #
    export DYLD_LIBRARY_PATH="${tbb_bin}:$DYLD_LIBRARY_PATH" #
fi #
 #
