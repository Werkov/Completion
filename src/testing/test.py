#!/usr/bin/python
#coding=utf-8
import sys
import codecs
import math
import string
from collections import deque
from numpy import mean
from numpy import var

# tests sentences against model
# @param Model   model
# @param list    sentences
# @param string  alphabet
# @param int     S      penalty in keystrokes for writing unknown symbol
# @param int     C      no. of keystrokes necessary for each symbol
# return no. of tokens (letters), overall cross entropy and overall keystrokes list
def testSentences(model, sentences, alphabet, S, C, verbose = False):
   entropy = []
   keystrokes = []
   tokens = 0
   for sentence in sentences:
      sentence = sentence.strip() #remove trailing NL
      pos = 0
      for char in sentence:
         prob = model.getCharLogProbability(sentence[0:pos], char)         
         entropy.append(-prob / (math.log(2, 10))) # 10 base log to 2 base

         # calculate no. of keystrokes as order in sorted alhabet
         sortedAlphabet = sorted(alphabet, key = lambda(c): model.getCharProbability(sentence[0:pos], c), reverse = 1)
         kst = C

	 
         try:
            kst += sortedAlphabet.index(char)
	    if verbose:
	       print char.encode("utf-8"), "("+format(10**prob, "f")+"): ", string.join(map(lambda(c): c.encode("utf-8"), sortedAlphabet[0:sortedAlphabet.index(char)+1]), ",")
         except ValueError:
            kst += S
	    print char.encode("utf-8"), "("+format(10**prob, "f")+"): ", "not in input alphabet"
	    
	 keystrokes.append(kst)
	 pos += 1
	 tokens += 1

   return tokens, entropy, keystrokes
   
# -- Default configuration --
S = 50
C = 1 # hitting enter
verbose = False

lettersL = u"abcdefghijklmnopqrstuvwxyzěščřžýáíéůúťďň"
lettersU = lettersL.upper()
numbers = "0123456789"
interpunction = ",.?!"
delimiters = " "
alphabet = lettersL + lettersU + delimiters+ interpunction + numbers


# -- Parse command line options and arguments --
if len(sys.argv) < 3:
   print "Usage: test.py modelName statsFile [-s penalty][-c necessary hits][-a alphabet][-v verbose] file(s) ..."
   sys.exit(1)

modelName = sys.argv[1]
statsFile = sys.argv[2]
Model = __import__(modelName + "Model")
Model = Model.LetterModel
#from ArpaModel import ArpaModel

#model = ArpaModel(modelName + ".arpa")
model = Model(statsFile)

args = deque(sys.argv[3:])
files = []

while len(args) > 0:
   arg = args.popleft()
   if arg == "-s":
      S = int(args.popleft())
   elif arg == "-c":
      C = int(args.popleft())
   elif arg == "-a":
      alphabet = args.popleft()
   elif arg == "-v":
      verbose = True
   else:
      files.append(arg)

if len(files) == 0:
   print "No input files given."
   sys.exit(1)
   
results = []	#results of single tests (to calculate variance)
for filename in files:
   f = codecs.open(filename, "r", "utf-8")
   n, h, k = testSentences(model, f.readlines(), alphabet, S, C, verbose)

   results.append((n, h, k))
   print "File:", filename
   print "Tokens:", n
   print "Entropy:", mean(h), "+/-", math.sqrt(var(h))
   print "Keystrokes:", mean(k), "+/-", math.sqrt(var(k))
   print
   f.close()


#statistics:
sumN, sumH, sumK = 0, 0, 0
for n, h, k in results:
   sumN, sumH, sumK = sumN + n, sumH + mean(h), sumK + mean(k)

# average
avgN = mean([res[0] for res in results])
avgH = mean([mean(res[1]) for res in results])
avgK = mean([mean(res[2]) for res in results])

#variance
varN = var([res[0] for res in results])
varH = var([mean(res[1]) for res in results])
varK = var([mean(res[2]) for res in results])

print "Overall test results:"
print "Average tokens: " + str(avgN) + " (variance " + str(varN) +  ")"
print "Average perplexity: " + str(2**avgH) + " (entropy " + str(avgH) + ")"
print "Average keystrokes: " + str(avgK) + " (variance " + str(varK) + ")"
print



