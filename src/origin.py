"""
Basic implementations of essential classes.
Module is temporarily named 'origin' as the classes will
be detached to specific modules when they become more complex.
"""
from math import log
from math import sqrt
import sys

import re
import string
import unicodedata
from utils import kenlm

N = 3 # must be >= 2

class MockLangModel:
    """Just specification of an interface"""
    def probability(self, ngram):
        """Return tuple – no. of occurencies and probability of ngram."""
        return 0.0, 0.0
    def allCount(self, length):
        """Return total count of observed ngrams of given length."""
        return 0
    def updateUserInput(self, text):
        """Used to refresh text inserted by user. Parameter is whole text from begining to the cursor."""
        pass

class MockLangModelB:
    def probability(self, context, token):
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
        (TYPE_DELIMITER, "[,\\.:;\"'\\-\\?!]"),
        (TYPE_OTHER, ".")
    ]

    # Delimiters after which e.g. true-casing is applied.
    sentenceDelimiters = set([".", "?", "!"])

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

        if token[0] == Tokenizer.TYPE_DELIMITER and token[1] in Tokenizer.sentenceDelimiters:
            self.beginSentence = True
        elif self.beginSentence:
            token = token[0], str.lower(token[1])
            self.beginSentence = False
        
        return token

class SimpleTriggerModel:
    def __init__(self, tokenizer):
        self.reset()
        self.tokenizer = tokenizer

    def reset(self):
        self.dictionary = {}
        self.sum = 0

    def updateUserInput(self, text):
        self.reset()
        for token in self.tokenizer.tokenize(text):
            self._add(token)

    def _add(self, token):
        if token[0] == Tokenizer.TYPE_WORD:
            if token[1] not in self.dictionary:
                self.dictionary[token[1]] = 0
            self.dictionary[token[1]] += 1
            self.sum += 1
        

    def probability(self, context, token):
        if token in self.dictionary:
            return self.dictionary[token] / self.sum
        else:
            return 0

class KenLMModel:
    def __init__(self, filename):
        self._model = kenlm.Model(filename)
        self.dictionary = self._model.GetVocabulary().GetTokens()

    def probability(self, context, token):
        state = self._model.NullContextState()
        v = self._model.GetVocabulary()
        # shift model to correct state
        for pretoken in context:
            prob, state = self._model.Score(state, v.Index(pretoken))

        prob, _ = self._model.Score(state, v.Index(token))
        return prob
            
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

    def allCount(self, length):
        return self.ngramCounts[length - 1]

    def probability(self, ngram):
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
        self.vocabularySize = vocabularySize if vocabularySize != None else self.baseLM.allCount(1) + 1 # one uknown word
        self.parameter = parameter

    def probability(self, ngram):
        count, prob = self.baseLM.probability(ngram) # don't use prob
        count += self.parameter
        return count, float(count) / self.allCount(len(ngram))

    def allCount(self, length):
        return self.baseLM.allCount(length) + self.parameter * (self.vocabularySize ** length)

class NgramLM:
    """
    Crops given ngram and behave like model with (M-1) long context
    """
    def __init__(self, baseLM, M):
        self.baseLM = baseLM
        self.M = M

    def probability(self, ngram):
        if len(ngram) == N:
            ngram = ngram[-self.M:]
        else:
            ngram = ngram[-(self.M-1):] if self.M > 1 else []
        if len(ngram) == 0:
            return 0, 1
        else:
            return self.baseLM.probability(ngram)

    def allCount(self, length):
        return self.baseLM.allCount(length)
    
class LinearInterLM:
    def __init__(self, LMs, coeffs):
        self.baseLMs = LMs
        self.coeffs = coeffs
    def probability(self, ngram):
        prob = 0
        cnt = 0
        for i in range(len(self.baseLMs)):
            c, p = self.baseLMs[i].probability(ngram)
            prob += p * self.coeffs[i]
            cnt += c * self.coeffs[i]
        return cnt, prob
        

    def allCount(self, length):
        cnt = 0
        for i in range(len(self.baseLMs)):
            c = self.baseLMs[i].allCount(length)
            cnt += c * self.coeffs[i]
        return cnt

class T9SuggestionSelector:
    keys = {
    "a": 2, "b": 2, "c": 2,
    "d": 3, "e": 3, "f": 3,
    "g": 4, "h": 4, "i": 4,
    "j": 5, "k": 5, "l": 5,
    "m": 6, "n": 6, "o": 6,
    "p": 7, "q": 7, "r": 7, "s": 7,
    "t": 8, "u": 8, "v": 8,
    "w": 9, "x": 9, "y": 9, "z": 9}

    def _normalize(self, text):
        return ''.join(x for x in unicodedata.normalize('NFKD', text) if x in string.ascii_letters).lower()

    def _toKeypad(self, text):
        return ''.join([str(self.keys[c]) for c in text])
    
    def __init__(self, dict=None):
        self.map = {}
        for word in dict:
            key = self._toKeypad(self._normalize(word))
            if key in self.map:
                self.map[key].append(word)
            else:
                self.map[key] = [word]
        

    def getSuggestions(self, context, prefix=None):
        if prefix == None or prefix not in self.map:
            return []
        return self.map[prefix]

class SuggestionSelector:
    def __init__(self, bigramDict=None, dict=None):
        self.bigramDict = bigramDict
        self.dict = dict

    def getSuggestions(self, context, prefix=None):
        lastToken = context[len(context)-1]
        if self.bigramDict == None and self.dict == None:
            return []
        elif self.bigramDict == None and self.dict != None:
            if prefix == None:
                return []
            else:
                return [token for token in self.dict if token.startswith(prefix)]
        else: # bigram is more important  elif self.bigramDict != None and self.dict == None:
            if prefix != None:
                if lastToken not in self.bigramDict:
                    return [token for token in self.bigramDict.keys() if token.startswith(prefix)]
                else:
                    return [token for token in self.bigramDict[lastToken].keys() if token.startswith(prefix)]
            else:
                if lastToken not in self.bigramDict:
                    return []
                else:
                    return self.bigramDict[lastToken].keys()

class SuggestionSorter:
    def __init__(self, languageModel):
        self.languageModel = languageModel
    def getSortedSuggestions(self, context, suggestions):
        tips = []
        for token in suggestions:
            prob = self.languageModel.probability(context, token)
            tips.append((token, prob))

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
        cnt, probContext = self.languageModel.probability(context)
        if probContext == 0:
            self.entropy += float("inf")
        else:
            cnt, probNgram = self.languageModel.probability(context + [token])
            self.entropy += -log(probNgram / probContext, 2)
            # print("{} | {}\t\t\t\t\t\t\t{:f}\t".format(token, context, log(probNgram/probContext)))
        self.tokenCnt += 1


    def getResult(self):
        entropyPerToken = self.entropy / self.tokenCnt
        return 2 ** entropyPerToken

class QwertyMetric:
    pass
class BikeyboardMetric:
    pass
class SuggesitionsMetric:
    pass


