import sys

from PyQt4 import QtCore
from PyQt4 import QtGui
from origin import Tokenizer

class StringTokenizer(Tokenizer):
    """Parse string into list of tokens."""
    def __init__(self):
        super(StringTokenizer, self).__init__()

    def tokenize(self, text):
        position = 0
        tokens = []
        token = self._getToken(text, position)
        while token != None:
            tokens.append(token)
            position += len(token[1])
            token = self._getToken(text, position)
        return tokens
    


class CompletionListView(QtGui.QListWidget):
    def keyPressEvent(self, event):
        event.ignore()

    def selectionMove(self, shift):
        if self.count() == 0:
            return
        row = self.currentRow() + shift
        row = (self.count() + row) % self.count()
        self.setCurrentRow(row)
        

class CompletionTextEdit(QtGui.QPlainTextEdit):
    Popup_Hidden = 0
    Popup_Visible = 1
    Popup_Focused = 2

    UserReason = 0
    InnerReason = 1

    Role_Data = QtCore.Qt.UserRole
    Role_Probability = Role_Data + 1
    Role_Partial = Role_Data + 2

    acceptBasicSet = ",.:;\"'?!"

#    TODO data for trigger models
#    tokenAppended = QtCore.pyqtSignal(tuple) # arg. is appended token
#    textMassivelyChanged = QtCore.pyqtSignal(int) # arg. is current position of cursor


    def __init__(self, parent=None):
        super(CompletionTextEdit, self).__init__(parent)
        self.tokenizer = None
        self.selector = None
        self.sorter = None
        self.contextLength = 3
        self._initPopup()
        self.lastTokenAppendedPosition = None
        self.cursorPositionChanged.connect(self._cursorPositionChangedHandler)
        #TODO data for trigger models # self.textChanged.connect(self._textChangedHandler)
        self.cursorMoveReason = self.UserReason
        
    def _initPopup(self):
        self.popup = CompletionListView(self)
        self.popup.itemClicked.connect(self._popupItemClickedHandler)
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
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.MoveAnchor, len(self._prefix()))
        self.popup.move(self.cursorRect(tc).right(), self.cursorRect(tc).bottom())

        self.popup.clear()
        for suggestion, probability in self._currentSuggestions():
            item = QtGui.QListWidgetItem()
            item.setData(self.Role_Data, suggestion)
            item.setData(self.Role_Partial, False)
            item.setData(QtCore.Qt.DisplayRole, "{}\t{:.2f}".format(suggestion, probability))
            self.popup.addItem(item)


    def _cursorPositionChangedHandler(self):
        if self.cursorMoveReason == self.UserReason:
            self.setPopupState(self.Popup_Hidden)
        self.cursorMoveReason = self.UserReason

#    TODO data for trigger models
#    def _textChangedHandler(self):
#        cursorPosition = self.textCursor().position()
#        if cursorPosition == len(self.toPlainText()):
#            if self.lastTokenAppendedPosition == None:
#                self.lastTokenAppendedPosition = self._lastTokenPosition()
#                self.tokenAppended.emit(self._getContext()[-1])
#            elif self.lastTokenAppendedPosition != self._lastTokenPosition():
#                self.lastTokenAppendedPosition = self._lastTokenPosition()
#                self.tokenAppended.emit(self._getContext()[-1])
#        else:
#            self.textMassivelyChanged.emit(cursorPosition)
#            self.lastTokenAppendedPosition = None

    def _popupItemClickedHandler(self, item):
        self._acceptSuggestion(None)
        
    def _currentSuggestions(self):
        # TODO grouping here
        context = [""]*(self.contextLength - len(self._context())) + [token[1] for token in self._context()]
        prefix = None if self._prefix() == "" else self._prefix()
        return self.sorter.getSortedSuggestions(context, self.selector.getSuggestions(context, prefix))

    def _prefix(self):
        tail = self._tail()
        if len(tail) == 0 or tail[-1][0] == Tokenizer.TYPE_WHITESPACE:
            return ""
        else:
            return tail[-1][1] # return string only

    def _context(self):
        tail = self._tail()
        if len(tail) == 0:
            return []
        
        if tail[-1][0] == Tokenizer.TYPE_WHITESPACE:
            return [token for token in tail if token[0] != Tokenizer.TYPE_WHITESPACE][-self.contextLength:]
        else:
            return [token for token in tail[:-1] if token[0] != Tokenizer.TYPE_WHITESPACE][-self.contextLength:]

    def _tail(self):
        tc = self.textCursor()
        # contextLength is in own tokens, therefore we take k-times more words (word + whitespace + reserve)
        tc.movePosition(QtGui.QTextCursor.WordLeft, QtGui.QTextCursor.KeepAnchor, self.contextLength * 3)
        return self.tokenizer.tokenize(tc.selectedText())
        
