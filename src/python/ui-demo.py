#!/usr/bin/python3

from PyQt4 import QtGui
import argparse
import sys


import common.configuration
import ui.Completion



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

        config = common.configuration.current

        self.txtMain                = ui.Completion.TextEdit(self)
        self.txtMain.selector       = config.selector
        self.txtMain.contextHandler = config.contextHandler
        if config.predictNext:
            self.txtMain.predictNext(config.primaryChain, config.secondaryChain, config.merger, config.commonChain)
        else:
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
    # initialize own parser
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="text file to edit", type=argparse.FileType('r'), nargs='?')

    # append subparsers for configuration parameters
    subparsers = parser.add_subparsers(title='Configurations', metavar="CONFIGURATION")
    common.configuration.fillSubparsers(subparsers)

    # create configuration
    args = parser.parse_args()
    common.configuration.createFromArgs(args)

    # start GUI
    app = QtGui.QApplication(sys.argv)
    _ = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
