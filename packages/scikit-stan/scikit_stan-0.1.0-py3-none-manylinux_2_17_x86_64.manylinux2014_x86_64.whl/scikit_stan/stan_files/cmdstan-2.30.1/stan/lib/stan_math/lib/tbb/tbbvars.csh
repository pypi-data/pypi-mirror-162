#!/bin/csh
setenv TBBROOT "/project/build/lib.linux-x86_64-cpython-37/scikit_stan/stan_files/cmdstan-2.30.1/stan/lib/stan_math/lib/tbb_2020.3" #
setenv tbb_bin "/project/build/lib.linux-x86_64-cpython-37/scikit_stan/stan_files/cmdstan-2.30.1/stan/lib/stan_math/lib/tbb" #
if (! $?CPATH) then #
    setenv CPATH "${TBBROOT}/include" #
else #
    setenv CPATH "${TBBROOT}/include:$CPATH" #
endif #
if (! $?LIBRARY_PATH) then #
    setenv LIBRARY_PATH "${tbb_bin}" #
else #
    setenv LIBRARY_PATH "${tbb_bin}:$LIBRARY_PATH" #
endif #
if (! $?LD_LIBRARY_PATH) then #
    setenv LD_LIBRARY_PATH "${tbb_bin}" #
else #
    setenv LD_LIBRARY_PATH "${tbb_bin}:$LD_LIBRARY_PATH" #
endif #
 #
