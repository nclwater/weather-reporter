import pandas as pd
from xhtml2pdf import pisa
import os
from jinja2 import Template


def read_data(path):
    df = pd.read_csv(path, sep='\t', parse_dates=[[0, 1]])
    df.columns = [c + ' ' if 'Unnamed' not in c else '' for c in df.columns]
    df.columns = df.columns + df.iloc[0]
    df = df.drop(0)
    return df


def create_pdf(path):
    with open(os.path.join(os.path.dirname(__file__), 'template.html')) as f:
        html = Template(f.read())

    html = html.render(data='Sample Data')

    with open(path, "w+b") as f:
        pisa_status = pisa.CreatePDF(html, dest=f)

    return pisa_status.err


