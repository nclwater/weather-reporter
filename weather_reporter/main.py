import pandas as pd
from xhtml2pdf import pisa
import re
import os
from jinja2 import Template
import matplotlib.pyplot as plt
import pathlib


image_dir = os.path.join(os.path.dirname(__file__), '.images')


def read_data(path):
    df = pd.read_csv(path, sep='\t', parse_dates=[[0, 1]])
    df.columns = [c.lower() + '_' if 'Unnamed' not in c else '' for c in df.columns]
    df.columns = df.columns + df.iloc[0]
    df.columns = [re.sub('[ .1234]', lambda s: {' ': '_', '.': ''}[s.group(0)]
    if not s.group(0).isdigit() else '', col).lower() for col in df.columns]
    df = df.drop(0).astype({'temp_out': float})
    return df


def create_pdf(path, **kwargs):
    with open(os.path.join(os.path.dirname(__file__), 'template.html')) as f:
        html = Template(f.read())

    html = html.render(**kwargs)

    with open(path, "wb") as f:
        pisa_status = pisa.CreatePDF(html, dest=f,
                                     # default_css=open(os.path.join(os.path.dirname(__file__),
                                     #                                             'typography.css'
                                     #                                             )
                                     #                  ).read()
        )

    return pisa_status.err


def create_plot(df: pd.DataFrame):
    create_image_dir()
    f, ax = plt.subplots()
    s = df['temp_out']
    s.plot(ax=ax)
    f.savefig(os.path.join(image_dir, 'plot.png'))


def create_image_dir():
    if not os.path.exists(image_dir):
        os.mkdir(image_dir)


def create_pdf_with_plot(path):
    uri = pathlib.Path(os.path.join(image_dir, 'plot.png')).as_uri()
    create_pdf(path, data=pd.DataFrame().to_html(), plot=os.path.sep.join(uri.split('/')))


