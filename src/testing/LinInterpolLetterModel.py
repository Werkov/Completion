#!/usr/bin/python
#coding=utf-8

import string
import re
from AbstractNgramLetterModel import AbstractNgramLetterModel
from numpy import dot

class LetterModel (AbstractNgramLetterModel):


   def getCharProbability(self, context, char):
      uniform = 1.0 / (self.alphabetSize - self.knownChars())

      # list of linear combination coefficients
      coeffs = [0.0, 0.05, 0.8, 0.15]

      # list of linear combination values
      probs = [uniform]

      for i in range(1,len(coeffs)):
	 self.order = i
	 self.lCoeff = 0.5
	 probs.append(super(LetterModel, self).getCharProbability(context, char))
	 
#      print probs
      return dot(coeffs, probs)