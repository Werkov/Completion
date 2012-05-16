#!/usr/bin/python3

import sys
import os

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from common.Tokenize import *




def formatFile(fin, fout):
    """
    collapse whitespace to single space
    and split text into sentences
    :fin  input file object
    :fout  output file object
    return number of parsed sentences
    """
    cntSentences = 0
    tft = TextFileTokenizer(fin)
    sent = SentenceTokenizer(tft)
    filter = TokenFilter(sent)
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
