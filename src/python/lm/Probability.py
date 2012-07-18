import collections

class NgramCounter:
    def __init__(self, order = 2):
        self._order = order
        self.reset()

    def reset(self, tokens = []):
        self._context = () # null context
        self._counter = collections.Counter()
        self._len = 0
        for token in tokens:
            self.append(token)


    def append(self, token):
        self._context = self._context + (token,)
        if len(self._context) > self._order:
            self._context = self._context[1:]

        self._len += 1
        for n in range(self._order):
            self._counter[self._context[n:]] += 1

    def __len__(self):
        return self._len

    def __getitem__(self, ngram):
        return self._counter[ngram]
    

