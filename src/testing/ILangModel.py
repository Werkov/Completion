#!/usr/bin/python

class ILangModel:
   # sets text used for testing the model
   def setText(self, text):
      pass

   # gets the probability of char @char at @position
   # in using history before @position from text
   def getCharProbability(self, position, char):
      pass
