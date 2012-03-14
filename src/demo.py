import sys

from PyQt4 import QtCore
from PyQt4 import QtGui
from ui import *
from origin import *

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

        klm = KenLMModel("../sample-data/povidky.arpa")
        #slm = SimpleLangModel(open("../sample-data/povidky.arpa"))
        #klm = KenLMModel("../large-data/big.arpa")

        selector = SuggestionSelector(dict=klm.dictionary)
        #selector = T9SuggestionSelector(dict=klm.dictionary)
        #selector = SuggestionSelector(bigramDict=slm.search)
        #selector = SuggestionSelector(dict=slm.search)
        sorter = SuggestionSorter(klm)

        self.txtMain = CompletionTextEdit(self)

        self.txtMain.selector = selector
        self.txtMain.sorter = sorter
        self.txtMain.contextLength = 2
        self.txtMain.tokenizer = StringTokenizer()
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.txtMain)


    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    app = QtGui.QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
