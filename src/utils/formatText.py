#!/usr/bin/python
#coding=utf-8

import sys
import string
from collections import deque

# collapse whitespace to single space
# and split text into sentences (as delimiter is used '.')
# @param file fin
# @param file fout
# @return int no. of parsed sentences
def formatFile(fin, fout):
   cntSentences= 0
   sentence = ""
   collapsed = True # skip preceding whitespace
   for line in fin:      
      for c in line:
         if c in string.whitespace:
            sentence += " " if not collapsed else ""
            collapsed = True
         elif c == ".":
            fout.write(sentence + "\n")
            sentence = ""
            cntSentences += 1
            collapsed = True
         else:
            sentence += c
            collapsed = False
   
   if sentence != "":
      fout.write(sentence + "\n")
      cntSentences += 1
   
   return cntSentences


# -- Parse command line options and arguments --
if len(sys.argv) < 2:
   print "Usage: format.py file(s) ..."
   sys.exit(1)

args = deque(sys.argv[1:])
files = []

while len(args) > 0:
   arg = args.popleft()
   files.append(arg)

if len(files) == 0:
   print "No input files given."
   sys.exit(1)
   
results = []   #results of single tests (to calculate variance)
for filename in files:
   fin = open(filename)
   fout = open(filename + ".sentences", "w")
   sentences = formatFile(fin, fout)
   print "File:", filename, "contains", sentences, "sentences."
   fin.close()
   fout.close()
