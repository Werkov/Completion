#!/usr/bin/python3
import sys
import os

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import common.Tokenize

class TokenNormalizer:
    """
    Accepts sequence of sentences and converts each token tuple into string
    representation of that tuple and substitutes special tokens types for special
    strings.
    """

    def __init__(self, sentences):
        self.reset(sentences)

    def reset(self, sentences):
        self.sentences = sentences

    def __iter__(self):
        for sentence in self.sentences:
            sentence = map(self._mapToken, filter(self._filterToken, sentence))
            yield sentence

    def _mapToken(self, token):
        if token[1] == common.Tokenize.TYPE_NUMBER:
            return common.Tokenize.TOKEN_NUMERIC
        else:
            return token[0]
        
    def _filterToken(self, token):
        return token[1] != common.Tokenize.TYPE_SENTENCE_END



def formatFile(fin, fout):
    """
    Collapse whitespace to single space and split text into sentences.

    :fin    input file object
    :fout   output file object
    return  number of parsed sentences
    """
    cntSentences = 0
    tft = common.Tokenize.TextFileTokenizer(fin)
    sent = common.Tokenize.SentenceTokenizer(tft)
    filter = TokenNormalizer(sent)
    cntSentences = 0
    for sentence in filter:
        fout.write(" ".join(sentence) + "\n")
        cntSentences += 1
   
    return cntSentences


# -- Parse command line options and arguments --
if len(sys.argv) < 2:
    print("Usage: format.py file(s) ...")
    sys.exit(1)

files = sys.argv[1:]

for filename in files:
    fin = open(filename)
    fout = open(filename + ".sentences", "w")
    sentences = formatFile(fin, fout)
    print("File '{}' contains {} sentences.".format(filename, sentences))
    fin.close()
    fout.close()
