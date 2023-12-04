import pandas as pd
import numpy as np

df = pd.read_csv('data.csv', delimiter=',', )

df.columns = df.columns.str.lower().str.replace(' ', '_')

def f(x):
    if x == 1.0:
        return x
print(df.head(10))
