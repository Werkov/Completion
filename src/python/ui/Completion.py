import common.Tokenize
from PyQt4 import QtCore
from PyQt4 import QtGui
from ui import TokenNormalizer

    
class ListView(QtGui.QListWidget):
    """Display suggestions and don't steal focus from text input area."""
    def keyPressEvent(self, event):
        event.ignore()

    def selectionMove(self, shift):
        if self.count() == 0:
            return
        row = self.currentRow() + shift
        row = (self.count() + row) % self.count()
        self.setCurrentRow(row)
    def pageMove(self, direction):
        if direction < 0:
            newPos = self.moveCursor(self.MovePageUp, QtCore.Qt.NoModifier)
        else:
            newPos = self.moveCursor(self.MovePageDown, QtCore.Qt.NoModifier)
        if newPos.isValid():
            self.setCurrentIndex(newPos)
        

class ContextHandler:
    """
    Keep components with state synchronized with input text.

    Components (listeners) are considered to have a state that can be changed with incoming
    token in only forward direction. Normally, state is changed gradually as the
    text is typed; in the case of cursor moves/correcting text, components are
    reset to the beginning state and "shifted" to current state.

    Listeners must have `shift(token)` and `reset()` methods.
    """
    def __init__(self, tokenizer, sentencer, normalizer=None):
        self.context = []
        self.prefix = ""
        self._tokenizer = tokenizer
        self._sentencer = sentencer
        self._normalizer = TokenNormalizer() if not normalizer else normalizer
        self._listeners = []

    def addListener(self, listener):
        """Register a listener to keep in sync with text."""
        self._listeners.append(listener)

    def update(self, text):
        """Call with the text that should be the new context."""
        self._tokenizer.reset(text, True)
        self._sentencer.reset(self._tokenizer)
        self._normalizer.reset(self._sentencer)

        tokens = list(self._normalizer)
        self.prefix = self._tokenizer.uncompleteToken[0] if self._tokenizer.uncompleteToken else ""

        if len(tokens) < len(self.context) or tokens[:len(self.context)] != self.context:
            print("reseting whole model")
            self._reset()
            self.context = []

        newTokens = tokens[len(self.context):]
        if newTokens and newTokens[-1] == common.Tokenize.TOKEN_END_SENTENCE:
            newTokens.append(common.Tokenize.TOKEN_BEG_SENTENCE)

        for token in newTokens:
            self._shift(token)
        self.context += newTokens

    def _reset(self):
        for listener in self._listeners:
            listener.reset()

    def _shift(self, token):
        for listener in self._listeners:
            listener.shift(token)

    def reset(self):
        self.context = []
        self.prefix = ""

    def shift(self, token):
        self.context.append(token)
        self._shift(token)

