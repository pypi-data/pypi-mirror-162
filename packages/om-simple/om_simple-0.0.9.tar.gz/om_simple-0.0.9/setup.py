import setuptools
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="om_simple",
    packages = find_packages(),
    package_data={'om_simple': ['*.jpg']},
    include_package_data=True,
    version="0.0.9",
    author="kyusonglee",
    description="OM Simple",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.soco.ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        "matplotlib",
        "opencv-python-headless<4.3",
        "pandas",
        "Image",
        #"torch",
        #"torchmetrics",
        #"torchvision",
        "pytorch-lightning",
        "timm",
        "tqdm"
    ]
)
