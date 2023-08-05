"""
setup file for python package
"""
import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="Data_Adaptor_sourav",
    version="0.1.3",
    author="Crossml",
    author_email="sourav@crossml.com",
    packages=setuptools.find_packages(),
    description="Input Adaptor to verify file extension",
    long_description=description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords=['Input-adaptor', 'Adaptor', 'DataAdaptor'],
    python_requires='>=3',
    install_requires=['boto3', 'requests', ]
)

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
