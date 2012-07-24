import itertools

import common.tokenize
import lm
import lm.arpaselector
import string
import unicodedata


class UniformSelector(lm.Selector):
    """
    Simple context-less selector with O(n) prefix search where `n` is size of
    the vocabulary. Search statically in a given dictionary or use vocabulary
    of given language model each time.
    """
    def __init__(self, dictionary=[], languageModel=None):
        self._dictionary = dictionary
        self._languageModel = languageModel

    def shift(self, token):
        pass

    def reset(self):
        pass

    def suggestions(self, prefix):
        voc = self._vocabulary()
        suggestions = [
            tok for tok in voc
            if  tok.lower().startswith(prefix.lower())
                and tok not in [common.tokenize.TOKEN_BEG_SENTENCE, common.tokenize.TOKEN_END_SENTENCE]
            ]
        prefixProb = len(suggestions) / len(voc) if len(voc) > 0 else 0
        return (suggestions, prefixProb)

    def _vocabulary(self):
        return self._languageModel.vocabulary() if self._languageModel else self._dictionary

class UnigramSelector(lm.arpaselector.ARPASelector):
    def __init__(self, filename, contextHandler, limit=10000, ** kwargs):
        lm.arpaselector.ARPASelector.__init__(self, filename)
        self._contextHandler = contextHandler
        self._limit = int(limit)

    def suggestions(self, prefix):
        if len(prefix) > 0 \
            and self._contextHandler.context[-1] in [common.tokenize.TOKEN_BEG_SENTENCE,
                common.tokenize.TOKEN_END_SENTENCE]:
            prefix = prefix[0].lower() + prefix[1:]

        r = self.unigramSuggestions(prefix, self._limit)
        l = r[0]
        return (l, r[1])


class BigramSelector(lm.arpaselector.ARPASelector):
    def __init__(self, filename, contextHandler, limit=10000, unigram_threshold=3, ** kwargs):
        lm.arpaselector.ARPASelector.__init__(self, filename)
        self._contextHandler = contextHandler
        self._limit = int(limit)
        self._unigramThreshold = int(unigram_threshold)

    def suggestions(self, prefix):
        if len(prefix) > 0 \
            and (self._contextHandler.context[-1] == common.tokenize.TOKEN_BEG_SENTENCE \
                 or self._contextHandler.context[-1] == common.tokenize.TOKEN_END_SENTENCE):
            prefix = prefix[0].lower() + prefix[1:]

        if len(prefix) > self._unigramThreshold:
            r = self.unigramSuggestions(prefix, self._limit)
        else:
            r = self.bigramSuggestions(prefix, self._limit)
#        r = self.bigramSuggestions(prefix, self._limit)
#        if len(r) == 0: # if we got 0 because of lack of suggestions
#            r = self.unigramSuggestions(prefix, self._limit)
        l = r[0]
        return (l, r[1])

class MultiSelector(lm.Selector):
    """Combine more selectors into one."""

    def __init__(self):
        self._selectors = []

    def addSelector(self, selector):
        self._selectors.append(selector)

    def shift(self, token):
        for selector in self._selectors:
            selector.shift(token)

    def reset(self):
        for selector in self._selectors:
            selector.reset()

    def suggestions(self, prefix):
        suggestions = []
        # TODO: returned prefixProbability is average of child selectors weighted by no.
        # of their suggesstions
        pProbs = 0
        total = 0
        for selector in self._selectors:
            suggs, prefixProb = selector.suggestions(prefix)
            suggestions.append(suggs)
            pProbs += prefixProb * len(suggs)
            total += len(suggs)
        return set(itertools.chain(*suggestions)), (pProbs / total if total > 0 else 0)


#class T9SuggestionSelector(lm.Selector):
#    keys = {
#    "a": 2, "b": 2, "c": 2,
#    "d": 3, "e": 3, "f": 3,
#    "g": 4, "h": 4, "i": 4,
#    "j": 5, "k": 5, "l": 5,
#    "m": 6, "n": 6, "o": 6,
#    "p": 7, "q": 7, "r": 7, "s": 7,
#    "t": 8, "u": 8, "v": 8,
#    "w": 9, "x": 9, "y": 9, "z": 9}
#
#    def _normalize(self, text):
#        return ''.join(x for x in unicodedata.normalize('NFKD', text) if x in string.ascii_letters).lower()
#
#    def _toKeypad(self, text):
#        return ''.join([str(self.keys[c]) for c in text])
#
#    def __init__(self, dict=None):
#        self._map = {}
#        for word in dict:
#            key = self._toKeypad(self._normalize(word))
#            if key in self._map:
#                self._map[key].append(word)
#            else:
#                self._map[key] = [word]
#
#
#    def suggestions(self, context, prefix=""):
#        if prefix == None or prefix not in self._map:
#            return []
#        return self._map[prefix]
#
#
