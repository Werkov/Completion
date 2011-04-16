#!/usr/bin/python

class ILangModel:
   # sets text used for testing the model
   def setText(self, text):
      return self

   # gets the probability of char @char at @position
   # in using history before @position from text
   def getCharProbability(self, position, char):
      return 0
