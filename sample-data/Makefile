
all: povidky.arpa

%.arpa: %.txt.sentences
	ngram-count -lm $@ -text $<

%.txt.sentences: %.txt
	../src/learning/formatText.py $<
