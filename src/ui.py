import sys

from PyQt4 import QtCore
from PyQt4 import QtGui
from origin import *

# training data
#f = open("../sample-data/povidky.txt")
#os = SimpleLangModel(f)
#f.close()
#
#oa = LaplaceSmoothLM(os, parameter=0.1)

tm = SimpleTriggerModel()
klm = KenLMModel("../sample-data/povidky.arpa")

#selector = SuggestionSelector(dict=tm.dictionary)
#sorter = SuggestionSorter(tm)

selector = SuggestionSelector(dict=klm.dictionary)
sorter = SuggestionSorter(klm)


# ask user and show him suggestions until empty string is given

class TextInputTokenizer(Tokenizer):
    
    def __init__(self):
        super(TextInputTokenizer, self).__init__()
        self.lastTokenEnd = 0

    def getToken(self, text):
        tokens = []
        token = None
        tokenEnd = self.lastTokenEnd
        while tokenEnd < len(text):
            token = self._getToken(text, self.lastTokenEnd)
            tokenEnd = len(token[1]) + tokenEnd
            if tokenEnd < len(text):
                tokens.append(token)
                self.lastTokenEnd = tokenEnd
            
        return tokens, token


class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.initUI()
        self.show()
    def initUI(self):
        # window itself
        self.resize(640, 480)
        self.center()
        self.setWindowTitle('Completion test')

        # debugging info
        self.dbg = DebugTrace(self)
        self.dbg.move(0, 220)
        self.dbg.resize(640, 200) # find different solution

        # text input
        self.txtInput = Autocomplete(self, self.dbg)
        self.txtInput.resize(640, 200)

        
        
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

class DebugTrace(QtGui.QListWidget):
    def __init__(self, parent):
        super(DebugTrace, self).__init__(parent)
        self.keyToRow = {}
        
    def printInfo(self, key, value):
        if key in self.keyToRow:
            self.item(self.keyToRow[key]).setText(key + ": " + str(value))
        else:
            self.addItem(key + ": " + str(value))
            self.keyToRow[key] = self.count() - 1

class Autocomplete(QtGui.QTextEdit):
    def __init__(self, parent, debugTrace = None):
        super(Autocomplete, self).__init__(parent)
        self.initUI();
        self.tokenizer = TextInputTokenizer()
        self.context = (N-1) * [""] # global variable from origin
        self.debugTrace = debugTrace

    def keyPressEvent(self, e):
        super(Autocomplete, self).keyPressEvent(e)        
        self.lstSuggestions.move(self.cursorRect().left(), self.cursorRect().top() + self.cursorRect().height())

        tokens, prefix = self.tokenizer.getToken(self.toPlainText())
        for token in tokens:
            if token[0] != Tokenizer.TYPE_WHITESPACE:
                self.context = self.context[1:len(self.context)]
                self.context.append(token[1])
                tm.add(token[1])

        if prefix == None or prefix[0] == Tokenizer.TYPE_WHITESPACE:
            prefix = None
        else:
            prefix = prefix[1]

        if self.debugTrace != None:
            self.debugTrace.printInfo("context", self.context)
            self.debugTrace.printInfo("prefix", prefix)
        
            
        tips = sorter.getSortedSuggestions(self.context, selector.getSuggestions(self.context, prefix))
        self.lstSuggestions.clear()
        if len(tips) > 0:            
            for tip in tips[0:20]:
                self.lstSuggestions.addItem("{}\t\t{}".format(*tip))
            self.lstSuggestions.setVisible(True)
        else:
            self.lstSuggestions.setVisible(False)
        

    def initUI(self):
        self.lstSuggestions = QtGui.QListWidget(self)        
        self.lstSuggestions.setVisible(False)


def main():
    app = QtGui.QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
