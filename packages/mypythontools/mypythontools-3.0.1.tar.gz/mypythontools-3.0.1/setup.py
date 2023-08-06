"""Install the package."""

from setuptools import setup

from mypythontools_cicd import packages

if __name__ == "__main__":

    extras_requirements = {
        i: packages.get_requirements(f"extras_{i}.txt", path="requirements") for i in ["all", "plots"]
    }

    setup(
        **packages.get_package_setup_args("mypythontools", development_status="alpha"),
        **packages.personal_setup_args_preset,
        description="Some tools/functions/snippets used across projects.",
        long_description=packages.get_readme(),
        install_requires=packages.get_requirements("requirements.txt", path="requirements"),
        extras_require=extras_requirements,
    )
