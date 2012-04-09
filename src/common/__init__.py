import sys
sys.path.append("../")

class Trie:
    def __init__(self):
        self.root = self._newNode()


    def _createNode(self, key):
        current = self.root
        for c in key:
            if c not in current[1]:
                current[1][c] = self._newNode()
            current = current[1][c]
        return current

    def _findNode(self, key):
        current = self.root
        for c in key:
            if c not in current[1]:
                return None
            current = current[1][c]
        return current

    def _newNode(self):
        return [None, {}]

    def __setitem__(self, key, data):
        node = self._createNode(key)
        node[0] = data

    def __delitem__(self, key):
        node = self._findNode(key)
        if not node or node[0] == None:
            raise KeyError
        node[0] = None

        if len(self.children(key)) == 0:
            parent = self._findNode(key[:-1])
            del parent[1][key[-1]]

    def __getitem__(self, key):
        node = self._findNode(key)
        if not node or node[0] == None:
            raise KeyError
        return node[0]

    def __contains__(self, key):
        node = self._findNode(key)
        return node != None and node[0] != None

    def __iter__(self):
        return iter(self.children(""))

    def children(self, key):
        node = self._findNode(key)
        if not node:
            raise KeyError
        result=[]
        for n in node[1]:
            if node[1][n][0] != None:
                result.append(key + n)
            result += self.children(key + n)
        return result

