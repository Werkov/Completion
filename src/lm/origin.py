"""
Basic implementations of essential classes.
Module is temporarily named 'origin' as the classes will
be detached to specific modules when they become more complex.
"""

import string
import unicodedata
import lm.kenlm
import common.Tokenize

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
        self._model = lm.kenlm.Model(filename)
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
    def __init__(self, file, tokenizer=common.Tokenize.TextFileTokenizer):
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

