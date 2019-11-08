import pandas as pd
import matplotlib.pyplot as plt
import os
from jinja2 import Template
from xhtml2pdf import pisa

image_dir = os.path.join(os.path.dirname(__file__), '.images')
if not os.path.exists(image_dir):
    os.mkdir(image_dir)


class Layout:
    def __init__(self, path):
        self.path = path
        self.df: pd.DataFrame = None
        self.numeric_variables: list = None
        self.start_date: pd.datetime = None
        self.end_date: pd.datetime = None
        self.plots: list = None

        self.read_dataset()
        self.plot_variables()

    def plot_variables(self):
        self.plots = []
        for variable in self.numeric_variables:
            f, ax = plt.subplots(figsize=(8, 3), dpi=300)
            self.df[self.start_date:self.end_date][variable].plot(ax=ax, title=variable)
            plt.tight_layout()
            path = os.path.join(image_dir, '{}.png'.format(variable))
            f.savefig(path)
            self.plots.append(path)

    def read_dataset(self):
        self.df = pd.read_csv(self.path, sep='\t', parse_dates=[[0, 1]], header=[0,1])
        self.df = self.df.set_index(self.df.columns[0])
        self.df.index.name = 'date_time'
        self.df.columns = [' '.join([c.strip() for c in col if 'Unnamed' not in c]).lower() for col in self.df.columns]
        self.df.columns = [col.replace(' ', '_').replace('.', '') for col in self.df.columns]
        self.numeric_variables = self.df.select_dtypes(include=['int', 'float']).columns
        self.start_date = self.df.index[0]
        self.end_date = self.df.index[-1]

    def create_pdf(self, path):
        with open(os.path.join(os.path.dirname(__file__), 'template.html')) as f:
            html = Template(f.read())

        css = open(os.path.join(os.path.dirname(__file__), 'style.css')).read()

        html = html.render(plot=self.plots,
                           css=css)

        with open(path, "wb") as f:
            pisa_status = pisa.CreatePDF(html, dest=f)

        return pisa_status.err


selected = [
    'temp_out',
    'hi_temp',
    'low_temp',
    'out_hum',
    'dew_pt',
    'wind_speed',
    'wind_dir',
    'wind_run',
    'hi_speed',
    'hi_dir',
    'wind_chill',
    'heat_index',
    'thw_index',
    'bar',
    'rain',
    'rain_rate',
    'heat_d-d',
    'cool_d-dt'
]
