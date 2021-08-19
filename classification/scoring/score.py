import joblib
import os
from azureml.core.model import Model


def init():
    global model
    model_path = Model.get_model_path(os.getenv("AZUREML_MODEL_DIR").split('/')[-2])

    model = joblib.load(model_path)


if __name__ == "__main__":
    init()