class TextEdit(QtGui.QPlainTextEdit):
    """
    UI text component with text completion feature.

        - display text and suggestions (retrived from selector)
        - accept user input
        - handle user events
        - assist writing whitespace

    Suggestions returned by selector are processed by customizable filter chain,
    expected output is a sequence of tuples with following fields:
        0: str      suggestion text,
        1: float    suggestion probability,
        2: bool     partial suggestion (those aren't appended a space).
    """
    Popup_Hidden = 0
    Popup_Visible = 1
    Popup_Focused = 2

    UserReason = 0
    InnerReason = 1

    Role_Data = QtCore.Qt.UserRole
    Role_Probability = Role_Data + 1
    Role_Partial = Role_Data + 2

    acceptBasicSet = ",.:;\"'?!"
    consumeSpaceSet = ",.:;?!)“" # characters that usually don't follow whitespace


    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.contextHandler = None
        self.selector       = None
        self._filters       = []

        self._initPopup()
               
        self.cursorPositionChanged.connect(self._cursorPositionChangedHandler)
        self.cursorMoveReason   = self.UserReason
        self.lastSpaceReason    = self.UserReason
        
    def _initPopup(self):
        self.popup = ListView(self)
        self.popup.setWindowFlags(QtCore.Qt.ToolTip)
        self.popup.itemClicked.connect(self._popupItemClickedHandler)
        self.setPopupState(self.Popup_Hidden)


        
    def setPopupState(self, state, refresh=True):
        self.popupState = state
        if state == self.Popup_Hidden:
            self.popup.setVisible(False)
            self.setFocus()
        elif state == self.Popup_Visible:
            if refresh:
                self._refreshPopup()
            self.popup.setVisible(True)
            self.setFocus()
        elif state == self.Popup_Focused:
            if refresh:
                self._refreshPopup()
                if self.popup.count() > 0:
                    self.popup.item(0).setSelected(True)
            
            self.popup.setVisible(True)
            self.popup.setFocus()            
        else:
            raise ValueError()

    def _refreshPopup(self):
        self._updateContext()
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.MoveAnchor, len(self._prefix()))
        position = QtCore.QPoint(self.cursorRect(tc).right(), self.cursorRect(tc).bottom())
        self.popup.move(self.mapToGlobal(position))

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


    def _popupItemClickedHandler(self, item):
        self._acceptSuggestion(None)
        
    def _currentSuggestions(self):
        self._updateContext()
        print(self.contextHandler.context)
        ll = self.selector.suggestions(self.contextHandler.prefix)

        for filter in self._filters:
            ll = filter(ll)

        return list(ll)

    def _prefix(self):
        self._updateContext()
        return self.contextHandler.prefix
    
    def _updateContext(self):
        cursorPosition = self.textCursor().position()
        textContent = self.toPlainText()[0:cursorPosition]
        self.contextHandler.update(textContent)

    def keyPressEvent(self, event):
        handled = False
        if self.popupState == self.Popup_Hidden:
            # manual invokation
            if event.key() == QtCore.Qt.Key_Space and event.modifiers() & QtCore.Qt.ControlModifier:
                self.setPopupState(self.Popup_Visible)
                handled = True
            elif event.text() != "" and event.text().isprintable():
                self.cursorMoveReason = self.InnerReason
                self._handleKeyPress(event)
                handled = True
                if len(self._currentSuggestions()) > 0:
                    self.setPopupState(self.Popup_Visible)

        elif self.popupState == self.Popup_Visible:
            # manual hiding
            if event.key() == QtCore.Qt.Key_Escape:
                self.setPopupState(self.Popup_Hidden)
                handled = True
            # selection change
            elif event.key() in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown]:
                if event.key() == QtCore.Qt.Key_Up:
                    self.popup.selectionMove(-1)
                elif event.key() == QtCore.Qt.Key_Down:
                    self.popup.selectionMove(1)
                elif event.key() == QtCore.Qt.Key_PageUp:
                    self.popup.pageMove(-1)
                elif event.key() == QtCore.Qt.Key_PageDown:
                    self.popup.pageMove(1)

                self.setPopupState(self.Popup_Focused, False)
                handled = True
            elif self._isFastAcceptKey(event):
                self._acceptSuggestion(event)
                handled = True
                if len(self._currentSuggestions()) > 0:
                    self.setPopupState(self.Popup_Visible)
                else:
                    self.setPopupState(self.Popup_Hidden)
            elif event.text() != "":
                self.cursorMoveReason = self.InnerReason
                self._handleKeyPress(event)
                handled = True
                if len(self._currentSuggestions()) > 0:
                    self._refreshPopup()
                else:
                    self.setPopupState(self.Popup_Hidden)

        elif self.popupState == self.Popup_Focused:
            # manual hiding
            if event.key() == QtCore.Qt.Key_Escape:
                self.setPopupState(self.Popup_Hidden)
                handled = True
            # selection change
            elif event.key() in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown]:
                if event.key() == QtCore.Qt.Key_Up:
                    self.popup.selectionMove(-1)
                elif event.key() == QtCore.Qt.Key_Down:
                    self.popup.selectionMove(1)
                elif event.key() == QtCore.Qt.Key_PageUp:
                    self.popup.pageMove(-1)
                elif event.key() == QtCore.Qt.Key_PageDown:
                    self.popup.pageMove(1)

                self.setPopupState(self.Popup_Focused, False)
                handled = True
            elif self._isAcceptKey(event):
                self._acceptSuggestion(event)
                handled = True
                if len(self._currentSuggestions()) > 0:
                    self.setPopupState(self.Popup_Visible)
                else:
                    self.setPopupState(self.Popup_Hidden)
            elif event.text() != "":
                self.cursorMoveReason = self.InnerReason
                self._handleKeyPress(event)
                handled = True
                if len(self._currentSuggestions()) > 0:
                    self._refreshPopup()
                else:
                    self.setPopupState(self.Popup_Hidden)

        if not handled:
            self._handleKeyPress(event)


    def _handleKeyPress(self, event):
        consumed = False
        if event.text() != "" and event.text() in self.consumeSpaceSet:
            consumed = self._consumeLastSpace()
        else:
            self.lastSpaceReason = self.UserReason
        QtGui.QPlainTextEdit.keyPressEvent(self, event)
        if consumed:
            self._appendSpace()

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
        suggestion = chosenItem.data(self.Role_Data)
        
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

        if suggestion in self.consumeSpaceSet:
            self._consumeLastSpace()

            
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, len(prefix))
        tc.insertText(suggestion + appendix)
        self.cursorMoveReason = self.InnerReason
        self.setTextCursor(tc)

    def _consumeLastSpace(self):
        if self.lastSpaceReason != self.InnerReason:
            return False
        
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, 1)
        tc.removeSelectedText()
        self.cursorMoveReason = self.InnerReason
        self.setTextCursor(tc)
        return True

    def _appendSpace(self):
        self.lastSpaceReason = self.InnerReason

        tc = self.textCursor()
        tc.insertText(" ")
        self.cursorMoveReason = self.InnerReason
        self.setTextCursor(tc)

    def addFilter(self, filter):
        """
        Append filter to suggestions filter chain.
        
        Filter must be a callable that accepts the sequence of suggestions and
        returns the modified sequence.
        """
        self._filters.append(filter)

