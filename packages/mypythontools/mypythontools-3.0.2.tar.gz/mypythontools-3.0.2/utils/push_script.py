"""Push the CI pipeline. Format, create commit from all the changes, push and deploy to PyPi."""

from mypythontools_cicd.cicd import cicd_pipeline, default_pipeline_config


if __name__ == "__main__":
    default_pipeline_config.deploy = True
    default_pipeline_config.test.prepare_test_venvs = ["3.7", "3.8", "3.9", "3.10", "wsl-3.7", "wsl-3.10"]
    default_pipeline_config.test.virtualenvs = [
        "tests/venv/3.7",
        "tests/venv/3.8",
        "tests/venv/3.9",
        "tests/venv/3.10",
    ]
    default_pipeline_config.test.sync_test_requirements = ["tests.txt"]
    default_pipeline_config.test.sync_test_requirements_path = "requirements"

    # default_pipeline_config.do_only = "test"

    # All the parameters can be overwritten via CLI args
    cicd_pipeline(config=default_pipeline_config)
