from setuptools import setup, find_packages
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "requirements.txt")) as f:
    required_packages = f.read().splitlines()
with open(os.path.join(dir_path, "README.md"), "r") as fh:
    long_description = fh.read()

if __name__ == "__main__":
    setup(long_description=long_description,
          long_description_content_type="text/markdown",
          include_package_data=True,
          packages=find_packages(),
          install_requires=required_packages,)
