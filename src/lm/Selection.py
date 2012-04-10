import string
import unicodedata

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

