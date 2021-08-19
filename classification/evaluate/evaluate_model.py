from azureml.core import Run
import argparse
import traceback
from util.model_helper import get_model

run = Run.get_context()

exp = run.experiment
ws = run.experiment.workspace
run_id = 'amlcompute'

parser = argparse.ArgumentParser("evaluate")

parser.add_argument(
    "--run_id",
    type=str,
    help="Training run ID"
)

parser.add_argument(
    "--model_name",
    type=str,
    help="Name of the Model",
    default="diabetes_model.pkl"
)

parser.add_argument(
    "--allow_run_cancel",
    type=str,
    help="Set this to false to avoid evaluation step from cancelling",
    default="true"
)

args = parser.parse_args()

run_id = args.run_id
model_name = args.model_name
allow_run_cancel = args.allow_run_cancel

metric_eval = 'accuracy'

try:
    first_registration = False
    tag_name = 'experiment_name'
    model = get_model(
        model_name=model_name,
        tag_name=tag_name,
        tag_value=exp.name,
        aml_workspace=ws)

    if model is not None:
        if metric_eval in model.tags:
            production_model_acc = float(model.tags[metric_eval])

        new_model_acc = float(run.parent.get_metrics().get(metric_eval))

        if (production_model_acc is None or new_model_acc is None):
            print('Unable to find', metric_eval, 'metrics')
            if((allow_run_cancel).lower() == 'true'):
                run.parent.cancel()

        else:
            print(
                'Current Production model acc:{}, '
                'New trained model acc:{}'.format(
                    production_model_acc, new_model_acc))

    else:
        print('This is the first model, it should be registered')

except Exception:
    traceback.print_exc(limit=None, file=None, chain=True)
    print('Something went wrong trying to evaluate.')
    raise
