import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyboto',
    version='v0.1.4',
    license='Mozilla Public License Version 2.0',
    author='steven-purcell',
    url='https://github.com/steven-purcell/pyboto',
    author_email='steven.ray.purcell@gmail.com',
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas',
        'boto3',
        'botocore'
    ],
    description='A simple boto3 wrapper to complete common operations in S3 such as '
                'get or put csv files, list objects and keys, etc.'
)
