import sys
sys.path.append("../")

import common.Tokenize

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
            yield common.Tokenize.TOKEN_BEG_SENTENCE
            for token in map(self._mapToken, sentence):
                yield token
            

    def _mapToken(self, token):
        if token[1] == common.Tokenize.TYPE_NUMBER:
            return common.Tokenize.TOKEN_NUMERIC
        elif token[1] == common.Tokenize.TYPE_SENTENCE_END:
            return common.Tokenize.TOKEN_END_SENTENCE
        else:
            return token[0]


