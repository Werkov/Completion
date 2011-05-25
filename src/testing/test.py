#!/usr/bin/python
#coding=utf-8
import sys
import math
from collections import deque

# tests sentences against model
# @param Model   model
# @param list    sentences
# @param string  alphabet
# @param int     S      penalty in keystrokes for writing unknown symbol
# @param int     C      no. of keystrokes necessary for each symbol
# return no. of tokens (letters), overall cross entropy and overall keystrokes no.
def testSentences(model, sentences, alphabet, S, C):
   entropy = 0
   keystrokes = 0
   tokens = 0
   for sentence in sentences:
      sentence = sentence.strip() #remove trailing NL
      pos = 0
      for char in sentence:
         prob = model.getCharProbability(sentence[0:pos], char)
         pos += 1
         tokens += 1         
         entropy += - math.log(prob, 2) if prob > 0 else float("inf")

         # calculate no. of keystrokes as order in sorted alhabet
         sortedAlphabet = sorted(alphabet, key = lambda(c): model.getCharProbability(sentence[0:pos], c), reverse = 1)
         keystrokes += C
         try:
            keystrokes += sortedAlphabet.index(char)
         except ValueError:
            keystrokes += S

   return tokens, entropy, keystrokes
   
# -- Default configuration --
S = 50
C = 1 # hitting enter

lettersL = "abcdefghijklmnopqrstuvwxyzěščřžýáíéůúťďň"
lettersU = lettersL.upper()
interpunction = ",."
delimiters = " "
alphabet = lettersL + lettersU + interpunction + delimiters


# -- Parse command line options and arguments --
if len(sys.argv) < 2:
   print "Usage: test.py modelName file(s) ..."
   sys.exit(1)

modelName = sys.argv[1]
Model = __import__(modelName + "Model")
Model = Model.Model

model = Model()

args = deque(sys.argv[2:])
files = []

while len(args) > 0:
   arg = args.popleft()
   if arg == "-s":
      S = int(args.popleft())
   elif arg == "-c":
      C = int(args.popleft())
   elif arg == "-a":
      alphabet = args.popleft()
   else:
      files.append(arg)

if len(files) == 0:
   print "No input files given."
   exit(1)
   
results = []	#results of single tests (to calculate variance)
for filename in files:
   f = open(filename)
   n, h, k = testSentences(model, f.readlines(), alphabet, S, C)
   results.append((n, h, k))
   print "File:", filename
   print "Tokens:", n
   print "Entropy:", h / n
   print "Keystrokes:", float(k) / n
   print
   f.close()


#statistics:
sumN, sumH, sumK = 0, 0, 0
for n, h, k in results:
   sumN, sumH, sumK = sumN + n, sumH + h/n, sumK + float(k)/n

# average
avgN, avgH, avgK = 0, 0, 0
avgN, avgH, avgK = float(sumN) / len(results), sumH / len(results), float(sumK) / len(results)

#variance
tmpN, tmpH, tmpK = 0, 0, 0
for n, h, k in results:
   tmpN, tmpH, tmpK = (avgN - n)**2, (avgH - h/n)**2, (avgK - float(k)/n)**2
varN, varH, varK = tmpN / len(results), tmpH / len(results), tmpK / len(results)

print "Overall test results:"
print "Average tokens: " + str(avgN) + " (variance " + str(varN) +  ")"
print "Average entropy: " + str(avgH) + " (variance " + str(varH) + ")"
print "Average keystrokes: " + str(avgK) + " (variance " + str(varK) + ")"
print



