from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QComboBox, QVBoxLayout, QWidget, QPushButton, \
    QFileDialog
from PyQt5 import QtSvg
from weather_reporter import Layout
import sys
import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f')
args = parser.parse_args()


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.activateWindow()
        self.setAcceptDrops(True)
        self.path = None
        self.layout = None
        self.plot = QtSvg.QSvgWidget()
        self.plot.setMinimumWidth(800)
        self.plot.setMinimumHeight(500)

        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.save)

        self.mainLayout = QVBoxLayout()

        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)

        self.setCentralWidget(self.mainWidget)

        self.variableDropDown = QComboBox()

        self.mainLayout.addWidget(self.variableDropDown)
        self.mainLayout.addWidget(self.plot)
        self.mainLayout.addWidget(self.saveButton)

        self.variableDropDown.activated.connect(self.change_variable)

        if args.f is not None:
            self.path = args.f
            self.add_data()

        self.show()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.path = url.toLocalFile()
            try:
                self.add_data()
            except pd.errors.ParserError:
                msg = QMessageBox()
                msg.setText('Could not load from {}'.format(os.path.basename(self.path)))
                msg.exec_()
                return
            break

    def add_data(self):
        self.layout = Layout(self.path)
        self.update_plot()

        for var in self.layout.variables:
            self.variableDropDown.addItem(var)

    def update_plot(self):
        self.layout.save_plot()
        self.plot.load(self.layout.plot.read())
        self.layout.plot.seek(0)

    def change_variable(self, variable_idx):
        self.layout.variable = self.layout.variables[variable_idx]
        self.update_plot()

    def save(self):
        dialog = QFileDialog.getSaveFileName(filter="PDF Files (*.pdf)")
        if dialog[0] != '':
            self.layout.create_pdf(dialog[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
