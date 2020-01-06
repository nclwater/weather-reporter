import unittest
from weather_reporter.app import App
import os
from PyQt5.QtWidgets import QApplication
import sys

tests = os.path.dirname(__file__)
sample_data_folder = os.path.join(tests, 'sample_data')
sample_data = os.path.join(sample_data_folder, 'sample.txt')
outputs = os.path.join(tests, 'outputs')
if not os.path.exists(outputs):
    os.mkdir(outputs)

app = QApplication(sys.argv)


class TestLayout(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.app.paths = [sample_data, sample_data]
        self.app.add_data()

    def test_set_duration(self):
        self.app.durationDropDown.setCurrentIndex(1)
        self.app.set_duration()

    def test_set_date(self):
        self.app.dateDropDown.setCurrentIndex(1)
        self.app.update_plot()

    def test_set_frequency(self):
        self.app.resampleDropDown.setCurrentIndex(1)
        self.app.set_frequency()

    def test_end_date_too_late(self):
        self.app.dateDropDown.setCurrentIndex(self.app.dateDropDown.count()-1)
        self.app.update_plot()

    def test_save_pdf(self):
        self.app.create_pdf(os.path.join(outputs, 'output.pdf'))




