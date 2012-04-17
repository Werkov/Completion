from PyQt4 import QtCore
from PyQt4 import QtGui

from common.Tokenize import Tokenizer


    


class ListView(QtGui.QListWidget):
    def keyPressEvent(self, event):
        event.ignore()

    def selectionMove(self, shift):
        if self.count() == 0:
            return
        row = self.currentRow() + shift
        row = (self.count() + row) % self.count()
        self.setCurrentRow(row)
        

class TextEdit(QtGui.QPlainTextEdit):
    Popup_Hidden = 0
    Popup_Visible = 1
    Popup_Focused = 2

    UserReason = 0
    InnerReason = 1

    Role_Data = QtCore.Qt.UserRole
    Role_Probability = Role_Data + 1
    Role_Partial = Role_Data + 2

    acceptBasicSet = ",.:;\"'?!"
    consumeSpaceSet = ",.:;?!" # characters that usually don't follow whitespace


    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.tokenizer      = None
        self.selector       = None
        self.sorter         = None
        self.filter         = None
        self.langModel      = None
        self.contextLength  = 3
        self._initPopup()
               
        self.cursorPositionChanged.connect(self._cursorPositionChangedHandler)
        self.textChanged.connect(self._textChangedHandler)
        self.cursorMoveReason = self.UserReason
        self.lastSpaceReason = self.UserReason
        
    def _initPopup(self):
        self.popup = ListView(self)
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
        for suggestion, probability, partial in self._currentSuggestions():
            item = QtGui.QListWidgetItem()
            item.setData(self.Role_Data, suggestion)
            item.setData(self.Role_Partial, partial)
            item.setData(QtCore.Qt.DisplayRole, "{}\t{:.2f}".format(suggestion + (":" if partial else ""), probability))
            self.popup.addItem(item)


    def _cursorPositionChangedHandler(self):
        if self.cursorMoveReason == self.UserReason:
            self.setPopupState(self.Popup_Hidden)
        self.cursorMoveReason = self.UserReason

    def _textChangedHandler(self):
        if self.langModel:
            # provide only text before cursor (without the last token)
            tc = self.textCursor()
            tc.movePosition(QtGui.QTextCursor.WordLeft, QtGui.QTextCursor.MoveAnchor, 1)
            tc.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.KeepAnchor)
            self.langModel.updateUserInput(tc.selectedText())


    def _popupItemClickedHandler(self, item):
        self._acceptSuggestion(None)
        
    def _currentSuggestions(self):
        context = [""]*(self.contextLength - len(self._context())) + [token[1] for token in self._context()]
        prefix = self._prefix()
        rawSuggestions = self.sorter.getSortedSuggestions(context, self.selector.getSuggestions(context, prefix))
        suggestions = [(suggestion, probability, False) for suggestion, probability in rawSuggestions]
        if self.filter != None:
            return self.filter.filter(suggestions, prefix)
        else:
            return suggestions    
    
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
                self._handleKeyPress(event)
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
                self._handleKeyPress(event)
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
                self._handleKeyPress(event)
                handled = True
                if len(self._currentSuggestions()) > 0:
                    self._refreshPopup()
                else:
                    self.setPopupState(self.Popup_Hidden)

        if not handled:
            self._handleKeyPress(event)

        print(self._context(), ": ", self._prefix())

    def _handleKeyPress(self, event):
        if event.text() != "" and event.text() in self.consumeSpaceSet:
            self._consumeLastSpace()
        elif event.text() == " ":
            self.lastSpaceReason = self.UserReason
        QtGui.QPlainTextEdit.keyPressEvent(self, event)

    def _isAcceptKey(self, keyEvent):
        return keyEvent.key() in [QtCore.Qt.Key_Tab, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Space] \
            or (keyEvent.text() != "" and keyEvent.text() in self.acceptBasicSet)

    def _isFastAcceptKey(self, keyEvent):
        return keyEvent.key() in [QtCore.Qt.Key_Tab]

    def _acceptSuggestion(self, keyEvent):
        """keyEvent can be none in case of invoking accept by mouse"""
        chosenItem = self.popup.currentItem() if self.popup.currentItem() else self.popup.item(0)
        if not chosenItem:
            return None
        prefix = self._prefix()
        
        if chosenItem.data(self.Role_Partial):
            appendix = ""
        elif keyEvent == None: # mouse
            appendix = " "
            self.lastSpaceReason = self.InnerReason
        elif keyEvent.text() == " ": # spacebar
            appendix = " "
            self.lastSpaceReason = self.UserReason
        elif keyEvent.text() in self.acceptBasicSet:
            if keyEvent.text() in self.consumeSpaceSet:
                self._consumeLastSpace()
            appendix = keyEvent.text() + " "
            self.lastSpaceReason = self.InnerReason
        else:
            appendix = " "
            self.lastSpaceReason = self.InnerReason
        
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, len(prefix))
        tc.insertText(chosenItem.data(self.Role_Data) + appendix)
        self.cursorMoveReason = self.InnerReason
        self.setTextCursor(tc)

    def _consumeLastSpace(self):
        if self.lastSpaceReason != self.InnerReason:
            return
        
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, 1)
        tc.removeSelectedText()
        self.cursorMoveReason = self.InnerReason
        self.setTextCursor(tc)
        print("eating last space")

