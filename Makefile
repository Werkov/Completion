# Ubuntu
#  certainly needs packages: python3, python3-sip, python3-sip-dev
#

wrapper_dir=src/utils/kenlm-wrapper

all: kenlm wrapper
	cd $(wrapper_dir) ; python3 -i kenlm.test.py

kenlm:
	make -C libs/kenlm

wrapper:
	make -C $(wrapper_dir) -f Makefile
	cd $(wrapper_dir) ; python3 configure.py
	make -C $(wrapper_dir) -f Makefile.generated


