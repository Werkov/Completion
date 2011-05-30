#!/usr/bin/python
#coding=utf-8

import string
import re
from AbstractLetterModel import AbstractLetterModel

class AbstractNgramLetterModel (AbstractLetterModel):
   # "abstract property"
   # order  order of ngram (1 for unigram)

   # "abstract property"
   # lCoeff  how much we add to unseen tokens

   def getCharProbability(self, context, char):
      context = self.alignContext(context, self.order - 1)
      ngram = context + char

#      if not ngram in self.counts:
#	 return 0
#      else:
#	 return (self.counts[ngram]) / (float(self.counts[context]))

      
      cn = float(self.counts[ngram] if ngram in self.counts else 0)
      nn = self.nCounts[self.order]
      bn = self.alphabetSize ** self.order
      
      cc = float(self.counts[context] if context in self.counts else 0)
      nc = self.nCounts[self.order-1]
      bc = self.alphabetSize ** (self.order-1)
      
      return ((cn + self.lCoeff) / (nn + self.lCoeff*bn)) * ((nc + self.lCoeff*bc) / (cc + self.lCoeff))
