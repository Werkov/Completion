from math import log
# coding=utf-8
N = 3 # must be >= 2

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
        self.ngrams = {} # occurencies for given ngram
        self.ngramCounts = N * [0] # occurencies for given ngram length
        self.ngramUniqueCounts = N * [0] # occurencies of unique ngrams
        self.search = {}
        for word in text.split():
            buffer = buffer[1:N]
            buffer.append(word)
            for order in range(N):
                self.ngramCounts[order] += 1
                key = self._ngramToKey(buffer[N-1-order:N])
                if key not in self.ngrams:
                    self.ngrams[key] = 1
                    self.ngramUniqueCounts[order] += 1
                else:
                    self.ngrams[key] += 1
            predictor = buffer[N-2]
            predicted = buffer[N-1]
            if not predictor in self.search:
                self.search[predictor] = {}
            self.search[predictor][predicted] = True

    def _ngramToKey(self, ngram):
        return SimpleLangModel.delimiter.join(ngram)

    def getAllCount(self, length):
        return self.ngramCounts[length - 1]

    def getProbability(self, ngram):
        order = len(ngram) - 1
#        if order > N-1:
#            return 0, 0.0
        key = self._ngramToKey(ngram)
        if key not in self.ngrams:
            return 0.0, 0.0
        else:
            return self.ngrams[key], float(self.ngrams[key]) / self.ngramCounts[order]

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
        count, prob = self.baseLM.getProbability(ngram) # don't use prob
        count += self.parameter
        return count, float(count) / self.getAllCount(len(ngram))

    def getAllCount(self, length):
        return self.baseLM.getAllCount(length) + self.parameter * (self.vocabularySize ** length)
        
# linear interpolation
# backoff
        
f = open("../tests/kopete.txt")
all = " ".join(f.readlines())
f.close()

os = SimpleLangModel(all)
oa = LaplaceSmoothLM(os, parameter=0.001)

M = N-1
buffer = (M) * [""]

word = raw_input("Start: ")
while word != "":
    buffer = buffer[1:M]
    buffer.append(word)
    if buffer[M-1] not in os.search:
        tips = []
    else:
        tips = os.search[buffer[M-1]].keys()
        #tips = os.search.keys()
    cnt, probB = oa.getProbability(buffer)
    tips2 = []
    for word in tips:
        cnt, probA = oa.getProbability(buffer + [word])
        tips2.append((word, log(probA / probB)))

    tips2.sort(key=lambda pair: -pair[1])
    for tip in tips2[0:20]:
        print """%s: %f""" % tip
    
    
    word = raw_input()



# run python -i {filename}
# ask questions like o*.getProbability(["word1", "word2"])
