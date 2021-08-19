from azureml.core import Run, Dataset
from azureml.core.model import Model as AMLModel
import argparse
import json
import os
import joblib
import sys
import traceback

# defining function to register model in AML
def register_aml_model(model_path, model_name, model_tags, exp, run_id, dataset_id, build_id: str = 'none', build_uri=None):
    try:
        tagsValue = {'area': 'classification', 'run_id': run_id, 'experiment_name': exp.name}
        tagsValue.update(model_tags)

        if build_id != 'none':
            model_already_registered(model_name, exp, run_id)

            tagsValue['BuildId'] = build_id
            if build_uri is not None:
                tagsValue['BuildUri'] = build_uri

        model = AMLModel.register(
            workspace=exp.workspace,
            model_name=model_name,
            model_path=model_path,
            tags=model_tags,
            datasets=[('training data', Dataset.get_by_id(exp.workspace, dataset_id))])

        os.chdir("..")
        print(
            "Model registered: {} \nModel Description: {} "
            "\nModel Version: {}".format(
                model.name, model.description, model.version))

    except Exception:
        traceback.print_exc(limit=None, file=None, chain=True)
        print("Model registration failed")
        raise


# defining function if the model is already registered
def model_already_registered(model_name, exp, run_id):
    model_list = AMLModel.list(exp.workspace, name=model_name, run_id=run_id)
    if len(model_list) >= 1:
        e = ("Model name:", model_name, "in workspace",
             exp.workspace, "with run_id ", run_id, "is already registered.")
        print(e)
        raise Exception(e)
    else:
        print("Model is not registered for this run.")


def main():
    run = Run.get_context()
    exp = run.experiment
    parser = argparse.ArgumentParser("register")

    parser.add_argument("--run_id", type=str, help="Training run ID")

    parser.add_argument("--model_name", type=str, help="Name of the Model", default="diabetes_model.pkl")

    parser.add_argument("--step_input", type=str, help=("input from previous steps"))

    args = parser.parse_args()

    run_id = args.run_id
    model_name = args.model_name
    model_path = args.step_input

    print('Getting the registration parameters')

    # load the parameters from parameters.json
    with open('../parameters.json') as f:
        pars = json.load(f)
    try:
        register_args = pars['registration']
    except KeyError:
        print("Could not load registration values from file")
        register_args = {"tags": []}

    # tag the model with appropriate tags and values
    model_tags = {}
    for tag in register_args['tags']:
        try:
            mtag = run.parent.get_metrics()[tag]
            model_tags[tag] = mtag

        except KeyError:
            print(f"Could not find {tag} metric on parent run")

    # load the model
    print("Loading model from " + model_path)
    model_file = os.path.join(model_path, model_name)
    model = joblib.load(model_file)
    parent_tags = run.parent.get_tags()

    # extracting the build id from run
    build_id = parent_tags["BuildId"]

    # extracting the build uri from run
    build_uri = parent_tags["BuildUri"]

    # register the model
    if model is not None:
        dataset_id = parent_tags["dataset_id"]
        register_aml_model(model_file, model_name, model_tags, exp, run_id, dataset_id, build_id, build_uri)

    else:
        print('Model not found. Skipping the model registration')
        sys.exit(0)


if __name__ == '__main__':
    main()