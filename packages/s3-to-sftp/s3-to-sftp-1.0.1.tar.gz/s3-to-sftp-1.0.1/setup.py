# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['s3_to_sftp']

package_data = \
{'': ['*']}

install_requires = \
['aws-embedded-metrics>=2.0,<3.0',
 'boto3>=1.24.22,<2.0.0',
 'compose-x-common>=1.0.3,<2.0.0',
 'jsonschema>=4,<5',
 'paramiko>=2.11.0,<3.0.0']

setup_kwargs = {
    'name': 's3-to-sftp',
    'version': '1.0.1',
    'description': 'S3 to SFTP application / watcher. Feeds from S3 to SQS notifications.',
    'long_description': '============\nS3 to SFTP\n============\n\nSimple application that listens on a SQS Queue and transfers files from S3\nto a SFTP Server.\n\nThe authentication can be done via username/password or username/private key.\nPrivate key should be stored "as-is" in AWS Secrets Manager.\n\nThe container must have an environment variable ``SFTP_TARGET``, that follows the format below.\nYou can set an enviroment variable for each of the below, using the property name as environment variable name.\n\nThe value in environment variables overrides the values otherwise set.\n\nBuild\n======\n\nYou can build the docker image with the following commands\n\n.. code-block::\n\n    docker build . -t s3-to-sftp\n\nAlternatively, using docker-compose\n\n.. code-block::\n\n    docker-compose build\n\nDeploy with ECS Compose-X\n===========================\n\nWe highly recommend that you store the value for ``SFTP_TARGET`` in AWS Secrets Manager.\n\nInstall compose-x\n------------------\n\n.. code-block::\n\n    python3 -m venv compose-x\n    source compose-x/bin/activate\n    pip install pip -U; pip install ecs-composex\n\nDeploy\n--------\n\nYou might need to update the settings in the aws.yaml file to meet your environment settings.\nOn start, the connection to the SFTP server is not established, so the deployment won\'t fail\nbecause of that. However, it requires to have the ``SFTP_TARGET`` details setup in before it\nstarts listening on the SQS queue jobs.\n\n.. code-block::\n\n    ecs-compose-x up -d templates -f docker-compose.yaml -f aws.yaml -p s3-to-sftp-testing\n\nMonitoring\n-----------\n\nIn AWS CloudWatch, you will see new metrics in a Namespace called ``S3ToSFTP`` which is going to have\nsome metrics, here for statistics.\n\nThese metrics are published using `EMF`_.\n\n.. _EMF: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Embedded_Metric_Format_Specification.html\n\n\nSFTP_TARGET format\n===================\n\n.. code-block::\n\n    {\n        "$schema": "http://json-schema.org/draft-07/schema#",\n        "id": "sftp-secret-format",\n        "type": "object",\n        "additionalProperties": false,\n        "properties": {\n            "host": {\n                "type": "string",\n                "format": "idn-hostname"\n            },\n            "port": {\n                "type": "number",\n                "minimum": 1,\n                "maximum": 65535\n            },\n            "username": {\n                "type": "string"\n            },\n            "password": {\n                "type": "string"\n            },\n            "default_path": {\n                "type": "string"\n            },\n            "private_key": {\n                "type": "string"\n            },\n            "private_key_pass": {\n                "type": "string"\n            }\n        },\n        "required": [\n            "host",\n            "port",\n            "username"\n        ]\n    }\n',
    'author': 'John Preston',
    'author_email': 'john@ews-network.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
