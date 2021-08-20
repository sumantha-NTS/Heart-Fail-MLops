import joblib
import numpy as np
import os
from azureml.core.model import Model
from inference_schema.schema_decorators \
    import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type \
    import NumpyParameterType

input_sample = np.array([
    [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
    [10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]])
output_sample = np.array([
    5021.509689995557,
    3693.645386402646])


@input_schema('data', NumpyParameterType(input_sample))
@output_schema(NumpyParameterType(output_sample))
def init():
    global model
    model_path = Model.get_model_path(
        os.getenv("AZUREML_MODEL_DIR").split('/')[-2])

    model = joblib.load(model_path)


if __name__ == "__main__":
    init()
