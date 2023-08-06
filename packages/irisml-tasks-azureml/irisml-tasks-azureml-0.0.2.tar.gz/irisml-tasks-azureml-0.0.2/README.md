# irisml-tasks-azureml

This package is a part of IrisML pipeline. It provides utility scripts and tasks to work with AzureML.

## Installation
```bash
pip install irisml-tasks-azureml
```

## Available commands
```bash
irisml_run_aml [-h] [--env ENV] [--cache_url CACHE_URL] [--no_cache] [--include_local_tasks [INCLUDE_LOCAL_TASKS]] [--custom_packages CUSTOM_PACKAGES [CUSTOM_PACKAGES ...]]
                      [--extra_index_url EXTRA_INDEX_URL] [--no_wait] [--compute_target COMPUTE_TARGET] [--subscription_id SUBSCRIPTION_ID] [--workspace WORKSPACE] [--experiment EXPERIMENT]
                      [--base_docker_image BASE_DOCKER_IMAGE] [--base_docker_image_registry BASE_DOCKER_IMAGE_REGISTRY] [--use_sp_on_remote]
                      job_filepath
```
This command submits an experiment to a remote AzureML node.

If --include_local_tasks option is used, python scripts in the current directory or the specified directory will be sent to AzureML and be loaded as custom tasks.

If environment variable AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET are set, this command will use ServicePrincipalAuthentication. Otherwise, the AzureML's default authentication method will be used.

If --use_sp_on_remote flag is used, the environment variables for service principal authentication will be set to the AML job. Note that those information will be visible to anyone who has read access to the job.

Example
```bash
irisml_run_aml irisml/docs/example/mobilenetv2_mnist_training.json -p irisml-tasks-torchvision irisml-tasks-training --compute_target <cluster_name> --subscription_id <subscription_id> --workspace <workspacename>
```

## Tasks
### run_azureml_child
Submit a new AzureML job as a child of the current run. Raises an exception if the current environment was not on AzureML.
