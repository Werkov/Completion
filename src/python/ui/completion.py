from PyQt4 import QtCore
from PyQt4 import QtGui


    
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
        2: bool     sugestion type (normal, partial, following word).
    """
    Popup_Hidden = 0
    Popup_Visible = 1
    Popup_Focused = 2

    UserReason = 0
    InnerReason = 1

    Role_Data = QtCore.Qt.UserRole
    Role_Probability = Role_Data + 1
    Role_Type = Role_Data + 2

    acceptBasicSet = ",.:;\"'?!"
    consumeSpaceSet = ",.:;?!)“" # characters that usually don't follow whitespace

    #
    # Initialization and settings
    #
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.contextHandler = None
        self.selector       = None
        self._filters       = []
        self._predictNext   = False

        self._initPopup()
               
        self.cursorPositionChanged.connect(self._cursorPositionChangedHandler)
        self.cursorMoveReason   = self.UserReason
        self.lastSpaceReason    = self.UserReason
        
    def _initPopup(self):
        self.popup = ListView(self)
        self.popup.setWindowFlags(QtCore.Qt.ToolTip)
        self.popup.itemClicked.connect(self._popupItemClickedHandler)
        self.setPopupState(self.Popup_Hidden)
    def addFilter(self, filter):
        """
        Append filter to suggestions filter chain.

        Filter must be a callable that accepts the sequence of suggestions and
        returns the modified sequence.
        """
        self._filters.append(filter)

    def predictNext(self, primaryChain, secondaryChain, merger, commonChain):
        """EXPERIMENTAL
        Objects needed for prediction next word in advance.
            - primaryChain      input is list of (string) suggestions,
                                expected output is sorted list of suggestions (tuples)
            - secondaryChain    analogous to primaryChain
            - merger            merges list of suggestion tuples into one list
            - commonChain       final filter chain od merged list of tuples
        """

        self._primaryChain      = primaryChain
        self._secondaryChain    = secondaryChain
        self._merger            = merger
        self._commonChain       = commonChain
        self._predictNext       = True

    #
    # Popup list
    #
        
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
        for suggestion, probability, type in self._currentSuggestions():
            item = QtGui.QListWidgetItem()
            item.setData(self.Role_Data, suggestion)
            item.setData(self.Role_Type, type)
            if type == ui.Suggestion.TYPE_NORMAL:
                display = suggestion
            elif type == ui.Suggestion.TYPE_PARTIAL:
                display = suggestion + ":"
            elif type == ui.Suggestion.TYPE_NEXT:
                display = self.predictor + " " + suggestion
            item.setData(QtCore.Qt.DisplayRole, "{}\t{:.2f}".format(display, probability))
            self.popup.addItem(item)

    #
    # Suggestions and context
    #
    def _currentSuggestions(self):
        self._updateContext()

        if self._predictNext: # EXPERIMENTAL
            first = self.selector.suggestions(self.contextHandler.prefix)
            for filter in self._primaryChain:
                first = filter(first)
            first = list(first)
            if first:
                self.predictor = first[0][0] # use first (best) prediction to predict even next word
                self.contextHandler.shift(self.predictor)
                self.contextHandler.prefix = ""
                second = self.selector.suggestions("")
                for filter in self._secondaryChain:
                    second = filter(second)
            else:
                second = []

            ll = self._merger(first, second)

            for filter in self._commonChain:
                ll = filter(ll)
        else:
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

    _fastAcceptMap = {
        QtCore.Qt.Key_F1: 0,
        QtCore.Qt.Key_F2: 1,
        QtCore.Qt.Key_F3: 2,
        QtCore.Qt.Key_F4: 3,
        QtCore.Qt.Key_F5: 4
    }
    def _acceptSuggestion(self, keyEvent):
        """keyEvent can be none in case of invoking accept by mouse"""
        if keyEvent and keyEvent.key() in self._fastAcceptMap:
            chosenItem = self.popup.item(self._fastAcceptMap[keyEvent.key()])
        else:
            chosenItem = self.popup.currentItem() if self.popup.currentItem() else self.popup.item(0)
            
        if not chosenItem:
            return None
        prefix = self._prefix()
        suggestion = chosenItem.data(self.Role_Data)
        prepend = ""

        if chosenItem.data(self.Role_Type) == ui.Suggestion.TYPE_PARTIAL:
            appendix = ""
        elif chosenItem.data(self.Role_Type) == ui.Suggestion.TYPE_NEXT:
            prepend = self.predictor + " "
            appendix = " "
            self.lastSpaceReason = self.InnerReason
        elif keyEvent == None: # mouse
            appendix = " "
            self.lastSpaceReason = self.InnerReason
        elif keyEvent.text() == " ": # spacebar
            appendix = " "
            self.lastSpaceReason = self.UserReason
        elif keyEvent.text() in self.acceptBasicSet:
            appendix = keyEvent.text() + " "
            self.lastSpaceReason = self.InnerReason
        else:
            appendix = " "
            self.lastSpaceReason = self.InnerReason

        if suggestion in self.consumeSpaceSet:
            self._consumeLastSpace()


        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, len(prefix))
        tc.insertText(prepend + suggestion + appendix)
        self.cursorMoveReason = self.InnerReason
        self.setTextCursor(tc)
        return True
    #
    # Event handling
    #
    def _cursorPositionChangedHandler(self):
        if self.cursorMoveReason == self.UserReason:
            self.setPopupState(self.Popup_Hidden)
        self.cursorMoveReason = self.UserReason

    def _popupItemClickedHandler(self, item):
        self._acceptSuggestion(None)

    def keyPressEvent(self, event):
        handled = False
        if self.popupState == self.Popup_Hidden:
            # manual invokation
            if event.key() == QtCore.Qt.Key_Space and event.modifiers() & QtCore.Qt.ControlModifier:
                self.setPopupState(self.Popup_Visible)
                print(self.contextHandler.context)
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
                handled = self._acceptSuggestion(event)
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

    #
    # Utils
    #
    def _isAcceptKey(self, keyEvent):
        return keyEvent.key() in [QtCore.Qt.Key_Tab, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Space] \
            or (keyEvent.text() != "" and keyEvent.text() in self.acceptBasicSet)

    def _isFastAcceptKey(self, keyEvent):
        return keyEvent.key() in [QtCore.Qt.Key_Tab, QtCore.Qt.Key_F1, QtCore.Qt.Key_F2, QtCore.Qt.Key_F3, QtCore.Qt.Key_F4, QtCore.Qt.Key_F5]


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

