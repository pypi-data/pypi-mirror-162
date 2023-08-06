from os import path

from setuptools import setup, find_packages

with open(path.join(path.abspath(path.dirname(__file__)), "README.md"), 'r', encoding="utf-8") as f:
    long_description = f.read()

setup(
    # https://packaging.python.org/specifications/core-metadata/#name
    name="basking-sdk",  # Required
    # https://www.python.org/dev/peps/pep-0440/
    version="{VERSION}",
    description="Basking.io python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://basking.io",
    author="Basking Automation GmbH",
    author_email="info@basking.io",
    keywords="occupancy analytics data api bas basking basking.io",
    packages=find_packages(where="./src/",exclude=["tests*"]),
    package_dir={"basking": "./src/basking"},
    python_requires=">=3.7, <4",
    install_requires=[
        "backoff==2.1.2",
        "boto3==1.24.45",
        "botocore==1.27.45",
        "certifi==2022.6.15; python_full_version >= '3.6.0'",
        "charset-normalizer==2.1.0; python_full_version >= '3.6.0'",
        "graphqlclient==0.2.4",
        "idna==3.3; python_version >= '3.5'",
        "jmespath==1.0.1; python_version >= '3.7'",
        "numpy==1.23.1; python_version < '3.10' and platform_machine != 'aarch64' and platform_machine != 'arm64'",
        "pandas==1.4.3",
        "python-dateutil==2.8.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pytz==2022.1",
        "requests==2.28.1",
        "s3transfer==0.6.0; python_version >= '3.7'",
        "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "urllib3==1.26.11; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5' and python_version < '4'",
    ],
    project_urls={
        "Bug Reports": "https://basking.io/contact-us/",
    },
)
