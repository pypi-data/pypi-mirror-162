@echo off
SET TBBROOT=D:\a\scikit-stan\scikit-stan\build\lib.win-amd64-cpython-37\scikit_stan\stan_files\cmdstan-2.30.1\stan\lib\stan_math\lib\tbb_2020.3
SET TBB_ARCH_PLATFORM=intel64\mingw8.3.0
SET TBB_TARGET_ARCH=intel64
SET CPATH=%TBBROOT%\include;%CPATH%
SET LIBRARY_PATH=D:\a\scikit-stan\scikit-stan\build\lib.win-amd64-cpython-37\scikit_stan\stan_files\cmdstan-2.30.1\stan\lib\stan_math\lib\tbb;%LIBRARY_PATH%
SET PATH=D:\a\scikit-stan\scikit-stan\build\lib.win-amd64-cpython-37\scikit_stan\stan_files\cmdstan-2.30.1\stan\lib\stan_math\lib\tbb;%PATH%
SET LD_LIBRARY_PATH=D:\a\scikit-stan\scikit-stan\build\lib.win-amd64-cpython-37\scikit_stan\stan_files\cmdstan-2.30.1\stan\lib\stan_math\lib\tbb;%LD_LIBRARY_PATH%
