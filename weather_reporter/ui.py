from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtSvg
from weather_reporter import Layout
import sys


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
            print(self.path)
            self.layout = Layout(self.path)
            self.plot = QtSvg.QSvgWidget()
            self.plot.load(self.layout.plot.read())
            self.plot.setGeometry(50, 50, 759, 668)
            self.setCentralWidget(self.plot)
            # self.plot.show()


            break



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
