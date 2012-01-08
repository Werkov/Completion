from kenlm import Model
m = Model("../../../sample-data/povidky.arpa")
v = m.GetVocabulary()
print("Try v.Index(<string>) for lookup in KenLM vocabulary")
