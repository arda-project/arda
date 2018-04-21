import pandas as pd
`

def load_data(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.read_excel(path)
