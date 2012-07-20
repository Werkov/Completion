#!/usr/bin/python3

import sys
import os.path

from PyQt4 import QtGui
import argparse
import common.configuration
import ui.Completion



class Window(QtGui.QMainWindow):
    WINDOW_TITLE = 'Completion test'

    def __init__(self):
        super(Window, self).__init__()
        self.filename = None
        self.touched = False
        
        self.initUI()
        self.show()

    def initUI(self):
        # window itself
        self.resize(640, 480)
        self.center()
        self.setWindowTitle()

        self.initMenu()
        self.initComponent()



    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initMenu(self):
        menu = self.menuBar().addMenu('&File')
        action = menu.addAction('&New')
        action.setShortcut(QtGui.QKeySequence.fromString('Ctrl+N'))
        action.triggered.connect(self.handleFileNew)

        action = menu.addAction('&Open')
        action.setShortcut(QtGui.QKeySequence.fromString('Ctrl+O'))
        action.triggered.connect(self.handleFileOpen)

        action = menu.addAction('&Save')
        action.setShortcut(QtGui.QKeySequence.fromString('Ctrl+S'))
        action.triggered.connect(self.handleFileSave)

        action = menu.addAction('Save &as')
        action.triggered.connect(self.handleFileSaveAs)

        menu.addSeparator()
        action = menu.addAction('&Quit')
        action.setShortcut(QtGui.QKeySequence.fromString('Alt+F4'))
        action.triggered.connect(self.handleFileQuit)

    def initComponent(self):
        config = common.configuration.current

        self.txtMain                = ui.Completion.TextEdit(self)
        self.txtMain.selector       = config.selector
        self.txtMain.contextHandler = config.contextHandler
        if config.predictNext:
            self.txtMain.predictNext(config.primaryChain, config.secondaryChain, config.merger, config.commonChain)
        else:
            for filter in config.filterChain:
                self.txtMain.addFilter(filter)

        self.txtMain.textChanged.connect(self.handleTextChanged)
        self.setCentralWidget(self.txtMain)

    #
    # Handlers
    #
    def handleFileNew(self):
        if self.askSave():
            self.txtMain.setPlainText("")
            self.touched = False
            self.filename = None
            self.setWindowTitle()

    def handleFileOpen(self):
        if self.askSave():
            filename = QtGui.QFileDialog.getOpenFileName(self,
                                                         'Open File');
            if filename:
                self.loadFile(filename)


    def handleFileSave(self):
        if not self.filename:
            filename = QtGui.QFileDialog.getSaveFileName(self,
                                                         'Save File');
            if filename:
                self.saveFile(filename)
            else:
                return
        else:
            self.saveFile(self.filename)

    def handleFileSaveAs(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Save File As');
        if filename:
            self.filename = filename
        else:
            return
        self.saveFile(self.filename)

    def handleFileQuit(self):
        self.close()

    def handleTextChanged(self):
        self.touched = True

    #
    # Utils
    #
    def askSave(self):
        """Return boolean whether continue in desired action."""
        if self.touched:
            reply = QtGui.QMessageBox.question(self,
                                               'Save file?',
                                               'Text has been modified.\nDo you wish to save the changes?',
                                               QtGui.QMessageBox.Save | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Save:
                self.saveFile()
            elif reply == QtGui.QMessageBox.No:
                return True
            elif reply == QtGui.QMessageBox.Cancel:
                return False

        return True

    def saveFile(self, filename):
        f = open(filename, 'w')
        f.write(self.txtMain.toPlainText())
        f.close()
        self.touched = False
        self.filename = filename
        self.setWindowTitle(os.path.basename(filename))

    def loadFile(self, filename):
        f = open(filename, 'r')
        self.txtMain.setPlainText(f.read())
        f.close()
        self.touched = False
        self.filename = filename
        self.setWindowTitle(os.path.basename(filename))

    #
    # Overrides
    #
    def closeEvent(self, event):
        if self.askSave():
            event.accept()
        else:
            event.ignore()

    def setWindowTitle(self, title = None):
        if not title:
            super().setWindowTitle(self.WINDOW_TITLE)
        else:
            super().setWindowTitle(title + ' – ' + self.WINDOW_TITLE)



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
    win = Window()
    if args.file:
        args.file.close()
        win.loadFile(args.file.name)
        
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
