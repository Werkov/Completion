#!/usr/bin/python
from ILangModel import ILangModel

class Model (ILangModel):
   alphabet = ""

   def setText(self, text):
      self.alphabet = ""

      for char in text:
	 if not char in self.alphabet:
	    self.alphabet += char

   def getCharProbability(self, position, char):
      return 1.0 / len(self.alphabet) if char in self.alphabet else 0
