"""
Interacive script

Asks user for words and gives probable suggestions.
Insert one word per row and confirm with <Enter>.
"""
from origin import *

# training data
f = open("../sample-data/povidky.txt")
os = SimpleLangModel(f)
f.close()

oa = LaplaceSmoothLM(os, parameter=0.1)

selector = SuggestionSelector(os.search)
sorter = SuggestionSorter(oa)

# ask user and show him suggestions until empty string is given
M = N-1
buffer = (M) * [""]
word = input("Start: ")
while word != "":
    buffer = buffer[1:M]
    buffer.append(word)
    tips = sorter.getSortedSuggestions(buffer, selector.getSuggestions(buffer))
    print()
    for tip in tips[0:20]:
        print("{}\t\t{}".format(*tip))
    word = input()


