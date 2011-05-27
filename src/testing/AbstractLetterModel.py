#!/usr/bin/python
#coding=utf-8

import codecs
import string
import re
from ILangModel import ILangModel

class AbstractLetterModel (ILangModel):
   counts = {}	  # counts of occurencies for each ngram
   nCounts = {}	  # counts of occurencies for each ngram length
   alphabetSize = 0
#   maxOrder = 0
   begToken = "\\beg"
   
   
   def __init__(self, statsFile):
      f = codecs.open(statsFile, "r", "utf-8")

      m = re.match(r"Chars (\d+)\s*(#.*)?", f.readline().strip())
      self.alphabetSize = int(m.group(1))

#      m = re.match(r"Order (\d+)\s*(#.*)?", f.readline().strip())
#      self.maxOrder = int(m.group(1))

      # load counts of unique ngrams
      ngramCounts = {}
      lenOrder = []

      line = f.readline().strip("\r\n")
      m = re.match(r"(\d+)-gram (\d+)\s*(#.*)?", line)
      while m:
	 ngramCounts[int(m.group(1))] = int(m.group(2))
	 lenOrder.append(int(m.group(1)))

	 line = f.readline().strip("\r\n")
	 m = re.match(r"(\d+)-gram (\d+)\s*(#.*)?", line)

      # load stats for each ngram length
      for len in lenOrder:
	 self.nCounts[len] = 0
	 for j in range(0, ngramCounts[len]):	    
	    m = re.match(r"(.*) (\d+)\s*(#.*)?", line)
	    cnt = int(m.group(2))
	    self.counts[m.group(1)] = cnt
	    self.nCounts[len] += cnt
	    line = f.readline().strip("\r\n")
	    
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
