import unittest
from weather_reporter import Layout


path = 'sample_data/sample.txt'


class TestLayout(unittest.TestCase):

    def test_plot_all_variables(self):
        layout = Layout(path)
        layout.create_pdf('all_plots.pdf')



