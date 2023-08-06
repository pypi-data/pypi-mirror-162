import pathlib
import tempfile
import unittest
from irisml.azureml import Job, JobEnvironment


class TestAzureML(unittest.TestCase):
    def test_job(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            job_filepath = pathlib.Path(temp_dir) / 'fake_config.json'
            job_filepath.write_text('{"tasks": []}')
            job = Job(job_filepath, {'env': 'value'})
            self.assertEqual(job.name, 'fake_config.json')
            self.assertTrue('fake_config.json' in job.command)

    def test_duplicated_packages(self):
        job_env = JobEnvironment(None, None, ['irisml>3', 'test_package'])
        self.assertEqual(set(job_env._pip_packages), set(['irisml>3', 'test_package', 'irisml-tasks', 'irisml-tasks-training']))

    def test_package_sorted(self):
        job_env = JobEnvironment(None, None, ['test_package3', 'test_package2'])
        self.assertEqual(job_env._pip_packages, ['irisml', 'irisml-tasks', 'irisml-tasks-training', 'test_package2', 'test_package3'])
