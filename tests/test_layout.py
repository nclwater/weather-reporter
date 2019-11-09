import unittest
from weather_reporter import Layout
import os

path = os.path.join(os.path.dirname(__file__), 'sample_data/sample.txt')


class TestLayout(unittest.TestCase):

    def test_plot_all_variables(self):
        layout = Layout(path)
        layout.create_pdf('all_plots.pdf')



