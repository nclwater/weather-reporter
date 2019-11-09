import unittest
from weather_reporter import Layout
import os

tests = os.path.dirname(__file__)
sample_data = os.path.join(tests, 'sample_data/sample.txt')
outputs = os.path.join(tests, 'outputs')
if not os.path.exists(outputs):
    os.mkdir(outputs)


class TestLayout(unittest.TestCase):

    def test_temperature(self):
        layout = Layout(sample_data)
        layout.set_variable('temp_out')
        layout.create_pdf(os.path.join(outputs, 'temp_out.pdf'))



