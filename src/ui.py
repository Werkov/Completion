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

class CompletionTextEdit(QtGui.QPlainTextEdit):
    def __init__(self, parent=None):
        super(CompletionTextEdit, self).__init__(parent)
        self.setMinimumWidth(400)
        self.setPlainText("")
        self.completer = None
        self.moveCursor(QtGui.QTextCursor.End)
        self.tokenizer = None
        self.context = (3-1) * [""] # 3 should be global variable from origin

    def setCompleter(self, completer):
        if self.completer:
            self.disconnect(self.completer, 0, self, 0)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer = completer
        #self.completer.activated[QtCore.QModelIndex].connect(self.insertCompletion)
        self.completer.activated[str].connect(self.insertCompletion)
        #self.completer.highlighted[str].connect(self.insertCompletion)
        
    def setTokenizer(self, tokenizer):
        self.tokenizer = tokenizer
    
    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()
    
    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        fillin = completion[-extra:] if extra > 0 else ""
        append = self.completer.acceptChar() if self.completer.acceptChar() != None else " "
        tc.insertText(fillin + append)
        self.setTextCursor(tc)

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self);
        QtGui.QPlainTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (
            QtCore.Qt.Key_Enter,
            QtCore.Qt.Key_Return,
            QtCore.Qt.Key_Escape,
            QtCore.Qt.Key_Tab,
            QtCore.Qt.Key_Backtab):
                event.ignore()
                return

        ## has ctrl-space been pressed??
        isShortcut = (event.modifiers() == QtCore.Qt.ControlModifier and
                      event.key() == QtCore.Qt.Key_Space)
        if (not self.completer or not isShortcut):
            QtGui.QPlainTextEdit.keyPressEvent(self, event)

        ## ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier ,
                QtCore.Qt.ShiftModifier)
        if ctrlOrShift and event.text() == "":
            # ctrl or shift key on it's own
            return


        hasModifier = ((event.modifiers() != QtCore.Qt.NoModifier) and not ctrlOrShift)

        #completionPrefix = self.textUnderCursor()

        self.tokenizer.setCursor(self.textCursor().position())
        tokens, prefix = self.tokenizer.getToken(self.toPlainText())
        for token in tokens:
            if token[0] != Tokenizer.TYPE_WHITESPACE:
                self.context = self.context[1:len(self.context)]
                self.context.append(token[1])
#                tm.add(token[1]) # important control point -- sending words to model

        if prefix == None or prefix[0] == Tokenizer.TYPE_WHITESPACE:
            prefix = None
            completionPrefix = ""
        else:
            prefix = prefix[1]
            completionPrefix = prefix
        
        if (not isShortcut and (hasModifier or event.text() == "" or
        len(completionPrefix) < 0)):
            self.completer.popup().hide()
            return

        if (completionPrefix != self.completer.completionPrefix()):
            self.completer.update(self.context, prefix, self.toPlainText())
            self.completer.setCompletionPrefix(completionPrefix)
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0,0))

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr) ## pop it up!

 

