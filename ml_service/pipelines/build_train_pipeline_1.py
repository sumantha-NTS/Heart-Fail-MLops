from azureml.core import Workspace, Datastore, Dataset
from azureml.pipeline.core import PipelineData, Pipeline
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
import os
from ml_service.util.env_variables import Env
from ml_service.util.attach_compute import get_compute
from ml_service.util.manage_environment import get_environment


def main():
    # configuring the runs for experiment
    run_config = RunConfiguration()

    # getting environment parameters
    e = Env()

    # Get Azure machine learning workspace
    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )
    print("get_workspace:", aml_workspace)

    # Get Azure machine learning cluster
    aml_compute = get_compute(aml_workspace, e.compute_name, e.vm_size)
    if aml_compute is not None:
        print("aml_compute:", aml_compute)

    # Create a reusable Azure ML environment
    environment = get_environment(
        aml_workspace,
        e.aml_env_name,
        conda_dependencies_file=e.aml_env_train_conda_dep_file,
        create_new=e.rebuild_env,
    )

    # updating the environment to run configaration
    run_config.environment = environment

    # fetching the datastore so as to upload the dataset in the next step
    if e.datastore_name:
        datastore_name = e.datastore_name
    else:
        datastore_name = aml_workspace.get_default_datastore().name
    print('Datastore_Name: ', datastore_name)

    # Get dataset name
    dataset_name = e.dataset_name

    # check upload flag
    if e.upload_flag == 'true':
        # finding the dataset in the datastore
        datatstore = Datastore.get(aml_workspace, datastore_name)
        file_name = e.csv_file_name
        target_path = "training_data/"
        path_on_datastore = os.path.join(target_path, file_name)
        print('Datastore: ', datatstore)
        dataset = Dataset.Tabular.from_delimited_files(
                path=(datatstore, path_on_datastore))
        # if (dataset.name):
        #     print(f'{dataset.name} dataset found')
        # else:
        #     raise Exception(
        #             'Could not find CSV dataset at "%s". If you have bootstrapped your project, you will need to provide a CSV.'  # NOQA: E501
        #             % file_name
        #         )

        # register in ML workspace
        dataset = dataset.register(
            workspace=aml_workspace,
            name=dataset_name,
            description="Heart Fail Prediction training data",
            tags={"format": "CSV"},
            create_new_version=True,
        )
    else:
        try:
            Dataset.get_by_name(
                workspace=aml_workspace,
                name=dataset_name,
                version=e.dataset_version)
            print('Dataset exists')
        except Exception as a:
            a = 'Dataset not found'
            print(a)
            raise

    # updating the datastore to run config
    run_config.environment.environment_variables[
        "DATASTORE_NAME"
        ] = datastore_name

    # creating pipeline parameters
    model_name_param = PipelineParameter(
        name="model_name",
        default_value=e.model_name)

    dataset_version_param = PipelineParameter(
        name="dataset_version",
        default_value=e.dataset_version)

    data_file_path_param = PipelineParameter(
        name="data_file_path",
        default_value="none")

    caller_run_id_param = PipelineParameter(
        name="caller_run_id",
        default_value="none")

    # Create a PipelineData to pass data between steps
    pipeline_data = PipelineData(
        "pipeline_data", datastore=aml_workspace.get_default_datastore()
    )

    train_step = PythonScriptStep(
        name="Train Model",
        script_name=e.train_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        outputs=[pipeline_data],
        arguments=[
            "--model_name",
            model_name_param,
            "--step_output",
            pipeline_data,
            "--dataset_version",
            dataset_version_param,
            "--data_file_path",
            data_file_path_param,
            "--caller_run_id",
            caller_run_id_param,
            "--dataset_name",
            dataset_name,
        ],
        runconfig=run_config,
        allow_reuse=True,
    )
    print("Step Train created")

    evaluate_step = PythonScriptStep(
        name="Evaluate Model ",
        script_name=e.evaluate_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        arguments=[
            "--model_name",
            model_name_param,
            "--allow_run_cancel",
            e.allow_run_cancel,
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step Evaluate created")

    register_step = PythonScriptStep(
        name="Register Model ",
        script_name=e.register_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        inputs=[pipeline_data],
        arguments=["--model_name", model_name_param, "--step_input", pipeline_data, ],  # NOQA: E501
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step Register created")

    # Check run_evaluation flag to include or exclude evaluation step.
    if (e.run_evaluation).lower() == "true":
        print("Include evaluation step before register step.")
        evaluate_step.run_after(train_step)
        register_step.run_after(evaluate_step)
        steps = [train_step, evaluate_step, register_step]
    else:
        print("Exclude evaluation step and directly run register step.")
        register_step.run_after(train_step)
        steps = [train_step, register_step]

    # creating the pipeline
    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    train_pipeline._set_experiment_name
    train_pipeline.validate()
    published_pipeline = train_pipeline.publish(
        name=e.pipeline_name,
        description="Model training/retraining pipeline",
        version=e.build_id,
    )
    print(f"Published pipeline: {published_pipeline.name}")
    print(f"for build {published_pipeline.version}")


if __name__ == '__main__':
    main()
