import unittest
from weather_reporter import read_data
import pandas as pd

sample_data = 'sample_data/sample.txt'


class TestMain(unittest.TestCase):

    def test_read_data(self):
        df = read_data(sample_data)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)


if __name__ == '__main__':
    unittest.main()
