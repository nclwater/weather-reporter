from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QComboBox, QVBoxLayout, QWidget, QPushButton, \
    QFileDialog, QHBoxLayout
from PyQt5 import QtSvg
from PyQt5.QtCore import Qt
import sys
import pandas as pd
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph
from svglib.svglib import svg2rlg
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

style = getSampleStyleSheet()

parser = argparse.ArgumentParser()
parser.add_argument('-f')
args = parser.parse_args()


min_length = 5



names = {
            'temp_out': 'Temperature (C)',
            'hi_temp': 'Maximum Temperature (C)',
            'low_temp': 'Minimum Temperature (C)',
            'out_hum': 'Humidity (%)',
            'dew_pt': 'Dew Point Temperature (C)',
            'wind_speed': 'Wind Speed (km/h)',
            'wind_dir': 'Wind Direction',
            'wind_run': 'Wind Run (km)',
            'hi_speed': 'Maximum Wind Speed (km/h)',
            'hi_dir': 'Direction of Maximum Wind Speed',
            'wind_chill': 'Wind Chill Factor (C)',
            'heat_index': 'Heat Index (C)',
            'thw_index': 'Feels Like Temperature (C)',
            'bar': 'Pressure (millibar)',
            'rain': 'Rainfall (mm)',
            'rain_rate': 'Rainfall Rate (mm/h)',
            'heat_d-d': 'Heating Degree Day (C)',
            'cool_d-d': 'Cooling Degree Day (C)',
            'in_temp': 'Indoor Temperature (C)',
            'in_hum': 'Indoor Humidity (%)',
            'in_dew': 'Indoor Dewpoint Temperature (C)',
            'in_heat': 'Indoor Heat Index (C)',
            'in_emc': 'Equilibrium Moisture Content ',
            'in_air_density': 'Indoor Air Density',
            'wind_samp': 'Number of Wind Measurements',
            'wind_tx': 'RF Channel for wind data',
            'iss_recept': '% - RF reception',
            'arc_int': 'Archive Interval (min)'
}



class App(QMainWindow):

    def __init__(self):
        super().__init__()

        self.df: pd.DataFrame = None
        self.variables: list = None
        self.start_date: pd.datetime = None
        self.end_date: pd.datetime = None
        self.variable = None
        self.svg: BytesIO = None
        self.freq = '1H'
        self.original_df = None
        
        self.setWindowTitle('SHEAR Weather Reporter')
        self.activateWindow()
        self.setAcceptDrops(True)
        self.path = None
        self.plotWidget = QtSvg.QSvgWidget()
        self.plotWidget.setMinimumWidth(800)
        self.plotWidget.setMinimumHeight(500)

        row1 = QHBoxLayout()

        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.save)

        self.mainLayout = QVBoxLayout()

        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)

        self.setCentralWidget(self.mainWidget)

        self.variableDropDown = QComboBox()
        self.resampleDropDown = QComboBox()
        self.dateDropDown = QComboBox()
        self.durationDropDown = QComboBox()
        self.durationDropDown.activated.connect(self.set_duration)

        self.resampleDropDown.activated.connect(self.set_frequency)

        row1.addWidget(self.variableDropDown)
        row1.addWidget(self.resampleDropDown)
        row1.addWidget(self.dateDropDown)
        row1.addWidget(self.durationDropDown)

        row2 = QHBoxLayout()

        for row in [row1, row2]:
            widget = QWidget()
            widget.setLayout(row)
            self.mainLayout.addWidget(widget)
        self.mainLayout.addWidget(self.plotWidget)
        self.mainLayout.addWidget(self.saveButton)

        self.variableDropDown.activated.connect(self.change_variable)

        if args.f is not None:
            self.path = args.f
            self.add_data()

        self.show()
        
    def update_plot(self):

        self.svg = BytesIO()

        f, ax = plt.subplots(figsize=(9, 6))
        self.df.loc[self.start_date:self.end_date, self.variable].plot(ax=ax)
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

        doc.build([Paragraph(self.get_name(), style=title_style), svg2rlg(self.svg)])



    def get_name(self, variable=None):

        if variable is None:
            return names[self.variable]
        else:
            return names[variable]

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
        self.df.columns = [' '.join([c.strip() for c in col if 'Unnamed' not in c]).lower() for col in self.df.columns]
        self.df.columns = [col.replace(' ', '_').replace('.', '') for col in self.df.columns]
        self.variables = self.df.select_dtypes(include=['int', 'float']).columns
        self.variable = self.variables[0]
        self.start_date = self.df.index[0]
        self.end_date = self.df.index[-1]
        self.original_df = self.df.copy()

        for var in self.variables:
            self.variableDropDown.addItem(self.get_name(var))

        duration = self.df.index[-1] - self.df.index[0]

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

        self.set_frequency()

        self.update_plot()


    def set_start_date(self, i):
        d = len(self.df[self.start_date:self.end_date])
        self.start_date = self.df.index[i]

        if i + d < len(self.df):
            self.end_date = self.df.index[i + d]
        else:
            self.end_date = self.df.index[-1]

        self.update_plot()

    def set_duration(self):
        duration = self.durationDropDown.currentData()
        periods = getattr(self.df.index.to_series().dt, duration)
        dates = periods[periods.diff() != 0]
        self.dateDropDown.clear()
        for date in dates.index:
            self.dateDropDown.addItem(('{:%d/%m/%Y}' if duration != 'month' else '{:%m/%Y}').format(date), date)



    def change_variable(self, variable_idx):

        variable = self.variables[variable_idx]

        assert variable in self.variables, '{} not available'.format(variable)
        self.variable = variable
        self.update_plot()

    def save(self):
        dialog = QFileDialog.getSaveFileName(filter="PDF Files (*.pdf)")
        if dialog[0] != '':
            self.create_pdf(dialog[0])

    def set_frequency(self):

        freq = self.resampleDropDown.itemData(self.resampleDropDown.currentIndex())

        self.freq = freq
        self.df = self.original_df.resample(freq).sum()

        self.update_plot()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
