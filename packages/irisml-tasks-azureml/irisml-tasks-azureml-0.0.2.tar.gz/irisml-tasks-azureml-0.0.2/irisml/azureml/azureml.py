import contextlib
import json
import logging
import os
import pathlib
import re
import shutil
import tempfile
import typing
import azureml.core
from irisml.core import JobDescription

logger = logging.getLogger(__name__)


class AMLJobManager:
    def __init__(self, subscription_id, workspace_name, experiment_name, compute_target_name, use_sp_on_remote=False):
        """
        Args:
            subscription_id (str): The subscription ID for the azureml resource.
            workspace_name (str): Workspace name
            experiment_name (str): Experiment name
            compute_target_name (str): Compute Target name
            use_sp_on_remote (bool): If True, get AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET from environment and send it to the AzureML.
        """
        self._workspace = self._get_workspace(subscription_id, workspace_name)
        self._experiment = azureml.core.Experiment(workspace=self._workspace, name=experiment_name)
        self._compute_target_name = compute_target_name
        self._use_sp_on_remote = use_sp_on_remote

    def _get_workspace(self, subscription_id, workspace_name):
        auth = None
        if os.getenv('AZURE_TENANT_ID') and os.getenv('AZURE_CLIENT_ID') and os.getenv('AZURE_CLIENT_SECRET'):
            logger.info(f"Using Service Principal to authenticate to AzureML. tenant_id={os.getenv('AZURE_TENANT_ID')}, client_id={os.getenv('AZURE_CLIENT_ID')}")
            auth = azureml.core.authentication.ServicePrincipalAuthentication(os.getenv('AZURE_TENANT_ID'), os.getenv('AZURE_CLIENT_ID'), os.getenv('AZURE_CLIENT_SECRET'))

        ws_dict = azureml.core.Workspace.list(subscription_id=subscription_id, auth=auth)
        workspaces = ws_dict.get(workspace_name)
        if not workspaces:
            raise RuntimeError(f"Workspace {workspace_name} is not found.")
        if len(workspaces) >= 2:
            raise RuntimeError("Multiple workspaces are found.")

        return workspaces[0]

    def _get_environment(self, job_env):
        env = azureml.core.environment.Environment(name='irisml')
        env.python.user_managed_dependencies = True
        if job_env.base_docker_image:
            env.docker.base_image = job_env.base_docker_image[0]
            env.docker.base_image_registry.address = job_env.base_docker_image[1]
        else:
            env.docker.base_image = None
            env.docker.base_dockerfile = job_env.dockerfile
        return env

    def _get_compute_target(self):
        if self._compute_target_name == 'local':
            return 'local'
        return azureml.core.compute.ComputeTarget(workspace=self._workspace, name=self._compute_target_name)

    def _get_environment_variables(self):
        env_vars = {}
        if self._use_sp_on_remote:
            tenant_id = os.getenv('AZURE_TENANT_ID')
            client_id = os.getenv('AZURE_CLIENT_ID')
            client_secret = os.getenv('AZURE_CLIENT_SECRET')
            logger.info(f"Using Service Principal on the remote. AZURE_TENANT_ID={tenant_id}, AZURE_CLIENT_ID={client_id}, AZURE_CLIENT_SECRET={bool(client_secret)}")
            env_vars['AZURE_TENANT_ID'] = tenant_id
            env_vars['AZURE_CLIENT_ID'] = client_id
            env_vars['AZURE_CLIENT_SECRET'] = client_secret

        return env_vars

    def get_script_run_config(self, project_dir, job, job_env, environment_variables):
        command = job.command
        if not environment_variables.get('AZURE_CLIENT_ID'):
            # For Managed Identity
            command = 'AZURE_CLIENT_ID=$DEFAULT_IDENTITY_CLIENT_ID ' + command

        script_run_config = azureml.core.ScriptRunConfig(source_directory=project_dir, compute_target=self._get_compute_target(), environment=self._get_environment(job_env), command=command)
        script_run_config.run_config.environment_variables.update(environment_variables)
        return script_run_config

    def submit(self, job, job_env):
        with job.create_project_directory() as project_dir:
            script_run_config = self.get_script_run_config(project_dir, job, job_env, self._get_environment_variables())
            run = self._experiment.submit(config=script_run_config)
            return AzureMLRun(run)


