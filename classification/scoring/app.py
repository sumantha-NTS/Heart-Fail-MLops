from flask import Flask
import joblib
from azureml.core.model import Model
import os

app = Flask(__name__)


def init():
    # load the model from file into a global object
    global model

    # we assume that we have just one model
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder
    # (./azureml-models/$MODEL_NAME/$VERSION)
    model_path = Model.get_model_path(
        os.getenv("AZUREML_MODEL_DIR").split('/')[-2])

    model = joblib.load(model_path)


@app.route('/')
def index():
    return 'Welcome'


if __name__ == "__main__":
    init()
