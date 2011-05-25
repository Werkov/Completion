#!/usr/bin/python
#coding=utf-8

import string
import re
from ILangModel import ILangModel

class ArpaModel (ILangModel):
   probs = {}
   knownTokens = {}
   ngramSize = -1
   begToken = "\\beg"
   unkToken = "\\unk"
   
   def __init__(self, arpaFile):
      f = open(arpaFile)
      # Modes:
      # 0 waiting for summary
      # 1 reading summary
      # 2 reading stats
      # 3 end reading
      mode = 0      
      ngramCnt = 0
      
      
      for line in f:
         line = line.strip()
         
         if mode == 0:
            if line == "\\data\\":
               mode = 1
         elif mode == 1:
            if self.ngramSize == -1:
               m = re.match(r"ngram (\d+)=(\d+)", line)
               self.ngramSize = int(m.group(1))
               ngramCnt = int(m.group(2))
            else:
               if line == "\\" + str(self.ngramSize) + "-grams:":
                  mode = 2
         elif mode == 2:            
            m = re.match(r"([\d\.\-]+) +(.+)", line)
            if not m:
               mode = 3
               continue
            prob = float(m.group(1))
            tokens = m.group(2)
            ngram = ""
            for token in re.split(r"\s", tokens):
               self.knownTokens[token] = True
               ngram += token
            
            self.probs[ngram] = prob            
         else:
            break
      
      f.close()
            
   
   def getCharProbability(self, context, char):
      log = self.getCharLogProbability(context, char)
      return 0 if log == float("-inf") else 10**log
   
   def getCharLogProbability(self, context, char):
      context = context[-(self.ngramSize-1):] if self.ngramSize > 1 else ""
      begTokens = self.ngramSize - len(context) - 1
      
      preNgram = context + char
      ngram = self.begToken * begTokens
      for c in preNgram:
         ngram += c if c in self.knownTokens else self.unkToken
         
      return self.probs[ngram]
