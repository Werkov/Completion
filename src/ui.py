import sys
from PyQt4 import QtGui, QtCore

from origin import *

# training data
f = open("../sample-data/povidky.txt")
os = SimpleLangModel(f)
f.close()

oa = LaplaceSmoothLM(os, parameter=0.1)

selector = SuggestionSelector(os.search)
sorter = SuggestionSorter(oa)

# ask user and show him suggestions until empty string is given




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

        # text input
        self.txtInput = Autocomplete(self)
        self.txtInput.resize(640, 200) # find different solution
        
        
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class Autocomplete(QtGui.QTextEdit):
    def __init__(self, parent):
        super(Autocomplete, self).__init__(parent)
        self.initUI();

    def keyPressEvent(self, e):
        super(Autocomplete, self).keyPressEvent(e)
        self.lstSuggestions.move(self.cursorRect().left(), self.cursorRect().top() + self.cursorRect().height())
        M = N-1
        buffer = (M) * [""]
        word = self.toPlainText().strip().split(" ")[-1:][0]
        print(word)
        if word != "":
            buffer = buffer[1:M]
            buffer.append(word)
            tips = sorter.getSortedSuggestions(buffer, selector.getSuggestions(buffer))
            self.lstSuggestions.clear()
            for tip in tips[0:20]:
                self.lstSuggestions.addItem("{}\t\t{}".format(*tip))
            self.lstSuggestions.setVisible(True)
        else:
            self.lstSuggestions.setVisible(False)
        

    def initUI(self):
        self.lstSuggestions = QtGui.QListWidget(self)
        self.lstSuggestions.insertItem(0, "ahoj")
        self.lstSuggestions.insertItem(0, "čau")
        self.lstSuggestions.insertItem(0, "čnic")
        self.lstSuggestions.setVisible(False)


def main():
    app = QtGui.QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
