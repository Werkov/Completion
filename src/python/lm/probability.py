import collections

class NgramCounter:
    def __init__(self, order=2):
        self._order = order
        self.reset()

    def reset(self, tokens=[]):
        self._context = () # null context
        self._counter = collections.Counter()
        self._len = 0
        self._vocabulary = set()
        for token in tokens:
            self.append(token)

    def nullContext(self):
        self._context = ()

    def append(self, token):
        self.shift(token)
        self._len += 1
            
    def shift(self, token):
        self._context = self._context + (token, )
        if len(self._context) > self._order:
            self._context = self._context[1:]
        for n in range(self._order):
            self._counter[self._context[n:]] += 1
        self._vocabulary.add(token)


    def __len__(self):
        return self._len

    def __getitem__(self, ngram):
        return self._counter[ngram]

    def items(self):
        return self._counter.items()

    def vocabulary(self):
        return self._vocabulary

    def __repr__(self):
        return self._counter.__repr__()
    

