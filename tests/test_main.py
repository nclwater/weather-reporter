import unittest
from weather_reporter import read_data, create_pdf
import pandas as pd

sample_data = 'sample_data/sample.txt'
pdf_path = 'out.pdf'


class TestMain(unittest.TestCase):

    def test_read_data(self):
        df = read_data(sample_data)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)

    def test_create_pdf(self):
        df = read_data(sample_data).iloc[:5]
        df = df[df.columns[:5]]

        create_pdf(pdf_path, data=df.to_html())


if __name__ == '__main__':
    unittest.main()
