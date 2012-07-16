import string
import unicodedata

import lm.arpaselector
import common.Tokenize

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
        

    def getSuggestions(self, context, prefix=""):
        if prefix == None or prefix not in self.map:
            return []
        return self.map[prefix]

class SuggestionSelector:
    def __init__(self, bigramDict=None, dict=None):
        self.bigramDict = bigramDict
        self.dict = dict

    def getSuggestions(self, context, prefix=""):
        lastToken = context[len(context)-1]
        if self.bigramDict == None and self.dict == None:
            return []
        elif self.bigramDict == None and self.dict != None:
            if prefix == "":
                return []
            else:
                return [token for token in self.dict if token.startswith(prefix)]
        else: # bigram is more important  elif self.bigramDict != None and self.dict == None:
            if prefix != "":
                if lastToken not in self.bigramDict:
                    return [token for token in self.bigramDict.keys() if token.startswith(prefix)]
                else:
                    return [token for token in self.bigramDict[lastToken].keys() if token.startswith(prefix)]
            else:
                if lastToken not in self.bigramDict:
                    return []
                else:
                    return self.bigramDict[lastToken].keys()

class UniformSelector:
    """
    Simple context-less selector with O(n) prefix search where `n` is size of
    the vocabulary.
    """
    def __init__(self, dictionary):
        self._dictionary = dictionary # TODO trie or don't use seriously

    def shift(self, token):
        pass

    def reset(self):
        pass

    def suggestions(self, prefix):        
        return [tok for tok in self._dictionary if tok.lower().startswith(prefix.lower())]


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