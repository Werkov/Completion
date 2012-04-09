import re

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

class StringTokenizer(Tokenizer):
    """Parse string into list of tokens."""
    def __init__(self):
        super(StringTokenizer, self).__init__()

    def tokenize(self, text):
        position = 0
        tokens = []
        token = self._getToken(text, position)
        while token != None:
            tokens.append(token)
            position += len(token[1])
            token = self._getToken(text, position)
        return tokens
