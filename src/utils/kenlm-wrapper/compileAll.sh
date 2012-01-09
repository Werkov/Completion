#!/bin/bash

make # wrapper

rm sipkenlm* # generated files
python3 configure.py # Makefile.generated
make -f Makefile.generated clean # Python module
make -f Makefile.generated # Python module

mv kenlm.so ../kenlm.so.`icu-config --version`
