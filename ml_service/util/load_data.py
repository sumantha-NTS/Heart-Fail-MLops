import pandas as pd


def upload_from_local(file_name: str = 'heart_fail.csv'):
    df = pd.read_csv('../../classification/data/heart_failure.csv')
    df.to_csv(file_name)
