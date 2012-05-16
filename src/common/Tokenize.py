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
        (TYPE_NUMBER, "\d+"),
        (TYPE_WORD, "\w+"),
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
    """
    Parse content of a file into sequence of tokens, skips whitespace.
    Token is tuple of (token type, token string representation).
    """
  
    def __init__(self, file):
        """Use file-like object as an input."""
        super().__init__()
        self.file = file
        self.currPos = 0
        self.currLine = ""

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

        return token

class StringTokenizer(Tokenizer):
    """
    Parse string into sequence of tokens.

    :text string to parse
    """
    def __init__(self, text):
        super().__init__()
        self.reset(text)

    def reset(self, text):
        self.text = text
        self.position = 0

    def __iter__(self):
        return self

    def __next__(self):
        """Return current token as a tuple (type, stringData) and conforms iterator protocol."""
        token = Tokenizer.TYPE_WHITESPACE, ""
        while token[0] == Tokenizer.TYPE_WHITESPACE:
            if self.position == len(self.text):
                raise StopIteration
            token = self._getToken(self.text, self.position)
            self.position += len(token[1])

        return token

class SentenceTokenizer:
    """
    Divide given sequence of tokens into sequence of lists, each representing one sentence.

    Also performs true-casing.
    """

    sentenceDelimiters = {".", "!", "?"}

    def __init__(self, tokens):
        self.reset(tokens)

    def reset(self, tokens):
        self.tokens = tokens

    def __iter__(self):
        result = []
        endOfSentence = True

        for t in self.tokens:
            if endOfSentence:
                t = t[0], t[1].lower()
                endOfSentence = False

            result.append(t)
            if t[1] in self.sentenceDelimiters:
                yield result
                result = []
                endOfSentence = True
                
        if len(result) > 0:
            yield result



class TokenFilter:
    """
    Accepts sequence of sentences and converts each token tuple into string
    representation of that tuple and substitutes special tokens types for special
    strings.
    """

    numericToken = "<num>"
    beginSenteceToken = "<s>"
    endSentenceToken = "</s>"
    unknownToken= "<unk>"

    def __init__(self, sentences):
        self.reset(sentences)

    def reset(self, sentences):
        self.sentences = sentences

    def __iter__(self):
        for sentence in self.sentences:
            sentence = map(self._mapToken, sentence)
            yield sentence

    def _mapToken(self, token):
        if token[0] == Tokenizer.TYPE_NUMBER:
            return self.numericToken
        else:
            return token[1]
