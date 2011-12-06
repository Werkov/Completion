"""
Basic implementations of essential classes.
Module is temporarily named 'origin' as the classes will
be detached to specific modules when they become more complex.
"""
from math import log, sqrt
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

class NgramLM:
    """
    Crops given ngram and behave like model with (M-1) long context
    """
    def __init__(self, baseLM, M):
        self.baseLM = baseLM
        self.M = M

    def getProbability(self, ngram):
        if len(ngram) == N:
            ngram = ngram[-self.M:]
        else:
            ngram = ngram[-(self.M-1):] if self.M > 1 else []
        if len(ngram) == 0:
            return 0, 1
        else:
            return self.baseLM.getProbability(ngram)

    def getAllCount(self, length):
        return self.baseLM.getAllCount(length)
    
class LinearInterLM:
    def __init__(self, LMs, coeffs):
        self.baseLMs = LMs
        self.coeffs = coeffs
    def getProbability(self, ngram):
        prob = 0
        cnt = 0
        for i in range(len(self.baseLMs)):
            c,p = self.baseLMs[i].getProbability(ngram)
            prob += p*self.coeffs[i]
            cnt += c*self.coeffs[i]
        return cnt, prob
        

    def getAllCount(self, length):
        cnt = 0
        for i in range(len(self.baseLMs)):
            c = self.baseLMs[i].getAllCount(length)
            cnt += c*self.coeffs[i]
        return cnt

class SuggestionSelector:
    def __init__(self, bigramDict):
        self.search = bigramDict
    def getSuggestions(self, context):
        lastToken = context[len(context)-1]
        if lastToken not in self.search:
            return []
        else:
            return self.search[lastToken].keys()

class SuggestionSorter:
    def __init__(self, languageModel):
        self.languageModel = languageModel
    def getSortedSuggestions(self, context, suggestions):
        cnt, probContext = self.languageModel.getProbability(context)
        tips = []
        for token in suggestions:
            cnt, probNgram = self.languageModel.getProbability(context + [token])
            tips.append((token, log(probNgram / probContext)))

        tips.sort(key=lambda pair: -pair[1])
        return tips

class AutomatedTest:
    def __init__(self, file):
        self.file = file
        self.metrics = []

    def addMetric(self, metric):
        self.metrics.append(metric)

    def runTest(self):
        tokenizer = TextFileTokenizer(self.file)
        history = ["beg", "beg"] # TODO
        for (type, token) in tokenizer:
            for metric in self.metrics:
                metric.measure(history, token)
            history.append(token)

class EntropyMetric:
    def __init__(self, languageModel):
        self.languageModel = languageModel
        self.entropy = 0
        self.tokenCnt = 0

    def measure(self, history, token):
        context = history[-(N-1):]
        cnt, probContext = self.languageModel.getProbability(context)
        if probContext == 0:
            self.entropy += float("inf")
        else:
            cnt, probNgram = self.languageModel.getProbability(context + [token])
            self.entropy += -log(probNgram/probContext, 2)
            # print("{} | {}\t\t\t\t\t\t\t{:f}\t".format(token, context, log(probNgram/probContext)))
        self.tokenCnt += 1


    def getResult(self):
        entropyPerToken = self.entropy / self.tokenCnt
        return 2**entropyPerToken

class QwertyMetric:
    pass
class BikeyboardMetric:
    pass
class SuggesitionsMetric:
    pass


#f = open("../sample-data/povidky.txt")
#os = SimpleLangModel(f)
#f.close()
#
#
#
#t = open("../tests/snoubenci.txt")
#start = -1
#end = -1
#step = 3
#p = pow(10, start)
#for i in range((end-start)*step + 1):
#    oa = LaplaceSmoothLM(os, parameter=p)
#    um = NgramLM(oa, 1)
#    bm = NgramLM(oa, 2)
#    tm = NgramLM(oa, 3)
#    metric = EntropyMetric(LinearInterLM([um, bm, tm], [0.0,0.0,1.0]))
#    test = AutomatedTest(t)
#    test.addMetric(metric)
#    test.runTest()
#    print("{}\t{}".format(p, metric.getResult()))
#    t.seek(0)
#    p *= pow(10, 1/step)
#
#
##print("Perplexity per token:\t{}".format(metric.getResult()))
#
#
#t.close()
#
##selector = SuggestionSelector(os.search)
##sorter = SuggestionSorter(oa)
##
##M = N-1
##buffer = (M) * [""]
##word = input("Start: ")
##while word != "":
##    buffer = buffer[1:M]
##    buffer.append(word)
##    tips = sorter.getSortedSuggestions(buffer, selector.getSuggestions(buffer))
##    for tip in tips[0:20]:
##        print("{}\t\t{}".format(*tip))
##    word = input()
##
#


# run python -i {filename}
# write single words and confirm with <enter>
