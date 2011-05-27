#
# Makefile for testing smoothed letter ngram LMs
#

## Main config

# training text file in DATA_DIR, must be sentence per line
TRAIN=povidky

# testing text file in current dir (tests), must be sentence per line
TEST=slovane

# name of the LM for test
MODEL=UnigramLetter

# maximumm ngram order when generating statsfile
NORDER=5

# don't inlude ngrams with frequency lesser than CROP
CROP=10

# size of the alphabet
ALPHABET=256

## Paths config

# storage of raw training data
DATA_DIR=../sample-data/
MODEL_DIR=../src/testing/
TEST_PY=../src/testing/test.py
FORMAT_PY=../src/utils/formatText.py
STATS_PY=../src/learning/charstats.py

all: train test

show: train test
	cat $(TEST)_results.txt


train: $(TRAIN).stats
$(TRAIN).stats: $(TRAIN).txt $(STATS_PY)
	$(STATS_PY) -n $(NORDER) -m $(CROP) -a $(ALPHABET) -o $@ $(TRAIN).txt

$(TRAIN).txt: $(DATA_DIR)$(TRAIN).txt $(FORMAT_PY)
	$(FORMAT_PY) $(DATA_DIR)$(TRAIN).txt
	mv $(DATA_DIR)$(TRAIN).txt.sentences $@
	

test: $(TEST)_results.txt
$(TEST)_results.txt: $(TEST).txt $(TRAIN).stats $(TEST_PY) $(MODEL_DIR)$(MODEL)Model.py
	$(TEST_PY) $(MODEL) $(TRAIN).stats $(TEST).txt > $@


clean:
	rm -f *.stats *_results.txt