class Job:
    def __init__(self, job_description_filepath: pathlib.Path, environment_variables: typing.Dict):
        # Check if the given file is a valid JobDescription
        job_description_dict = json.loads(job_description_filepath.read_text())
        job_description = JobDescription.from_dict(job_description_dict)
        if job_description is None:
            raise RuntimeError(f"The given file is not a valid job description: {job_description_filepath}")

        self._job_description_filepath = job_description_filepath
        self._environment_variables = environment_variables
        self._custom_task_relative_paths = []

    @property
    def name(self):
        return self._job_description_filepath.name

    @property
    def command(self):
        c = f'irisml_run {self.name} -v'
        for key, value in self._environment_variables.items():
            c += f' -e {key}="{value}"'
        if self._custom_task_relative_paths:  # Add the current directory to PYTHONPATH so that the custom tasks can be loaded.
            c = 'PYTHONPATH=.:$PYTHONPATH ' + c
        return c

    def add_custom_tasks(self, tasks_dir: pathlib.Path):
        self._custom_task_relative_paths = [str(p.relative_to(tasks_dir)) for pattern in ['*.py', '*.json', '*.yaml'] for p in tasks_dir.rglob(pattern)]
        self._custom_task_dir = tasks_dir

    @contextlib.contextmanager
    def create_project_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            shutil.copy(self._job_description_filepath, temp_dir)
            for p in self._custom_task_relative_paths:
                if p.startswith('irisml/tasks'):
                    dest = temp_dir / p
                else:
                    dest = temp_dir / 'irisml' / 'tasks' / p

                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(self._custom_task_dir / p, dest)
            yield temp_dir


class JobEnvironment:
    STANDARD_PACKAGES = ['irisml', 'irisml-tasks', 'irisml-tasks-training']

    def __init__(self, base_docker_image, base_docker_image_registry, custom_packages, extra_index_url=None):
        self._base_docker_image = base_docker_image
        self._base_docker_image_registry = base_docker_image_registry
        # Make sure it's sorted so that the Docker image will be cached correctly.
        self._pip_packages = sorted(self._add_standard_packages(custom_packages))
        self._extra_index_url = extra_index_url

    @property
    def base_docker_image(self):
        return self._base_docker_image and (self._base_docker_image, self._base_docker_image_registry)

    @property
    def dockerfile(self):
        pip_packages_str = ' '.join([f'"{p}"' for p in self._pip_packages])
        pip_option = f' --extra-index-url {self._extra_index_url}' if self._extra_index_url else ''
        return """FROM ubuntu:20.04
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip python3-venv python3.8-dev build-essential && rm -rf /var/lib/apt/lists/*
RUN python3.8 -m venv /opt/python
ENV PATH=/opt/python/bin:$PATH
RUN pip install --disable-pip-version-check --no-cache-dir setuptools wheel
RUN pip install {} {}
""".format(pip_packages_str, pip_option)

    def _add_standard_packages(self, custom_packages):
        """Add standard packages so that there are no duplicates."""
        name_pattern = re.compile(r'^[a-zA-Z0-9.\-_]*')
        package_names = [name_pattern.match(p).group(0) for p in custom_packages]
        missing_packages = set(self.STANDARD_PACKAGES) - set(package_names)
        return custom_packages + list(missing_packages)

    def __str__(self):
        s = ''
        if self._base_docker_image:
            s += f'Base Docker: {self._base_docker_image}'
            if self._base_docker_image_registry:
                s += f' ({self._base_docker_image_registry})'
            s += '\n'
        s += f'Packages: {",".join(self._pip_packages)}'
        if self._extra_index_url:
            s += f'\nExtra index url: {self._extra_index_url}'
        return s


class AzureMLRun:
    def __init__(self, run):
        self._run = run

    def wait_for_completion(self):
        return self._run.wait_for_completion(show_output=True)

    def get_portal_url(self):
        return self._run.get_portal_url()

    def __str__(self):
        return f'AzureML Run(id={self._run.id}, url={self._run.get_portal_url()}'
