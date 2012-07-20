import re

TOKEN_NUMERIC       = "<num>"
TOKEN_BEG_SENTENCE  = "<s>"
TOKEN_END_SENTENCE  = "</s>"
TOKEN_UNK           = "<unk>"

TYPE_WORD           = 1
TYPE_NUMBER         = 2
TYPE_DELIMITER      = 3
TYPE_OTHER          = 4
TYPE_WHITESPACE     = 5
TYPE_SENTENCE_END   = 6
TYPE_EMOTICON       = 7

class Tokenizer:
    """
    (Abstract) base for tokenizer classes. Try matching specified patterns.
    
    Considered patterns (and tokens returned by _getToken) are spefified
    within masks list. When ambiguous, first matches.

    Token is a tuple of:
        - string representation
        - type (module constant TYPE_*)
        - position of token begining (zero-based character count).
    """

    masks = [
        (TYPE_WHITESPACE, "\s+"),
        (TYPE_NUMBER, "\d+"),
        (TYPE_WORD, "\w+"),
        (TYPE_EMOTICON, ":-[\)\(\[\]DpP]"),
        (TYPE_DELIMITER, "([,:;\"„“]+|\\.+|[\\?!]+|[\\-–—]+)"),
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
                return (m.group(0), type, pos)
        return None



class TextFileTokenizer (Tokenizer):
    """
    Parse content of a file into sequence of tokens, skip whitespace.
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
        token = "", TYPE_WHITESPACE, 0
        while token[1] == TYPE_WHITESPACE:
            if self.currPos == len(self.currLine):
                self.currLine = self.file.readline()
                self.currPos = 0
            if self.currLine == "":
                raise StopIteration
            token = self._getToken(self.currLine, self.currPos)
            self.currPos += len(token[0])

        return token

class StringTokenizer(Tokenizer):
    """
    Parse given string into sequence of tokens.

    When `onlyComplete` is set to True last token is omitted because it needn't
    be complete (only tokens followed by another token are complete).

    Last uncomplete token can be acceessed via `uncompleteToken` attribute.
    """
    def __init__(self, text=None, onlyComplete=False):
        super().__init__()
        self.reset(text, onlyComplete)

    def reset(self, text=None, onlyComplete=False):
        """Used to recycle tokenizer object with new input."""
        self.text = text if text else ""
        self.position = 0
        self.onlyComplete = onlyComplete
        self.uncompleteToken = None     # last token that's considered uncomplete

    def __iter__(self):
        return self

    def __next__(self):
        token = "", TYPE_WHITESPACE, self.position
        while token[1] == TYPE_WHITESPACE:
            if self.position == len(self.text):
                raise StopIteration
            token = self._getToken(self.text, self.position)
            self.position += len(token[0])

        if self.onlyComplete and self.position == len(self.text):
            self.uncompleteToken = token
            raise StopIteration

        return token

class SentenceTokenizer:
    """
    Divide given sequence of tokens into sequence of lists, each representing
    one (unfinished) sentence. Finished sentences are appended an end sentence
    token.

    Also performs true-casing.

    This simple implementation splits stream of tokens after chosen tokens (sentence
    delimiters) and lowercases first token in a sentence.
    """

    

    def __init__(
                 self,
                 tokens=None,
                 sentenceDelimiters=set([".", "!", "?", ":", "..."]),
                 abbreviations=set()
                 ):
        self.reset(tokens)
        self._sentenceDelimiters = sentenceDelimiters
        self._abbreviations = abbreviations

    def reset(self, tokens=None):
        self.tokens = tokens if tokens else []

    def __iter__(self):
        result = []
        endOfSentence = False

        for t in self.tokens:
            if endOfSentence and t[1] != TYPE_DELIMITER:
                yield result + [(TOKEN_END_SENTENCE, TYPE_SENTENCE_END, t[2])]
                result = []
                endOfSentence = False                

            if t[0] in self._sentenceDelimiters:
                if len(result) > 0 and not (result[-1][0] in self._abbreviations
                    or (result[-1][1] == TYPE_NUMBER and TOKEN_NUMERIC in self._abbreviations)):
                    endOfSentence = True
            if len(result) == 0:
                t = t[0].lower(), t[1], t[2]
                
            result.append(t)
                

        if endOfSentence:
            result.append((TOKEN_END_SENTENCE, TYPE_SENTENCE_END, t[2]))
        yield result



class TokenNormalizer:
    """
    Accepts sequence of (unfinished) sentences and converts each token tuple into string
    representation, merge sentences and delimits them by special tokens.
    """

    def __init__(self, sentences = None):
        self.reset(sentences)

    def reset(self, sentences = None):
        self.sentences = sentences if sentences else []

    def __iter__(self):
        for sentence in self.sentences:
            yield TOKEN_BEG_SENTENCE
            for token in map(self._mapToken, sentence):
                yield token


    def _mapToken(self, token):
        if token[1] == TYPE_NUMBER:
            return TOKEN_NUMERIC
        elif token[1] == TYPE_SENTENCE_END:
            return TOKEN_END_SENTENCE
        else:
            return token[0]


