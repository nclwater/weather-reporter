import pandas as pd


def read_data(path):
    df = pd.read_csv(path, sep='\t', parse_dates=[[0, 1]])
    df.columns = [c + ' ' if 'Unnamed' not in c else '' for c in df.columns]
    df.columns = df.columns + df.iloc[0]
    df = df.drop(0)
    return df
