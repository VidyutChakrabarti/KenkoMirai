import pandas as pd

def preprocess_data(data):
    df = pd.DataFrame(data)
    df.fillna(0, inplace=True)
    return df

if __name__ == "__main__":
    sample_data = {"col1": [1, None, 3], "col2": [4, 5, None]}
    df = preprocess_data(sample_data)
    print(df)
