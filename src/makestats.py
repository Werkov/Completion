#!/usr/bin/python
import sys

from collections import deque


class Reader:
   line = deque()
   f = None
   def __init__(self, filename):
      self.f = open(filename)
		
   def __del__(self):
      self.f.close()
		
   def getToken(self, word=1):
      if word:
	 return self.getWordToken()
      else:
	 return self.f.read(1)
	
   def getWordToken(self):
      while len(self.line) == 0:
	 curLine = self.f.readline()
	 if curLine == "":
	    return ""
	 #str.split(curLine, " ")
	 w = curLine.split(" ")
	 while "" in w: w.remove("")
	 self.line = deque(w)
	 
	
      return self.line.popleft()


args = deque(sys.argv[1:])
files = []  #files to process
n = 1
mode = 0  #0- letters, 1 words

while len(args) > 0:
   par = args.popleft()
   if par == "-n":
      n = int(args.popleft())
   elif par == "-w":
      mode = 1
   elif par == "-h":
      print "Usage: makestats [-w] [-n number] files ..."
      exit()
   else:
      files.append(par)


stats = dict()
tokensCnt = 0
filesCnt = 0

for filename in files:
   filesCnt += 1
   buffer = deque([""] * n)   

   r = Reader(filename)
   token = r.getToken(mode)
   while token != "":
      tokensCnt += 1
      if str.strip(token) == "":
	 token = r.getToken(mode)
	 continue
      buffer.append((" " if mode else "") + token)
      buffer.popleft()

      key = ""
      for t in buffer:
	 key += t

      if key in stats:
	 stats[key] += 1
      else:
	 stats[key] = 1

      token = r.getToken(mode)


ngrams = sorted(stats.items(), key=lambda item: item[1])
ngrams.reverse()

out = open("a.stats", "w")
for ngram in ngrams:
   out.write(ngram[0] + " " + str(ngram[1]) + "\n")
	
out.close()

print "Files processed: ", filesCnt
print "Tokens processed: ", tokensCnt