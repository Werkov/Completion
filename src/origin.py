from symbol import parameters
# coding=utf-8
N = 3

class MockLangModel:
    """Just specification of an interface"""
    def getProbability(self, ngram):
        """Return tuple – no. of occurencies and probability of ngram"""
        return 0.0, 0.0
    def getAllCount(self, length):
        """Return total count of observed ngrams of given length"""
        return 0

class SimpleLangModel:
    """
    This model only provides simple statistics from given text.
    As token is taken everything delimited by whitespace.
    Used for testing.
    """
    delimiter = "__"
    def __init__(self, text):
        buffer = N * ['']
        self.ngrams = [{} for tmp in range(N)] # occurencies for given ngram
        self.ngramCounts = N * [0] # occurencies for given ngram length
        self.ngramUniqueCounts = N * [0] # occurencies of unique ngrams
        for word in text.split():
            buffer = buffer[1:N]
            buffer.append(word)
            for order in range(N):
                self.ngramCounts[order] += 1
                key = self._ngramToKey(buffer[N-1-order:N])
                if key not in self.ngrams[order]:
                    self.ngrams[order][key] = 1
                    self.ngramUniqueCounts[order] += 1
                else:
                    self.ngrams[order][key] += 1

    def _ngramToKey(self, ngram):
        return SimpleLangModel.delimiter.join(ngram)

    def getAllCount(self, length):
        return self.ngramCounts[length - 1]

    def getProbability(self, ngram):
        order = len(ngram) - 1
#        if order > N-1:
#            return 0, 0.0
        key = self._ngramToKey(ngram)
        if key not in self.ngrams[order]:
            return 0.0, 0.0
        else:
            return self.ngrams[order][key], float(self.ngrams[order][key]) / self.ngramCounts[order]

class LaplaceSmoothLM:
    """
    Smoothes given model by adding a constant to occurencies of all ngrams.
    """
    def __init__(self, baseLM, vocabularySize=None, parameter=1):
        """If vocabulary size not set, it's taken as unigram count from the model"""
        self.baseLM = baseLM
        self.vocabularySize = vocabularySize if vocabularySize != None else self.baseLM.getAllCount(1) + 1 # one uknown word
        self.parameter = parameter

    def getProbability(self, ngram):
        count,  = self.baseLM.getProbability(ngram) # don't use prob
        count += self.parameter
        return count, float(count)/self.getAllCount(len(ngram))

    def getAllCount(self, length):
        return self.baseLM.getAllCount(length) + self.parameter * (self.vocabularySize ** length)
        
        
        
f = open("../tests/povidky.txt")
all = " ".join(f.readlines())
f.close()

os = SimpleLangModel(all)
oa = LaplaceSmoothLM(os, parameter = 0.1)

# run python -i {filename}
# ask questions like o*.getProbability(["word1", "word2"])