#    TODO trigger base model data push
#    def _lastTokenPosition(self):
#        """Return position behind last character of last token before cursor."""
#        tail = self._getTail()
#        if len(tail) == 0:
#            return 0
#        else:
#            cursorPosition = self.textCursor().position()
#            if tail[-1][0] == Tokenizer.TYPE_WHITESPACE:
#                return cursorPosition - len(tail[-1][1])
#            else:
#                return cursorPosition

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
                if len(self._currentSuggestions()) > 0:
                    self.setPopupState(self.Popup_Visible)

        elif self.popupState() == self.Popup_Visible:
            # manual hiding
            if event.key() == QtCore.Qt.Key_Escape:
                self.setPopupState(self.Popup_Hidden)
                handled = True
            # selection change
            elif event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_Down: #TODO pgup/down
                if event.key() == QtCore.Qt.Key_Up:
                    self.popup.selectionMove(-1)
                else:
                    self.popup.selectionMove(1)
                self.setPopupState(self.Popup_Focused)
                handled = True
            elif self._isFastAcceptKey(event):
                self._acceptSuggestion(event)
                handled = True
                if len(self._currentSuggestions()) > 0:
                    self.setPopupState(self.Popup_Visible)
                else:
                    self.setPopupState(self.Popup_Hidden)
            elif event.text().isprintable() and event.text() != "":
                self.cursorMoveReason = self.InnerReason
                QtGui.QPlainTextEdit.keyPressEvent(self, event)
                handled = True
                if len(self._currentSuggestions()) > 0:
                    self._refreshPopup()
                else:
                    self.setPopupState(self.Popup_Hidden)

        elif self.popupState() == self.Popup_Focused:
            # manual hiding
            if event.key() == QtCore.Qt.Key_Escape:
                self.setPopupState(self.Popup_Hidden)
                handled = True
            # selection change
            elif event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_Down: #TODO pgup/down
                if event.key() == QtCore.Qt.Key_Up:
                    self.popup.selectionMove(-1)
                else:
                    self.popup.selectionMove(1)
                handled = True
            elif self._isAcceptKey(event):
                self._acceptSuggestion(event)
                handled = True
                if len(self._currentSuggestions()) > 0:
                    self.setPopupState(self.Popup_Visible)
                else:
                    self.setPopupState(self.Popup_Hidden)
            elif event.text().isprintable() and event.text() != "":
                self.cursorMoveReason = self.InnerReason
                QtGui.QPlainTextEdit.keyPressEvent(self, event)
                handled = True
                if len(self._currentSuggestions()) > 0:
                    self._refreshPopup()
                else:
                    self.setPopupState(self.Popup_Hidden)

        if not handled:
            QtGui.QPlainTextEdit.keyPressEvent(self, event)
        print(self._context(), ": ", self._prefix())


    def _isAcceptKey(self, keyEvent):
        return keyEvent.key() in [QtCore.Qt.Key_Tab, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Space] \
            or (keyEvent.text() != "" and keyEvent.text() in self.acceptBasicSet)

    def _isFastAcceptKey(self, keyEvent):
        return keyEvent.key() in [QtCore.Qt.Key_Tab]

    def _acceptSuggestion(self, keyEvent):
        """keyEvent can be none in case of invoking accept by mouse"""
        chosenItem = self.popup.currentItem() if self.popup.currentItem() else self.popup.item(0)
        prefix = self._prefix()
        
        if chosenItem.data(self.Role_Partial):
            appendix = ""
        elif keyEvent == None or keyEvent.text() == " ": # mouse or space
            appendix = " "
        elif keyEvent.text() in self.acceptBasicSet:
            appendix = keyEvent.text() + " "
        else:
            appendix = " "
        
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, len(prefix))
        tc.insertText(chosenItem.data(self.Role_Data) + appendix)
        self.cursorMoveReason = self.InnerReason
        self.setTextCursor(tc)

