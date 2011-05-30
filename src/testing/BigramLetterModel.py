#!/usr/bin/python
#coding=utf-8

import string
import re
from AbstractLetterModel import AbstractLetterModel

class LetterModel (AbstractLetterModel):
   def getCharProbability(self, context, char):
      context = self.alignContext(context, 1)
      ngram = context + char

#      if not ngram in self.counts:
#	 return 0
#      else:
#	 return (self.counts[ngram]) / (float(self.counts[context]))

      l = 0.9
      cn = float(self.counts[ngram] if ngram in self.counts else 0)
      nn = self.nCounts[2]
      bn = self.alphabetSize ** 2
      
      cc = float(self.counts[context] if context in self.counts else 0)
      nc = self.nCounts[1]
      bc = self.alphabetSize ** 1
      
      return ((cn + l) / (nn + l*bn)) * ((nc + l*bc) / (cc + l))
