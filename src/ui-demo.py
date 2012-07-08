#!/usr/bin/python3
from common.Configuration import DebugConfiguration
import sys

from PyQt4 import QtGui
from common.Configuration import ConfigurationBuilder, DebugConfiguration
from common.Tokenize import StringTokenizer, SentenceTokenizer
import ui.Completion
import ui.Filter

configBuilder = ConfigurationBuilder()

class Window(QtGui.QWidget):
    def __init__(self, configName):
        super(Window, self).__init__()
        self.initUI(configName)
        self.show()
    def initUI(self, configName):
        # window itself
        self.resize(640, 480)
        self.center()
        self.setWindowTitle('Completion test')

        #config = configBuilder[configName]
        config = DebugConfiguration() # TODO retrieve configuration intelligently

        self.txtMain                = ui.Completion.TextEdit(self)
        self.txtMain.selector       = config.selector
        self.txtMain.contextHandler = config.contextHandler

        for filter in config.filterChain:
            self.txtMain.addFilter(filter)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.txtMain)


    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    if len(sys.argv) < 2:
        print("Usage: {} config-name".format(sys.argv[0]))
        sys.exit(1)
    app = QtGui.QApplication(sys.argv)
    _ = Window(sys.argv[1])
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
