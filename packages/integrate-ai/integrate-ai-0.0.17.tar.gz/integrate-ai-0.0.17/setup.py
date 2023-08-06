from setuptools import setup, find_packages
from pathlib import Path

version = "0.0.17"

name = "integrate-ai"

required = ["typer[all]", "docker", "pyjwt"]

directory = Path(__file__).parent
long_description = (directory / "README.md").read_text()
license = (directory / "LICENSE").read_text()

setup(
    name=name,
    version=version,
    description="integrate.ai Command Line Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src", exclude=["test"]),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=required,
    entry_points={"console_scripts": ["iai = integrate_ai.cli:main"]},
    license=license,
    maintainer="integrate.ai",
    maintainer_email="contact@integrate.ai",
    url="https://integrate.ai",
    project_urls={"Twitter": "https://twitter.com/integrateai"},
)
