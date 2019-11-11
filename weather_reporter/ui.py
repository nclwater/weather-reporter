from PyQt5.QtWidgets import QMainWindow, QApplication
from weather_reporter import Layout
import sys


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.show()
        self.activateWindow()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
