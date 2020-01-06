import sys
import argparse
from PyQt5.QtWidgets import QApplication
from weather_reporter.app import App


parser = argparse.ArgumentParser()
parser.add_argument('-f', action='append')
args = parser.parse_args()

app = QApplication(sys.argv)
ex = App(args.f)
ex.show()
sys.exit(app.exec_())
