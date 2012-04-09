from kenlm import Model, Vocabulary
m = Model("../../../sample-data/povidky.arpa")
print("Got model")
v = m.GetVocabulary()
print("Got vocabulary")
b = m.BeginSentenceState()
print("Got state")
t = v.GetTokens()
