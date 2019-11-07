import unittest
from weather_reporter import read_data, create_pdf, create_plot, create_pdf_with_plot
import pandas as pd
import os

df = read_data(os.path.join(os.path.dirname(__file__), 'sample_data/sample.txt'))


class TestMain(unittest.TestCase):

    def test_read_data(self):
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)

    def test_create_pdf(self):
        df_head = df.head()
        df_head = df_head[df_head.columns[:5]]

        create_pdf('out.pdf',
                   data=df_head.to_html())

    def test_create_pdf_with_plot(self):
        create_plot(df)
        create_pdf_with_plot('plot.pdf')



