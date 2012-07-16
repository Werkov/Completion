FORMAT=../src/python/learning/formatText.py
BINKLM=../bin/kenlm/build_binary
BINSEL=../bin/selector/build_binary

.SECONDARY: povidky.arpa.gz
.PHONY: all clean
.DEFAULT: all

%.bin: %.arpa.gz
	$(BINKLM) -a 22 -q 8 -b 8 trie $< $@

%.sel.bin: %.arpa.gz
	$(BINSEL) $< $@

%.arpa.gz: %.arpa
	gzip $<

%.arpa: %.txt.sentences
	ngram-count -unk -lm $@ -text $<

%.txt.sentences: %.txt
	$(FORMAT) $<

all: povidky.bin povidky.sel.bin

clean:
	rm -f povidky.bin povidky.sel.bin
