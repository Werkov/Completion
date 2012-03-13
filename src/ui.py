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
        event.ignore()

    def selectionMove(self, shift):
        if self.count() == 0:
            return
        row = self.currentRow()
        print("Current: ", row)
        row += shift
        row = (self.count() + row) % self.count()
        self.setCurrentRow(row)
        

class CompletionTextEdit(QtGui.QPlainTextEdit):
    suggestions = ["mouka", "evoluční", "prokaryotický", "nejstrategičtější", "nejstrašidelnější", "pracný", "prachový", "pomeranč"]
    Popup_Hidden = 0
    Popup_Visible = 1
    Popup_Focused = 2

    UserReason = 0
    InnerReason = 1

    def __init__(self, parent=None):
        super(CompletionTextEdit, self).__init__(parent)
        self.setMinimumWidth(400)
#        self.setPlainText("")
#        self.moveCursor(QtGui.QTextCursor.End)
        self.tokenizer = None
        self._initPopup()
        self.cursorPositionChanged.connect(self._cursorPositionChangedHandler)
        self.cursorMoveReason = self.UserReason
        
    def _initPopup(self):
        self.popup = CompletionListView(self)
        self.setPopupState(self.Popup_Hidden)

    def popupState(self):
        if self.popup.isVisible():
            return self.Popup_Focused if self.popup.hasFocus() else self.Popup_Visible
        else:
            return self.Popup_Hidden
        
    def setPopupState(self, state):
        if state == self.Popup_Hidden:
            self.popup.setVisible(False)
            self.setFocus()
        elif state == self.Popup_Visible:
            self._refreshPopup()
            self.popup.setVisible(True)
            self.setFocus()
        elif state == self.Popup_Focused:
            self._refreshPopup()
            self.popup.setVisible(True)
            self.popup.setFocus()
            if self.popup.count() > 0:
                self.popup.item(0).setSelected(True)
        else:
            raise ValueError()

    def _refreshPopup(self):
        self.popup.move(self.cursorRect().right(), self.cursorRect().bottom())
        self.popup.clear()
        self.popup.addItems(self.currentSuggestions())

    def _cursorPositionChangedHandler(self):
        if self.cursorMoveReason == self.UserReason:
            self.setPopupState(self.Popup_Hidden)
        self.cursorMoveReason = self.UserReason
        
    def setTokenizer(self, tokenizer):
        self.tokenizer = tokenizer

    def currentSuggestions(self):
        # find prefix
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        prefix = tc.selectedText();

        # fill suggestions
        return [w for w in self.suggestions if w.startswith(prefix)]

    def keyPressEvent(self, event):
        handled = False
        if self.popupState() == self.Popup_Hidden:
            # manual invokation
            if event.key() == QtCore.Qt.Key_Space and event.modifiers() & QtCore.Qt.ControlModifier:
                self.setPopupState(self.Popup_Visible)
                handled = True
            elif event.text().isprintable() and event.text() != "":
                self.cursorMoveReason = self.InnerReason
                QtGui.QPlainTextEdit.keyPressEvent(self, event)
                handled = True
                if len(self.currentSuggestions()) > 0:
                    self.setPopupState(self.Popup_Visible)

        elif self.popupState() == self.Popup_Visible:
            # manual hiding
            if event.key() == QtCore.Qt.Key_Escape:
                self.setPopupState(self.Popup_Hidden)
                handled = True
            # selection change
            elif event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_Down:
                if event.key() == QtCore.Qt.Key_Up:
                    self.popup.selectionMove(-1)
                else:
                    self.popup.selectionMove(1)
                self.setPopupState(self.Popup_Focused)
                handled = True
            elif event.text().isprintable() and event.text() != "":
                self.cursorMoveReason = self.InnerReason
                QtGui.QPlainTextEdit.keyPressEvent(self, event)
                handled = True
                if len(self.currentSuggestions()) > 0:
                    self._refreshPopup()
                else:
                    self.setPopupState(self.Popup_Hidden)

        elif self.popupState() == self.Popup_Focused:
            # manual hiding
            if event.key() == QtCore.Qt.Key_Escape:
                self.setPopupState(self.Popup_Hidden)
                handled = True
            # selection change
            elif event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_Down:
                if event.key() == QtCore.Qt.Key_Up:
                    self.popup.selectionMove(-1)
                else:
                    self.popup.selectionMove(1)
                handled = True
            elif self._isAcceptKey(event):
                self.cursorMoveReason = self.InnerReason
                self._acceptSuggestion()
                handled = True
                if len(self.currentSuggestions()) > 0:
                    self.setPopupState(self.Popup_Visible)
                else:
                    self.setPopupState(self.Popup_Hidden)
            elif event.text().isprintable() and event.text() != "":
                self.cursorMoveReason = self.InnerReason
                QtGui.QPlainTextEdit.keyPressEvent(self, event)
                handled = True
                if len(self.currentSuggestions()) > 0:
                    self._refreshPopup()
                else:
                    self.setPopupState(self.Popup_Hidden)

        if not handled:
            QtGui.QPlainTextEdit.keyPressEvent(self, event)

    def _isAcceptKey(self, event):
        return event.key() in [QtCore.Qt.Key_Tab, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]

    def _acceptSuggestion(self):
        tc = self.textCursor()
        tc.insertText(self.popup.currentItem().text())
        self.setTextCursor(tc)

