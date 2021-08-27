
import numpy
import joblib
import os
from azureml.core.model import Model
from inference_schema.schema_decorators \
    import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type \
    import NumpyParameterType


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


input_sample = numpy.array([
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]])
output_sample = numpy.array([0])


# Inference_schema generates a schema for your web service
# It then creates an OpenAPI (Swagger) specification for the web service
# at http://<scoring_base_url>/swagger.json
@input_schema('data', NumpyParameterType(input_sample))
@output_schema(NumpyParameterType(output_sample))
def run(data):
    try:
        print(data)
        result = model.predict([[0.636, 0, 0.071, 0, 0.09, 1, 0.29, 0.157, 0.4857, 1, 0, 0]])
        # you can return any datatype as long as it is JSON-serializable
        return {"result": result.tolist()}
    except Exception as e:
        error = str(e)
        return error
