from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5 import QtSvg
from weather_reporter import Layout
import sys
import pandas as pd
import os


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.show()
        self.activateWindow()
        self.setAcceptDrops(True)
        self.path = None
        self.layout = None
        self.plot = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.path = url.toLocalFile()
            try:
                self.layout = Layout(self.path)
            except pd.errors.ParserError:
                msg = QMessageBox()
                msg.setText('Could not load from {}'.format(os.path.basename(self.path)))
                msg.exec_()
                return
            self.plot = QtSvg.QSvgWidget()
            self.plot.load(self.layout.plot.read())
            self.setCentralWidget(self.plot)

            break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
