from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QComboBox, QVBoxLayout, QWidget, QPushButton, \
    QFileDialog, QHBoxLayout, QSlider
from PyQt5 import QtSvg
from PyQt5.QtCore import Qt
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
        self.setWindowTitle('SHEAR Weather Reporter')
        self.activateWindow()
        self.setAcceptDrops(True)
        self.path = None
        self.layout = None
        self.plot = QtSvg.QSvgWidget()
        self.plot.setMinimumWidth(800)
        self.plot.setMinimumHeight(500)
        self.periodSlider = QSlider(orientation=Qt.Horizontal)
        self.startDateSlider = QSlider(orientation=Qt.Horizontal)

        row1 = QHBoxLayout()

        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.save)

        self.mainLayout = QVBoxLayout()

        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)

        self.setCentralWidget(self.mainWidget)

        self.variableDropDown = QComboBox()
        self.resampleDropDown = QComboBox()
        for freq, name in [('1H', 'Hourly'), ('1D', 'Daily'), ('1W', 'Weekly'), ('1M', 'Monthly')]:
            self.resampleDropDown.addItem(name, freq)

        self.resampleDropDown.activated.connect(self.set_frequency)

        row1.addWidget(self.variableDropDown)
        row1.addWidget(self.resampleDropDown)

        row2 = QHBoxLayout()
        row2.addWidget(self.startDateSlider)
        row2.addWidget(self.periodSlider)

        for row in [row1, row2]:
            widget = QWidget()
            widget.setLayout(row)
            self.mainLayout.addWidget(widget)
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

        for var in self.layout.variables:
            self.variableDropDown.addItem(self.layout.get_name(var))

        self.startDateSlider.setMaximum(len(self.layout.df))
        self.periodSlider.setMaximum(len(self.layout.df))
        self.periodSlider.setValue(len(self.layout.df))

        self.show_plot()

    def show_plot(self):
        self.plot.load(self.layout.plot.read())
        self.layout.plot.seek(0)

    def change_variable(self, variable_idx):
        self.layout.set_variable(self.layout.variables[variable_idx])
        self.show_plot()

    def save(self):
        dialog = QFileDialog.getSaveFileName(filter="PDF Files (*.pdf)")
        if dialog[0] != '':
            self.layout.create_pdf(dialog[0])

    def set_frequency(self):
        freq = self.resampleDropDown.itemData(self.resampleDropDown.currentIndex())
        self.layout.set_frequency(freq)
        self.show_plot()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
