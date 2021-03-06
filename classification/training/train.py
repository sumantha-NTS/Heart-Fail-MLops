# importing necessary libraries
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# scaling function
def scaling_func(df):
    x = df.drop('DEATH_EVENT', axis=1)
    scalar = MinMaxScaler()
    data = pd.DataFrame(scalar.fit_transform(x), columns=x.columns)
    data['y'] = df['DEATH_EVENT']
    return data


def split_data(df):
    x_train, x_test, y_train, y_test = train_test_split(
        df.drop('y', axis=1), df.y, test_size=0.2, random_state=2)

    data = {
        'train': {'x': x_train, 'y': y_train},
        'test': {'x': x_test, 'y': y_test}}
    return data


def train_model(df, args):
    model = RandomForestClassifier(**args)
    model.fit(df['train']['x'], df['train']['y'])
    return model


def get_metrics(model, df):
    pred = model.predict(df['test']['x'])
    acc = accuracy_score(df['test']['y'], pred)
    metrics = {'accuracy': acc}
    return metrics


def main():
    print('Running train.py file')

    # Load the dataset
    df = pd.read_csv('../data/heart_failure.csv')

    # Scale the input data
    scaled_data = scaling_func(df)
    print(scaled_data.iloc[0])

    # splitting the data
    data = split_data(scaled_data)

    # training parameters
    rf_args = {'n_estimators': 500}

    # train the model
    model = train_model(data, rf_args)

    # getting the metrics of the model
    metrics = get_metrics(model, data)
    print(metrics)

    # testing the results
    test_data = np.array(
        [0.636, 0, 0.071, 0, 0.09, 1, 0.29, 0.157, 0.4857, 1, 0, 0])
    print(model.predict([test_data]))


if __name__ == '__main__':
    main()
