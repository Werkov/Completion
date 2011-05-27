#!/usr/bin/python

import sys
import codecs

from collections import deque
from string import join

# default configuration
n = 3	    # maximum ngram order
alphabetSize = 0     # size of the alphabet, 0 is replaced with no. of unique unigrams
minCount = 1	     # no. of minimal occurencies of ngram to include it into statsfile
output = "a.stats"   # name of output file


class Reader:
   f = None
   line = unicode(u"")
   begToken = "\\beg"   # token to mark begining of the text
   newSentence = begToken

   def __init__(self, filename):
      self.f = codecs.open(filename, "r", "utf-8")
		
   def __del__(self):
      self.f.close()
		
   def getToken(self):
      nl = False
      while len(self.line) == 0:
	 rawLine = self.f.readline()
	 if rawLine == "":
	    return ""
	 
	 self.line = rawLine.strip()
	 nl = True	 

      if nl:
	 return self.newSentence

      c = self.line[0]
      self.line = self.line[1:]
      
      return c
	


args = deque(sys.argv[1:])
files = []  # files to process


while len(args) > 0:
   par = args.popleft()
   if par == "-n":
      n = int(args.popleft())
   elif par == "-a":
      alphabetSize = int(args.popleft())
   elif par == "-o":
      output = args.popleft()
   elif par == "-m":
      minCount = int(args.popleft())
   elif par == "-h":
      print "Usage: charstats [-n number] [-a alphabetSize] [-m minCount] [- output] files ..."
      exit(1)
   else:
      files.append(par)


stats = [{} for i in range(0, n)]   # [{}] * n does shallow copies of dictionary
tokensCnt = 0
filesCnt = 0

for filename in files:
   filesCnt += 1   

   r = Reader(filename)
   token = r.getToken()
   while token != "":
      if token == Reader.newSentence:
	 buffer = [Reader.begToken] * n
	 token = r.getToken()
	 continue
	 
      tokensCnt += 1
      buffer.append(token)
      buffer = buffer[1:]

      for length in range(1, n + 1):
	 key = join(buffer[-length:], "")

	 if key in stats[length-1]:
	    stats[length-1][key] += 1
	 else:
	    stats[length-1][key] = 1

      token = r.getToken()

ngrams = [[]] * n
for length in range(1, n + 1):
   ngrams[length-1] = filter(lambda item: item[1] >= minCount, sorted(stats[length-1].items(), key=lambda item: item[1]))
   ngrams[length-1].sort(key=lambda item: item[1])
   ngrams[length-1].reverse()


alphabetSize = len(ngrams[0]) + 1 if alphabetSize == 0 else alphabetSize # +1 for begining token


out = codecs.open(output, "w", "utf-8")

# write header
out.write("Chars " + str(alphabetSize) + "\n")

for length in range(1, n + 1):
   out.write(str(length) + "-gram " + str(len(ngrams[length-1])) + "\n")

# write counts
for length in range(1, n + 1):
   for ngram in ngrams[length-1]:
      out.write(ngram[0] + " " + str(ngram[1]) + "\n")
	
out.close()


print "Files processed: ", filesCnt
print "Tokens processed: ", tokensCnt