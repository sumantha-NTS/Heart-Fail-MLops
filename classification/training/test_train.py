import numpy as np
from train import train_model


def test_train_model():
    X_train = np.array([1, 2, 3, 4, 5, 6]).reshape(-1, 1)
    y_train = np.array([10, 9, 8, 8, 6, 5])
    data = {"train": {"x": X_train, "y": y_train}}

    model = train_model(data, {"n_estimators": 100})

    preds = model.predict([[1], [2]])
    np.testing.assert_almost_equal(preds, [10, 9])
