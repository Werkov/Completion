#!/usr/bin/python
#coding=utf-8

import string
import re
from AbstractLetterModel import AbstractLetterModel

class LetterModel (AbstractLetterModel):
   def getCharProbability(self, context, char):
      l = 0.9  # experimental
      if char in self.counts:
	 return l * self.counts[char] / float(self.nCounts[1])
      else:
	 return (1-l) / (self.alphabetSize - self.knownChars())
