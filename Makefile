SIMPLE_MAKES=src/cpp/kenlm-wrapper src/cpp/ARPA-selector sample-data
CMAKES=libs/kenlm
SIP_MAKES=src/sip/kenlm-bindings src/sip/selector-bindings

.PHONY: $(SIMPLE_MAKES) $(SIP_MAKES) $(CMAKES)

all: $(SIMPLE_MAKES) $(SIP_MAKES) $(CMAKES)

$(SIMPLE_MAKES):
	make -C $@

$(CMAKES):
	(cd $@ ; test -f Makefile || cmake .)
	make -C $@
	cp $(CMAKES)/bin/build_binary bin/kenlm/

$(SIP_MAKES):
	(cd $@; sip-install --target-dir ../../../bin/$(notdir $@))

#
# -- dependencies --
#
# both use KenLM
src/cpp/kenlm-wrapper: libs/kenlm
src/cpp/ARPA-selector: libs/kenlm

# bindings needs C++ objects
src/sip/kenlm-bindings: src/cpp/kenlm-wrapper
src/sip/selector-bindings: src/cpp/ARPA-selector

# building binaries
sample-data: libs/kenlm src/cpp/ARPA-selector
