import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "control-broker",
    "version": "0.12.1",
    "description": "Control Broker allows customers to deploy an HTTP API on AWS that executes Policy as Code (PaC) policies using Open Policy Agent (OPA) or CloudFormation Guard to evaluate inputs and return decisions.",
    "license": "Apache-2.0",
    "url": "https://github.com/VerticalRelevance/control-broker/",
    "long_description_content_type": "text/markdown",
    "author": "Clark Schneider<cschneider@verticalrelevance.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/VerticalRelevance/control-broker.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "control_broker",
        "control_broker._jsii"
    ],
    "package_data": {
        "control_broker._jsii": [
            "control-broker@0.12.1.jsii.tgz"
        ],
        "control_broker": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.28.1, <3.0.0",
        "aws-cdk.aws-apigatewayv2-alpha==2.28.1.a0",
        "aws-cdk.aws-apigatewayv2-authorizers-alpha==2.28.1.a0",
        "aws-cdk.aws-apigatewayv2-integrations-alpha==2.28.1.a0",
        "aws-cdk.aws-lambda-python-alpha==2.28.1.a0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.61.0, <2.0.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
