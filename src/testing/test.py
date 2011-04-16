#!/usr/bin/python
import sys
import math

# gets alphabet of unique chars from text
def getAllphabet(text):
   ret = ""
   for char in text:
	 if not char in ret:
	    ret += char
   return ret

def testText(model, text):

   entropy = 0
   keystrokes = 0
   position = 0
   alphabet = getAllphabet(text)
   model.setText(data)

   for char in data:
      prob = model.getCharProbability(position, char)
      entropy += - math.log(prob, 2) if prob > 0 else float("inf")

      # calculate no. of keystrokes as order in sorted alhabet
      sortedAlphabet = sorted(alphabet, key = lambda(c): model.getCharProbability(position, c), reverse = 1)
      keystrokes += sortedAlphabet.index(char)
      
      position += 1

   # normalize per char
   entropy /= len(text)
   keystrokes /= float(len(text))

   return entropy, keystrokes


if len(sys.argv) < 2:
   print "Usage: test.py modelName testData ..."
   sys.exit(1)

modelName = sys.argv[1]
Model = __import__(modelName + "Model")
Model = Model.Model

model = Model()

print "Test results: (filename, cross entropy, keystrokes)"
for filename in sys.argv[2:]:
   f = open(filename)
   data = f.read()
   f.close()


   print filename, ":", testText(model, data)



