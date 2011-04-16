#!/usr/bin/python

from ILangModel import ILangModel

statsFile = "a.stats"

class Model:# (ILangModel):
   frequencies = {}
   sum = 0

   def __init__(self):
      self.alphabet = ""
      f = open(statsFile)
      for line in f:
	 line = line.split(" ")
	 self.frequencies[line[0]] = int(line[1])
	 self.sum += int(line[1])
	 
      f.close()

      print self.frequencies

   def setText(self, text):
      pass


   def getCharProbability(self, position, char):
      return self.frequencies[char] / float(self.sum) if char in self.frequencies else 0
