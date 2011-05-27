#!/usr/bin/python
import math

class ILangModel:
   # gets the probability that @char follows
   # the given @context
   #return double
   def getCharProbability(self, context, char):
      return 0
   
   # gets the probability that @char follows
   # the given @context as 10 base logarithm
   #return double
   def getCharLogProbability(self, context, char):
      prob = self.getCharProbability(context, char)
      return math.log(prob, 10) if prob > 0 else float("-inf")
