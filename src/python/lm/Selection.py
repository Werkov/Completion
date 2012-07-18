import string
import unicodedata
import itertools

import lm
import lm.arpaselector
import common.Tokenize


class UniformSelector(lm.Selector):
    """
    Simple context-less selector with O(n) prefix search where `n` is size of
    the vocabulary. Search statically in a given dictionary or use vocabulary
    of given language model each time.
    """
    def __init__(self, dictionary = [], languageModel = None):
        self._dictionary = dictionary
        self._languageModel = languageModel

    def shift(self, token):
        pass

    def reset(self):
        pass

    def suggestions(self, prefix):        
        return [tok for tok in self._vocabulary() if tok.lower().startswith(prefix.lower())]

    def _vocabulary(self):
        return self._languageModel.vocabulary() if self._languageModel else self._dictionary


class BigramSelector(lm.arpaselector.ARPASelector):
    def __init__(self, filename, contextHandler):
        lm.arpaselector.ARPASelector.__init__(self, filename)
        self._contextHandler = contextHandler

    def suggestions(self, prefix):
        if len(prefix) > 0 \
            and (self._contextHandler.context[-1] == common.Tokenize.TOKEN_BEG_SENTENCE \
                 or self._contextHandler.context[-1] == common.Tokenize.TOKEN_END_SENTENCE):
            prefix = prefix[0].lower() + prefix[1:]

        if len(prefix) > 3:
            l = self.unigramSuggestions(prefix)
        else:
            l = self.bigramSuggestions(prefix)

        if len(l) > 10000:
            l = [w for w in l if len(w) > 5] # experimental
        return [] if len(l) > 10000 else l

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
        for selector in self._selectors:
            suggestions.append(selector.suggestions(prefix))
        return set(itertools.chain(*suggestions))


class T9SuggestionSelector(lm.Selector):
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
        self._map = {}
        for word in dict:
            key = self._toKeypad(self._normalize(word))
            if key in self._map:
                self._map[key].append(word)
            else:
                self._map[key] = [word]


    def suggestions(self, context, prefix=""):
        if prefix == None or prefix not in self._map:
            return []
        return self._map[prefix]


