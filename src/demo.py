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

        tm = SimpleTriggerModel()
        #klm = KenLMModel("../sample-data/povidky.arpa")
        slm = SimpleLangModel(open("../sample-data/povidky.txt")) # only for dictionary
        #selector = SuggestionSelector(dict=tm.dictionary)
        #sorter = SuggestionSorter(tm)

        #selector = SuggestionSelector(dict=klm.dictionary)
        #selector = SuggestionSelector(bigramDict=slm.search)
        #selector = SuggestionSelector(dict=slm.search)
        #sorter = SuggestionSorter(klm)

        self.txtMain = CompletionTextEdit(self)
        #self.txtMain.setCompleter(DictionaryCompleter(sorter=sorter, selector=selector))
        self.txtMain.setTokenizer(TextInputTokenizer())
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
