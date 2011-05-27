#!/usr/bin/python
#coding=utf-8

import codecs
import re
from ILangModel import ILangModel

class AbstractLetterModel (ILangModel):
   counts = {}	  # counts of occurencies for each ngram
   nCounts = {}	  # counts of occurencies for each ngram length
   nUCounts = {}  # counts of unique ngrams occurencies for each length
   alphabetSize = 0
   begToken = "\\beg"
   
   
   def __init__(self, statsFile):
      f = codecs.open(statsFile, "r", "utf-8")

      m = re.match(r"Chars (\d+)\s*(#.*)?", f.readline().strip())
      self.alphabetSize = int(m.group(1))

      # load counts of unique ngrams
      lenOrder = []

      line = f.readline().strip("\r\n")
      m = re.match(r"(\d+)-gram (\d+)\s*(#.*)?", line)
      while m:
	 self.nUCounts[int(m.group(1))] = int(m.group(2))
	 lenOrder.append(int(m.group(1)))

	 line = f.readline().strip("\r\n")
	 m = re.match(r"(\d+)-gram (\d+)\s*(#.*)?", line)

      # load stats for each ngram length
      for len in lenOrder:
	 self.nCounts[len] = 0
	 for j in range(0, self.nUCounts[len]):
	    m = re.match(r"(.*) (\d+)\s*(#.*)?", line)
	    cnt = int(m.group(2))
	    self.counts[m.group(1)] = cnt
	    self.nCounts[len] += cnt
	    line = f.readline().strip("\r\n")
	    
      f.close()
            
   def knownChars(self):
      return self.nUCounts[1] if 1 in self.nUCounts else 0