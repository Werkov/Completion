SIMPLE_MAKES=libs/kenlm src/cpp/kenlm-wrapper src/cpp/ARPA-selector
SIP_MAKES=src/sip/kenlm-bindings src/sip/selector-bindings

.PHONY: $(SIMPLE_MAKES) $(SIP_MAKES)

all: $(SIMPLE_MAKES) $(SIP_MAKES)

$(SIMPLE_MAKES):
	make -C $@

$(SIP_MAKES):
	(cd $@; ./configure.py)
	make -C $@
	make -C $@ install

src/cpp/kenlm-wrapper: libs/kenlm
src/cpp/ARPA-selector: libs/kenlm
src/sip/kenlm-bindings: src/cpp/kenlm-wrapper
src/sip/selector-bindings: src/cpp/ARPA-selector

