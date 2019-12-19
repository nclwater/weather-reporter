import os
import pandas as pd


class Station:
    def __init__(self, path):
        self.location = os.path.splitext(os.path.basename(path))[0]
        self.df = pd.read_csv(path, sep='\t', parse_dates=[[0, 1]], header=[0, 1], na_values='---', dayfirst=True)
        self.df = self.df.set_index(self.df.columns[0])
        self.df.index.name = None
        self.df.index = self.df.index.to_period('1H')
        self.df.columns = [' '.join([c.strip() for c in col if 'Unnamed' not in c]).lower() for col in self.df.columns]
        self.df.columns = [col.replace(' ', '_').replace('.', '') for col in self.df.columns]
        self.record_length = self.df.index[-1] - self.df.index[0]

        self.rain = self.df.rain
        self.temp = self.df.temp_out

    def resample(self, freq):
        self.rain = self.df.rain.resample(freq).sum()
        self.temp = self.df.temp_out.resample(freq).mean()
