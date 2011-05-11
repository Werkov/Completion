# Toto je jen schematická ukázka Makefile
SHELL=bash
TRAIN=small
TEST=dtest

all: train test

train: $(TRAIN).model
$(TRAIN).model: $(TRAIN).txt train.pl
	./train.pl < $(TRAIN).txt > $@

test: $(SAMPLE)_results.txt
$(SAMPLE)_results.txt: $(TEST).txt $(TRAIN).model test.pl
	./test.pl $(TRAIN).model < $(TEST).txt | tee $@

clean:
	rm -f *.model *_results.txt

# small.txt a dtest.txt jsou uloženy v repozitáři
# Pro trénování na větších datech lze použít TRAIN=big
big.txt:
	wget http://this.file.is.not.stored.in.git/big.txt
