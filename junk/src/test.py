"""
Runs a set of tests and calculates perplexity.
In this form it tests various values of parameter p
for Laplace smoothing.
"""
from origin import *

# training text
f = open("../sample-data/povidky.txt")
#f = open("../tests/snoubenci.txt")
os = SimpleLangModel(f)
f.close()

# testing text
t = open("../tests/snoubenci.txt")
start = -5 # lower bound for Laplace smoothing parameter (in powers of ten)
end = 1 # upper bound for Laplace smoothing parameter (in powers of ten)
step = 3 # how many steps do between two orders of ten power
p = pow(10, start)
for i in range((end-start)*step + 1):
    oa = LaplaceSmoothLM(os, parameter=p)
    um = NgramLM(oa, 1)
    bm = NgramLM(oa, 2)
    tm = NgramLM(oa, 3)
    metric = EntropyMetric(LinearInterLM([um, bm, tm], [0.8,0.1,0.1]))
    test = AutomatedTest(t)
    test.addMetric(metric)
    test.runTest()
    print("{}\t{}".format(p, metric.getResult()))
    t.seek(0)
    p *= pow(10, 1/step)

t.close()

