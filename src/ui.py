import sys

from PyQt4 import QtCore
from PyQt4 import QtGui
from origin import Tokenizer

class TextInputTokenizer(Tokenizer):

    def __init__(self):
        super(TextInputTokenizer, self).__init__()
        self.lastTokenEnd = 0
    def setCursor(self, position):
        self.lastTokenEnd = min(self.lastTokenEnd, position)

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
    

class DictionaryCompleter(QtGui.QCompleter):
    _acceptChar = None
    LABEL_COL = 0
    TEXT_COL = 1
    PARTIAL_COL = 2
    def __init__(self, parent=None, sorter=None, selector=None):
        QtGui.QCompleter.__init__(self, QtGui.QStandardItemModel(), parent)
        self.setCompletionColumn(self.TEXT_COL)
        self.sorter = sorter
        self.selector = selector

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.KeyPress and self.popup().isVisible():
            if event.text() != "" and event.text() in " ,.:;\"'?!":
                curIndex = self.popup().currentIndex()
                if curIndex.row() > 0:
                    self._acceptChar = event.text()
                    self._q_complete(curIndex)                    
                    return False
            else:
                self._acceptChar = None

        return QtGui.QCompleter.eventFilter(self, object, event)
    
    def acceptChar(self):
        return self._acceptChar

    def update(self, context, prefix, text):
        print(context); print(prefix)
        model = QtGui.QStandardItemModel()#self.model()
        if prefix == "pokor":
            print("own")
            item = QtGui.QStandardItem("{}\t{:.2f}".format("pokorword", 80))
            item2 = QtGui.QStandardItem("pokorpecka")
            model.setItem(0, self.LABEL_COL, item)
            model.setItem(0, self.TEXT_COL, item2)
            row = 1
        else:
            row = 0
            
        for word, prob in self.sorter.getSortedSuggestions(context, self.selector.getSuggestions(context, prefix)):
            item = QtGui.QStandardItem("{}\t{:.2f}".format(word, prob))
            item2 = QtGui.QStandardItem(word)
            model.setItem(row, self.LABEL_COL, item)
            model.setItem(row, self.TEXT_COL, item2)
            row += 1
        
        self.setModel(model)
        self.popup().setModelColumn(self.LABEL_COL)

class CompletionListView(QtGui.QListWidget):
    def keyPressEvent(self, event):
        event.ignore() # send it higher

class CompletionTextEdit(QtGui.QPlainTextEdit):
    suggestions = ["mouka", "evoluční", "prokaryotický", "nejstrategičtější", "nejstrašidelnější", "pracný", "prachový", "pomeranč"]
    def __init__(self, parent=None):
        super(CompletionTextEdit, self).__init__(parent)
        self.setMinimumWidth(400)
#        self.setPlainText("")
#        self.moveCursor(QtGui.QTextCursor.End)
        self.tokenizer = None
        self.popup = CompletionListView(self)
        self.popup.addItem("xerxes")
        self.popup.addItem("yerxes")
        self.popup.addItem("zerxes")
        self.popup.addItem("aerxes")
        self.popup.setVisible(False)
        
        
    def setTokenizer(self, tokenizer):
        self.tokenizer = tokenizer
    

    def keyPressEvent(self, event):
        QtGui.QPlainTextEdit.keyPressEvent(self, event)
        # find prefix
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        prefix = tc.selectedText();

        # fill suggestions
        suggestions = [w for w in self.suggestions if w.startswith(prefix)]
        if len(suggestions) == 0:
            self.popup.setVisible(False)
            return

        self.popup.clear()
        for w in suggestions:
            self.popup.addItem(w)
        self.popup.setVisible(True)

        first = suggestions[0]
        cursor = self.textCursor()
        cursor.insertText(first[len(prefix):])
        cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, len(first)-len(prefix))
        self.setTextCursor(cursor)

        
        self.popup.move(self.cursorRect().right(), self.cursorRect().bottom())
        print("Key: {}".format(prefix))

 

