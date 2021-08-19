from azureml.core import Run
from azureml.core import Workspace
from azureml.core.model import Model as AMLModel


# defining function which Retrieves and returns the current workspace.
def get_current_workspace() -> Workspace:
    run = Run.get_context(allow_offline=False)
    experiment = run.experiment
    return experiment.workspace


# defining function to fetch the model
def get_model(
    model_name: str,
    model_version: int = None,  # If none, return latest model
    tag_name: str = None,
    tag_value: str = None,
    aml_workspace: Workspace = None
) -> AMLModel:

    if aml_workspace is None:
        print("No workspace defined - using current experiment workspace.")
        aml_workspace = get_current_workspace()

    tags = None
    if tag_name is not None or tag_value is not None:

        # Both a name and value must be specified to use tags.
        if tag_name is None or tag_value is None:
            raise ValueError(
                "model_tag_name and model_tag_value should both be supplied"
                + "or excluded")

        tags = [[tag_name, tag_value]]

    model = None

    # Fetch the model wrt the  model version
    if model_version is not None:
        model = AMLModel(
            aml_workspace,
            name=model_name,
            version=model_version,
            tags=tags)

    else:
        models = AMLModel.list(
            aml_workspace,
            name=model_name,
            tags=tags,
            latest=True)

        if len(models) == 1:
            model = models[0]
        elif len(models) > 1:
            raise Exception("Expected only one model")

    return model
