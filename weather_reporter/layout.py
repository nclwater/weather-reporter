import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate
from svglib.svglib import svg2rlg
from reportlab.lib.pagesizes import A4, landscape
from io import BytesIO


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

        self.read_dataset()
        self.save_plot()

    def save_plot(self):

        self.plot = BytesIO()

        f, ax = plt.subplots(figsize=(9, 6))
        self.df[self.start_date:self.end_date][self.variable].plot(ax=ax, title=self.variable)
        plt.tight_layout()

        f.savefig(self.plot, format='svg')
        self.plot.seek(0)

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

        doc.build([svg2rlg(self.plot)])

    def set_variable(self, variable):
        assert variable in self.variables, '{} not available'.format(variable)
        self.variable = variable
