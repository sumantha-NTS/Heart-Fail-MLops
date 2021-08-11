from azureml.core import Run, Experiment, Workspace, Dataset
from azureml.core.model import Model as AMLModel
import argparse, json, os


def main():
    run = Run.get_context()
    exp = run.experiment
    parser = argparse.ArgumentParser("register")

    parser.add_argument("--run_id",type=str,help="Training run ID")

    parser.add_argument("--model_name",type=str,help="Name of the Model",default="diabetes_model.pkl")

    parser.add_argument("--step_input",type=str,help=("input from previous steps"))

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
    model_file = os.path.join(model_path,model_name)
    



if __name__ == '__main__':
    main()