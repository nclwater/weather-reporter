from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QComboBox, QVBoxLayout, QWidget, QPushButton, \
    QFileDialog, QHBoxLayout, QLabel
from pandas.plotting import register_matplotlib_converters
from PyQt5 import QtSvg, QtCore, QtGui
import sys
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph
from svglib.svglib import svg2rlg
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import matplotlib.dates as mdates

style = getSampleStyleSheet()
register_matplotlib_converters()


min_length = 5


class App(QMainWindow):

    def __init__(self, path=None):
        super().__init__()

        self.df: pd.DataFrame = None
        self.svg: BytesIO = None
        self.freq = '1H'
        self.df = None
        self.rain = None
        self.temp = None
        self.dates = None
        
        self.setWindowTitle('SHEAR Weather Reporter')
        self.activateWindow()
        self.setAcceptDrops(True)
        self.path = path
        self.plotWidget = QtSvg.QSvgWidget()
        self.plotWidget.setMinimumWidth(800)
        self.plotWidget.setMinimumHeight(500)

        self.logosWidget = QWidget()
        layout = QHBoxLayout()
        self.logosWidget.setLayout(layout)

        for image in [
            'newcastle_university_logo.png',
            'uganda_red_cross_society_long_small.png',
            'shear_logo.png',
            'actogether_uganda_small.png',
            'makerere_university_logo_long_small.png',
        ]:

            logo = QLabel()
            logo.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'img', image)))
            layout.addWidget(logo)
            logo.setAlignment(QtCore.Qt.AlignCenter)

        row1 = QHBoxLayout()

        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.save)

        self.mainLayout = QVBoxLayout()

        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)

        self.setCentralWidget(self.mainWidget)

        self.resampleDropDown = QComboBox()
        self.dateDropDown = QComboBox()
        self.durationDropDown = QComboBox()
        self.durationDropDown.activated.connect(self.set_duration)

        self.dropWidget = QLabel('Drop a Davis WeatherLink export file here')
        self.dropWidget.setStyleSheet("margin:5px; border:1px dashed rgb(0, 0, 0); padding:10px")

        self.resampleLabel = QLabel('Resolution:')
        self.dateLabel = QLabel('Date:')
        self.durationLabel = QLabel('Duration:')

        font = QtGui.QFont("Times", 12, QtGui.QFont.Normal)
        for label in [self.resampleLabel, self.dateLabel, self.durationLabel]:
            label.setAlignment(QtCore.Qt.AlignRight)
            label.setFont(font)

        self.showWidgets(False)

        self.resampleDropDown.activated.connect(self.set_frequency)

        self.dateDropDown.activated.connect(self.update_plot)

        row1.addWidget(self.resampleLabel)
        row1.addWidget(self.resampleDropDown)
        row1.addWidget(self.durationLabel)
        row1.addWidget(self.durationDropDown)
        row1.addWidget(self.dateLabel)
        row1.addWidget(self.dateDropDown)
        row1.addWidget(self.dropWidget)

        row2 = QHBoxLayout()

        for row in [row1, row2]:
            widget = QWidget()
            widget.setLayout(row)
            self.mainLayout.addWidget(widget)

        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.mainLayout.addWidget(self.plotWidget)
        self.mainLayout.addWidget(self.saveButton)
        self.mainLayout.addWidget(self.logosWidget)

        if self.path is not None:
            self.add_data()

    def showWidgets(self, show: bool):
        self.dateDropDown.setVisible(show)
        self.durationDropDown.setVisible(show)
        self.resampleDropDown.setVisible(show)
        self.plotWidget.setVisible(show)
        self.saveButton.setVisible(show)
        self.dateLabel.setVisible(show)
        self.durationLabel.setVisible(show)
        self.resampleLabel.setVisible(show)
        self.dropWidget.setVisible(not show)
        
    def update_plot(self):

        self.svg = BytesIO()

        f, ax = plt.subplots(figsize=(9, 6))
        date = self.dateDropDown.currentData()

        end_index = self.dates.index.get_loc(date)+1
        if end_index >= len(self.dates):
            end_date = self.temp.index[-1]
        else:
            end_date = self.dates.index[end_index]

        temp = self.temp.loc[date:end_date]

        ax.plot(temp.index.start_time, temp.values, color='firebrick')

        ax.set_ylabel('Temperature (C)')

        ymin, ymax = ax.get_ylim()
        ymax = ymax + ymax - ymin
        ax.set_ylim(ymin, ymax)

        twinx = ax.twinx()

        twinx.invert_yaxis()

        rain = self.rain.loc[date:end_date].iloc[:-1]

        width = rain.index.end_time - rain.index.start_time

        twinx.bar(rain.index.start_time, rain.values, width=width, align='edge')

        twinx.set_ylabel('Rainfall (mm)')

        ymax, ymin = twinx.get_ylim()
        ymax = ymax + ymax - ymin
        twinx.set_ylim(ymax, ymin)

        locator = mdates.AutoDateLocator()
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

        plt.tight_layout()

        f.savefig(self.svg, format='svg')
        self.svg.seek(0)
        plt.close(f)

        self.plotWidget.load(self.svg.read())
        self.svg.seek(0)

    def create_pdf(self, path):

        title_style = style['h1']
        title_style.alignment = 1

        doc = SimpleDocTemplate(path, rightMargin=0, leftMargin=0, topMargin=0, bottomMargin=0,
                                pagesize=landscape(A4))

        doc.build([Paragraph('SHEAR {} Weather Report for the {} of {}'.format(
            self.resampleDropDown.currentText(),
            self.durationDropDown.currentText(),
            self.dateDropDown.currentText()),
            style=title_style), svg2rlg(self.svg)])

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

        self.df = pd.read_csv(self.path, sep='\t', parse_dates=[[0, 1]], header=[0, 1], na_values='---', dayfirst=True)
        self.df = self.df.set_index(self.df.columns[0])
        self.df.index.name = None
        self.df.index = self.df.index.to_period('1H')
        self.df.columns = [' '.join([c.strip() for c in col if 'Unnamed' not in c]).lower() for col in self.df.columns]
        self.df.columns = [col.replace(' ', '_').replace('.', '') for col in self.df.columns]

        duration = self.df.index[-1].end_time - self.df.index[0].start_time

        if duration > pd.Timedelta(hours=min_length):
            self.resampleDropDown.addItem('Hourly', '1H')
            self.durationDropDown.addItem('Day', 'day')
        if duration > pd.Timedelta(days=min_length):
            self.resampleDropDown.addItem('Daily', '1D')
            self.durationDropDown.addItem('Week', 'week')
            self.durationDropDown.addItem('Month', 'month')
        if duration > pd.Timedelta(weeks=min_length):
            self.resampleDropDown.addItem('Weekly', '1W')
        if duration > pd.Timedelta(days=31 * min_length):
            self.resampleDropDown.addItem('Monthly', '1M')
            self.durationDropDown.addItem('Year', 'year')

        self.rain = self.df.rain
        self.temp = self.df.temp_out

        self.set_duration()
        self.set_frequency()

        self.update_plot()

        self.showWidgets(True)

    def set_duration(self):
        duration = self.durationDropDown.currentData()
        periods = getattr(self.rain.index.to_series().dt, duration)
        self.dates = periods[periods.diff() != 0]
        self.dateDropDown.clear()

        if duration == 'month':
            date_string = '{:%m/%Y}'
        elif duration == 'year':
            date_string = '{:%Y}'
        else:
            date_string = '{:%d/%m/%Y}'

        for date in self.dates.index:
            self.dateDropDown.addItem(date_string.format(date.start_time), date)

        self.update_plot()

    def save(self):
        dialog = QFileDialog.getSaveFileName(filter="PDF Files (*.pdf)")
        if dialog[0] != '':
            self.create_pdf(dialog[0])

    def set_frequency(self):

        freq = self.resampleDropDown.itemData(self.resampleDropDown.currentIndex())

        self.freq = freq
        self.rain = self.df.rain.resample(freq).sum()
        self.temp = self.df.temp_out.resample(freq).mean()

        self.update_plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    ex = App(args.f)
    ex.show()
    sys.exit(app.exec_())
