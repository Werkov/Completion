#!/usr/bin/python
#coding=utf-8

import string
import re
from ILangModel import ILangModel

class AbstractLetterModel (ILangModel):
   counts = {}	  # coutns for letter ngrams
   nCounts = {}	  # counts for whole ngram classes
   alphabetSize = 0
   maxOrder = 0
   begToken = "\\beg"
   
   
   def __init__(self, statsFile):
      f = open(statsFile)

      m = re.match(r"Chars (\d+)\s*(#.*)?", f.readline().strip())
      self.alphabetSize = int(m.group(1))

      m = re.match(r"Order (\d+)\s*(#.*)?", f.readline().strip())
      self.maxOrder = int(m.group(1))

      ngramCounts = [0] * (self.maxOrder + 1) # one wasted item in order to index from 1

      # load counts of unique ngrams
      for i in range(1, self.maxOrder + 1):
	 m = re.match(r"\d+-gram (\d+)\s*(#.*)?", f.readline().strip())
	 ngramCounts[i] = int(m.group(1))

      # load stats for each ngram length
      for i in range(1, self.maxOrder + 1):
	 self.nCounts[i] = 0
	 for j in range(0, ngramCounts[i]):
	    line = f.readline().strip()
	    print line
	    m = re.match(r"(.*) (\d+)\s*(#.*)?", line)
	    cnt = int(m.group(2))
	    self.counts[m.group(1)] = cnt
	    self.nCounts[i] += cnt
	    
      f.close()
            
   
 
   def getCharProbability(self, context, char):
      return self.counts[char] / float(self.nCounts[1]) if char in self.counts else 0
#      context = context[-(self.ngramSize-1):] if self.ngramSize > 1 else ""
#      begTokens = self.ngramSize - len(context) - 1
#
#      preNgram = context + char
#      ngram = self.begToken * begTokens
#      for c in preNgram:
#         ngram += c if c in self.knownTokens else self.unkToken
#
#      return self.probs[ngram]
