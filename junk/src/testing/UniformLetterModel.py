#!/usr/bin/python
#coding=utf-8

import string
import re
from AbstractLetterModel import AbstractLetterModel

class LetterModel (AbstractLetterModel):
   def getCharProbability(self, context, char):
      return 1.0 / self.alphabetSize
