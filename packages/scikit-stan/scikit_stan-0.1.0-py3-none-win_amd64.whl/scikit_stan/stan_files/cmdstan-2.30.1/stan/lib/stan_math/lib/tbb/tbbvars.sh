#!/bin/sh
export TBBROOT="D:/a/scikit-stan/scikit-stan/build/lib.win-amd64-cpython-37/scikit_stan/stan_files/cmdstan-2.30.1/stan/lib/stan_math/lib/tbb_2020.3"
export TBB_ARCH_PLATFORM="intel64\mingw8.3.0"
export TBB_TARGET_ARCH="intel64"
export CPATH="${TBBROOT}/include;$CPATH"
export LIBRARY_PATH="D:/a/scikit-stan/scikit-stan/build/lib.win-amd64-cpython-37/scikit_stan/stan_files/cmdstan-2.30.1/stan/lib/stan_math/lib/tbb;$LIBRARY_PATH"
export PATH="D:/a/scikit-stan/scikit-stan/build/lib.win-amd64-cpython-37/scikit_stan/stan_files/cmdstan-2.30.1/stan/lib/stan_math/lib/tbb;$PATH"
export LD_LIBRARY_PATH="D:/a/scikit-stan/scikit-stan/build/lib.win-amd64-cpython-37/scikit_stan/stan_files/cmdstan-2.30.1/stan/lib/stan_math/lib/tbb;$LD_LIBRARY_PATH"
