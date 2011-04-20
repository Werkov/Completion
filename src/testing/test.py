#!/usr/bin/python
import sys
import math

def extractSentences(f, start = -1, end = -1):
	f.seek(0)
	if start == -1 and end == -1:
		return f.readlines()
	else:
		sentences = []
		for i, sen in enumerate(f.readlines()):
			if start <= i and i < end:
				sentences.append(sen)
		return sentences

# tests sentences against model
# return no. of tokens (leters), overall cross entropy and overall keystrokes no.
def testSentences(model, sentences, alphabet):
	entropy = 0
	keystrokes = 0
	tokens = 0
	for sentence in sentences:
		sentence = sentence.strip() #remove trailing NL
		pos = 0
		for char in sentence:
			pos += 1
			tokens += 1
			prob = model.getCharProbability(sentence[0:pos], char) # append previous sentence?
			entropy += - math.log(prob, 2) if prob > 0 else float("inf")

			# calculate no. of keystrokes as order in sorted alhabet
			sortedAlphabet = sorted(alphabet, key = lambda(c): model.getCharProbability(sentence[0:pos], c), reverse = 1)
			keystrokes += sortedAlphabet.index(char)
	
	return tokens, entropy, keystrokes
	#TODO: model support for other methods

def simpleTestFile(model, f, start = -1, end = -1):
	return testSentences(model, extractSentences(f, start, end))

def learnModelFromFile(model, f, start = -1, end = -1):
	model.clear()
	for sentence in extractSentences(f, start, end):
		model.addSentence(sentence)

# gets alphabet of unique chars from text
def getAlphabet(text):
   ret = ""
   for char in text:
	 if not char in ret:
	    ret += char
   return ret

if len(sys.argv) < 2:
   print "Usage: test.py modelName [-n groups] file(s) ..."
   sys.exit(1)

modelName = sys.argv[1]
Model = __import__(modelName + "Model")
Model = Model.Model

model = Model()

mode = 0 #0 is simple, 1 is leaving-one-out
groups = 0
args = sys.argv[3:]
files = []

while len(args) > 0:
	arg = args.popleft()
	if arg == "-n":
		mode = 1
		groups = int(args.popleft())
	else:
		files.append(arg)

results = []	#results of single tests (to calculate variance)
if mode == 0:
	for filename in files:
		f = open(filename)
		res = simpleTestFile(model, f)
		results.append(res)
		print "File:", filename
		print "Entropy:", res[1] / res[0]
		print "Keystrokes:", float(res[1] / res[0])
		print
elif mode == 1:
	pass
#TODO do LOO mode

#statistics:
sumN, sumH, sumK = 0, 0, 0
for n, h, k in results:
	sumN, sumH, sumK = sumN + n, sumH + h, sumK + k

#TODO: end statistics

print "Test results: (filename, cross entropy, keystrokes)"
for filename in sys.argv[2:]:
   f = open(filename)
   data = f.read()
   f.close()


   print filename, ":", testText(model, data)




