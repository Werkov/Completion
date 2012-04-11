#!/usr/bin/python3
#coding=utf-8

import sys
import os
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from common.Tokenize import TextFileTokenizer, Tokenizer

# collapse whitespace to single space
# and split text into sentences (as delimiter is used '.')
# @param file fin
# @param file fout
# @return int no. of parsed sentences
def formatFile(fin, fout):
   cntSentences= 0
   sentence = []
   for token in TextFileTokenizer(fin):
       if token[0] == Tokenizer.TYPE_DELIMITER and token[1] in Tokenizer.sentenceDelimiters:
           cntSentences += 1
           fout.write(" ".join(sentence) + "\n")
           sentence = []
       elif token[0] != Tokenizer.TYPE_WHITESPACE:
           sentence.append(token[1])
   
   return cntSentences


# -- Parse command line options and arguments --
if len(sys.argv) < 2:
   print( "Usage: format.py file(s) ...")
   sys.exit(1)

files = sys.argv[1:]

if len(files) == 0:
   print("No input files given.")
   sys.exit(1)
   
results = []   #results of single tests (to calculate variance)
for filename in files:
   fin = open(filename)
   fout = open(filename + ".sentences", "w")
   sentences = formatFile(fin, fout)
   print("File:", filename, "contains", sentences, "sentences.")
   fin.close()
   fout.close()
