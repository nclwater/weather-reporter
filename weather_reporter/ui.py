from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QComboBox, QVBoxLayout, QWidget, QPushButton, \
    QFileDialog, QHBoxLayout, QLabel, QLineEdit
from pandas.plotting import register_matplotlib_converters
from PyQt5 import QtSvg, QtCore, QtGui
import sys
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Table, TableStyle
from svglib.svglib import svg2rlg
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import matplotlib.dates as mdates
from typing import List

style = getSampleStyleSheet()
register_matplotlib_converters()


min_length = 5


class App(QMainWindow):

    def __init__(self, paths=None):
        super().__init__()

        self.dfs: List[pd.DataFrame] = []
        self.svg: BytesIO = None
        self.freq = '1H'
        self.rain: List[pd.Series] = []
        self.temp: List[pd.Series] = []
        self.dates = None
        self.title = None
        self.location = None
        
        self.setWindowTitle('SHEAR Weather Reporter')
        self.activateWindow()
        self.setAcceptDrops(True)
        self.paths = paths
        plotWidget = QWidget()
        plotWidgetLayout = QHBoxLayout()
        plotWidget.setLayout(plotWidgetLayout)
        self.plotWidget = QtSvg.QSvgWidget()
        self.plotWidget.setFixedWidth(800)
        self.plotWidget.setFixedHeight(500)
        plotWidgetLayout.addWidget(self.plotWidget)

        self.plotTitleWidget = QLabel()
        self.plotTitleWidget.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))

        self.logosWidget = QWidget()
        layout = QHBoxLayout()
        self.logosWidget.setLayout(layout)

        self.logos = [os.path.join(os.path.dirname(__file__), 'img', image) for image in [
            'newcastle_university_logo.png',
            'uganda_red_cross_society_long_small.png',
            'shear_logo.png',
            'actogether_uganda_small.png',
            'makerere_university_logo_long_small.png',
        ]]

        for image in self.logos:

            logo = QLabel()
            logo.setPixmap(QtGui.QPixmap(image))
            layout.addWidget(logo)
            logo.setAlignment(QtCore.Qt.AlignCenter)

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

        self.showWidgets(False)

        self.resampleDropDown.activated.connect(self.set_frequency)

        self.dateDropDown.activated.connect(self.update_plot)


        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        title = QWidget()
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.resampleDropDown)
        title_layout.addWidget(QLabel('Weather Report for the'))
        title_layout.addWidget(self.durationDropDown)
        title_layout.addWidget(QLabel('of'))
        title_layout.addWidget(self.dateDropDown)
        # title_layout.addWidget(self.plotTitleWidget)
        title_layout.setAlignment(QtCore.Qt.AlignCenter)
        title.setLayout(title_layout)
        self.mainLayout.addWidget(title)
        self.mainLayout.addWidget(plotWidget)
        self.mainLayout.addWidget(self.saveButton)
        self.mainLayout.addWidget(self.logosWidget)

        if self.paths is not None:
            self.add_data()

    def update_location(self):
        if self.df is not None:
            self.update_plot()

    def showWidgets(self, show: bool):
        self.dateDropDown.setVisible(show)
        self.durationDropDown.setVisible(show)
        self.resampleDropDown.setVisible(show)
        self.plotWidget.setVisible(show)
        self.saveButton.setVisible(show)
        self.dropWidget.setVisible(not show)
        
    def update_plot(self):

        self.svg = BytesIO()
        f, axes = plt.subplots(len(self.dfs), figsize=(9, 6))
        date = self.dateDropDown.currentData()

        end_index = self.dates.index.get_loc(date)+1

        for ax, temp, rain in zip(axes.flat, self.temp, self.rain):

            if end_index >= len(self.dates):
                end_date = temp.index[-1]
            else:
                end_date = self.dates.index[end_index]

            temp = temp.loc[date:end_date]

            ax.plot(temp.index.start_time, temp.values, color='firebrick')

            ax.set_ylabel('Temperature (C)')

            ymin, ymax = ax.get_ylim()
            ymax = ymax + ymax - ymin
            ax.set_ylim(ymin, ymax)

            twinx = ax.twinx()

            twinx.invert_yaxis()

            rain = rain.loc[date:end_date].iloc[:-1]

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

            self.title = '{} Weather Report for the {} of {}'.format(
                self.resampleDropDown.currentText(),
                self.durationDropDown.currentText(),
                self.dateDropDown.currentText())

            self.plotTitleWidget.setText(self.title)
            ax.set_title("Location: {}".format(self.location.title()))
            ax.patch.set_visible(False)
        f.patch.set_visible(False)

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

        story = [Paragraph(self.title, style=title_style), svg2rlg(self.svg)]

        chart_style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                  ('VALIGN', (0, 0), (-1, -1), 'CENTER')])

        images = []

        for logo in self.logos:
            from reportlab.lib import utils
            from reportlab.lib.units import cm
            height = 0.5 * cm

            img = utils.ImageReader(logo)
            iw, ih = img.getSize()
            aspect = iw / ih
            images.append(Image(logo, width=height*aspect, height=height))

        story.append(Table([images],
                           colWidths=[150 for _ in self.logos],
                           rowHeights=[3], style=chart_style))

        doc.build(story)

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
        for path in self.paths:
            self.location = os.path.splitext(os.path.basename(path))[0]
            df = pd.read_csv(path, sep='\t', parse_dates=[[0, 1]], header=[0, 1], na_values='---', dayfirst=True)
            df = df.set_index(df.columns[0])
            df.index.name = None
            df.index = df.index.to_period('1H')
            df.columns = [' '.join([c.strip() for c in col if 'Unnamed' not in c]).lower() for col in df.columns]
            df.columns = [col.replace(' ', '_').replace('.', '') for col in df.columns]
            self.dfs.append(df)

            duration = df.index[-1].end_time - df.index[0].start_time

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

            self.rain.append(df.rain)
            self.temp.append(df.temp_out)

        self.set_duration()
        self.set_frequency()

        self.update_plot()

        self.showWidgets(True)
        print(len(self.dfs))

    def set_duration(self):
        duration = self.durationDropDown.currentData()
        periods = getattr(self.rain[0].index.to_series().dt, duration)
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
        for i in range(len(self.dfs)):
            self.rain[i] = self.dfs[i].rain.resample(freq).sum()
            self.temp[i] = self.dfs[i].temp_out.resample(freq).mean()

        self.update_plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='append')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    ex = App(args.f)
    ex.show()
    sys.exit(app.exec_())
