from math import log
import re
import sys

N = 3 # must be >= 2

class MockLangModel:
    """Just specification of an interface"""
    def getProbability(self, ngram):
        """Return tuple – no. of occurencies and probability of ngram"""
        return 0.0, 0.0
    def getAllCount(self, length):
        """Return total count of observed ngrams of given length"""
        return 0

class Tokenizer:
    """
    Base for tokenizer classes. Try matching specified patterns.
    
    Considered patterns (and tokens returned by _getToken) are spefified
    within masks list. When ambiguous, first matches.
    """
    TYPE_WORD = 1
    TYPE_NUMBER = 2
    TYPE_DELIMITER = 3
    TYPE_OTHER = 4
    TYPE_WHITESPACE = 5

    masks = [
        (TYPE_WHITESPACE, "\s+"),
        (TYPE_WORD, "\w+"),
        (TYPE_NUMBER, "\d+"),
        (TYPE_DELIMITER, "[,\\.:;\"'\\-]"),
        (TYPE_OTHER, ".")
    ]
    def __init__(self):
        self.regexps = []
        for type, mask in self.masks:
            self.regexps.append((type, re.compile(mask)))
        
    def _getToken(self, string, pos):
        """Return token starting at the position of the string."""
        for type, regexp in self.regexps:
            m = regexp.match(string, pos)
            if m:
                return (type, m.group(0))
        return None

class TextFileTokenizer (Tokenizer):
    """Parse content of a file into sequence of tokens, skips whitespace and perform true-casing."""

    # Delimiters after which true-casing is applied.
    sentenceDelimiters = set(".")
        
    def __init__(self, file):
        """Use file-like object as an input"""
        super(TextFileTokenizer, self).__init__()
        self.file = file
        self.currPos = 0
        self.currLine = ""
        self.beginSentence = True # used for detecting begining of sentece

    def __iter__(self):
        return self

    def __next__(self):
        """Return current token as a tuple (type, stringData) and conforms iterator protocol."""
        token = Tokenizer.TYPE_WHITESPACE, ""
        while token[0] == Tokenizer.TYPE_WHITESPACE:
            if self.currPos == len(self.currLine):
                self.currLine = self.file.readline()
                self.currPos = 0
            if self.currLine == "":
                raise StopIteration
            token = self._getToken(self.currLine, self.currPos)
            self.currPos += len(token[1])

        if token[0] == Tokenizer.TYPE_DELIMITER and token[1] in TextFileTokenizer.sentenceDelimiters:
            self.beginSentence = True
        elif self.beginSentence:
            token = token[0], str.lower(token[1])
            self.beginSentence = False
        
        return token


class SimpleLangModel:
    """
    This model only provides simple statistics from given text file.
    Used for testing.
    """
    delimiter = "__"
    def __init__(self, file, tokenizer=TextFileTokenizer):
        buffer = N * ['']
        self.ngrams = {} # occurencies for given ngram
        self.ngramCounts = N * [0] # occurencies for given ngram length
        self.ngramUniqueCounts = N * [0] # occurencies of unique ngrams
        self.search = {}
        t = tokenizer(file)
        for type, word in t:
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
os = SimpleLangModel(f)
f.close()

oa = LaplaceSmoothLM(os, parameter=0.002)

M = N-1
buffer = (M) * [""]

word = input("Start: ")
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
        print("{}: {}".format(*tip))


    word = input()




# run python -i {filename}
# write single words and confirm with <enter>
