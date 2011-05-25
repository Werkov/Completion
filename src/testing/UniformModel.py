#!/usr/bin/python
#coding=utf-8

import string
from ILangModel import ILangModel

class Model (ILangModel):
   alphabet = string.ascii_letters + " ,."
   
   def getCharProbability(self, context, char):
      return 1.0 / len(self.alphabet) if char in self.alphabet else 0
