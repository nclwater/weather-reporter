import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph
from svglib.svglib import svg2rlg
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

style = getSampleStyleSheet()


class Layout:
    def __init__(self, path):
        self.path = path
        self.df: pd.DataFrame = None
        self.variables: list = None
        self.start_date: pd.datetime = None
        self.end_date: pd.datetime = None
        self.plot: str = None
        self.variable = None
        self.plot: BytesIO = None
        self.freq = '1H'

        self.read_dataset()
        self.update_plot()

    def update_plot(self):

        self.plot = BytesIO()

        f, ax = plt.subplots(figsize=(9, 6))
        self.df[self.start_date:self.end_date][self.variable].resample(self.freq).sum().plot(ax=ax)
        plt.tight_layout()

        f.savefig(self.plot, format='svg')
        self.plot.seek(0)
        plt.close(f)

    def read_dataset(self):
        self.df = pd.read_csv(self.path, sep='\t', parse_dates=[[0, 1]], header=[0,1])
        self.df = self.df.set_index(self.df.columns[0])
        self.df.index.name = 'date_time'
        self.df.columns = [' '.join([c.strip() for c in col if 'Unnamed' not in c]).lower() for col in self.df.columns]
        self.df.columns = [col.replace(' ', '_').replace('.', '') for col in self.df.columns]
        self.variables = self.df.select_dtypes(include=['int', 'float']).columns
        self.variable = self.variables[0]
        self.start_date = self.df.index[0]
        self.end_date = self.df.index[-1]

    def create_pdf(self, path):

        doc = SimpleDocTemplate(path, rightMargin=0, leftMargin=0, topMargin=0, bottomMargin=0,
                                pagesize=landscape(A4))

        doc.build([Paragraph(self.get_name(), style=style['h1']), svg2rlg(self.plot)])

    def set_variable(self, variable):
        assert variable in self.variables, '{} not available'.format(variable)
        self.variable = variable
        self.update_plot()

    def set_frequency(self, freq):
        self.freq = freq
        self.update_plot()

    def get_name(self, variable=None):

        names = {
            'temp_out': 'Temperature',
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
            'arc_int': 'Archive Interval (min)',
        }

        if variable is None:
            return names[self.variable]
        else:
            return names[variable]
