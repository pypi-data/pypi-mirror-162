'''
# Control Broker

*Give everyone in your organization subsecond security and compliance decisions based on the organization's latest policies.*

## Contributing

Please see [CONTRIBUTING.md](./CONTRIBUTING.md).

## Features

* Runs a Policy as Code service as a serverless AWS application - you bring the policies, and Control Broker helps you store, organize, and use them - plus it helps you monitor, and analyze their usage.
* Defined in the AWS Python CDK for push-button, repeatable deployment.
* Can be invoked from anywhere in your environment that can invoke an API Gateway API.
* Supports policies written for Open Policy Agent (CloudFormation Guard planned).
* Also helps with notifications, auditing, and analysis of discovered compliance issues.

## Example use cases

* [Using the Control Broker from a CodePipeline application pipeline to block deployment of non-compliant CDK resources](https://github.com/VerticalRelevance/control-broker-codepipeline-example)
* [Using the Control Broker to detect non-compliant changes to deployed resources with AWS Config](https://github.com/VerticalRelevance/control-broker-consumer-example-config)
* [Using the Control Broker from a development machine to evaluate IaC against the organization's latest security policies as it is being written](https://github.com/VerticalRelevance/control-broker-consumer-example-local-dev)

## Deploying Your Own Control Broker

<!--### Upload your secret config file--><!--The Control Broker needs some secret values to be available in its environment. These are stored in a Secrets Manager Secret as a JSON--><!--blob, and the Control Broker's deployment mechanisms grab these values as they need to.--><!--Before proceeding, you'll have to copy [our example secrets file](./supplementary_files/) to a secure location on your machine and replace--><!--the values in it with your own. Then, [create a Secret--><!--in Secrets--><!--Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/tutorials_basic.html#tutorial-basic-step1)--><!--called "control-broker/secret-config" with this JSON text as its value.--><!--![Using the SecretsManager console to create the secret value](docs/diagrams/images/secretsmanager-console-secret-config.png)--><!--![Using the SecretsManager console to name the secret and give it a description](docs/diagrams/images/secretsmanager-console-secret-config-name-page.png)--><!--Here are some helpful hints about what to put in these values:--><!--> Note: You can change the name of the secret that Control Broker uses by changing the value of the "control-broker/secret-config/secrets-manager-secret-id" context variable.-->

### Deploy the CDK app

Install the [AWS CDK Toolkit
v2](https://docs.aws.amazon.com/cdk/v2/guide/cli.html) CLI tool.

If you encounter issues running the `cdk` commands below, check the version of
`aws-cdk-lib` from [./requirements.txt](./requirements.txt) for the exact
version of the CDK library used in this repo. The latest v2 version of the CDK
Toolkit should be compatible, but try installing the CDK Toolkit version
matching `requirements.txt` before trying other things to resolve your issues.

Clone this repo to your machine before proceeding.

Follow the setup steps below to properly configure the environment and first
deployment of the infrastructure.

To manually create a virtualenv on MacOS and Linux:

`$ python3 -m venv .venv`

After the init process completes and the virtualenv is created, you can use the
following step to activate your virtualenv.

`$ source .venv/bin/activate`

If you are on a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

`$ pip install -r requirements.txt`

[Bootstrap](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-bootstrap) the
cdk app:

`cdk bootstrap`

At this point you can
[deploy](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-deploy) the CDK
app for this blueprint:

`$ cdk deploy`

After running `cdk deploy`, the Control Broker will be set up.

## Next Steps

Try launching one of the [Example use cases](./README.md#example-use-cases)!
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_apigateway
import aws_cdk.aws_apigatewayv2_alpha
import aws_cdk.aws_lambda
import aws_cdk.aws_logs
import aws_cdk.aws_s3
import constructs


class Api(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.Api",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_access_log_group: typing.Optional[aws_cdk.aws_logs.LogGroup] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api_access_log_group: 
        '''
        props = ApiProps(api_access_log_group=api_access_log_group)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addInputHandler")
    def add_input_handler(self, input_handler: "BaseInputHandler") -> None:
        '''
        :param input_handler: -
        '''
        return typing.cast(None, jsii.invoke(self, "addInputHandler", [input_handler]))

    @jsii.member(jsii_name="configureAwsApiGatewayHTTPApiLogging")
    def _configure_aws_api_gateway_http_api_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "configureAwsApiGatewayHTTPApiLogging", []))

    @jsii.member(jsii_name="getUrlForInputHandler")
    def get_url_for_input_handler(
        self,
        input_handler: "BaseInputHandler",
    ) -> typing.Optional[builtins.str]:
        '''
        :param input_handler: -
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "getUrlForInputHandler", [input_handler]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessLogRetention")
    def access_log_retention(self) -> aws_cdk.aws_logs.RetentionDays:
        return typing.cast(aws_cdk.aws_logs.RetentionDays, jsii.get(self, "accessLogRetention"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiAccessLogGroup")
    def api_access_log_group(self) -> aws_cdk.aws_logs.LogGroup:
        return typing.cast(aws_cdk.aws_logs.LogGroup, jsii.get(self, "apiAccessLogGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsApiGatewayHTTPApi")
    def aws_api_gateway_http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        '''Lazily create the HTTP API when it is first accessed.'''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpApi, jsii.get(self, "awsApiGatewayHTTPApi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsApiGatewayRestApi")
    def aws_api_gateway_rest_api(self) -> aws_cdk.aws_apigateway.RestApi:
        '''Lazily create the Rest API when it is first accessed.'''
        return typing.cast(aws_cdk.aws_apigateway.RestApi, jsii.get(self, "awsApiGatewayRestApi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputHandlers")
    def _input_handlers(self) -> typing.List["BaseInputHandler"]:
        return typing.cast(typing.List["BaseInputHandler"], jsii.get(self, "inputHandlers"))

    @_input_handlers.setter
    def _input_handlers(self, value: typing.List["BaseInputHandler"]) -> None:
        jsii.set(self, "inputHandlers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evalEngine")
    def eval_engine(self) -> typing.Optional["BaseEvalEngine"]:
        return typing.cast(typing.Optional["BaseEvalEngine"], jsii.get(self, "evalEngine"))

    @eval_engine.setter
    def eval_engine(self, value: typing.Optional["BaseEvalEngine"]) -> None:
        jsii.set(self, "evalEngine", value)


@jsii.data_type(
    jsii_type="control-broker.ApiBindingHeaders",
    jsii_struct_bases=[],
    name_mapping={},
)
class ApiBindingHeaders:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiBindingHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="control-broker.ApiProps",
    jsii_struct_bases=[],
    name_mapping={"api_access_log_group": "apiAccessLogGroup"},
)
class ApiProps:
    def __init__(
        self,
        *,
        api_access_log_group: typing.Optional[aws_cdk.aws_logs.LogGroup] = None,
    ) -> None:
        '''
        :param api_access_log_group: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if api_access_log_group is not None:
            self._values["api_access_log_group"] = api_access_log_group

    @builtins.property
    def api_access_log_group(self) -> typing.Optional[aws_cdk.aws_logs.LogGroup]:
        result = self._values.get("api_access_log_group")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.LogGroup], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="control-broker.AwsApiType")
class AwsApiType(enum.Enum):
    HTTP = "HTTP"
    REST = "REST"
    WEBSOCKET = "WEBSOCKET"


class BaseApiBinding(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="control-broker.BaseApiBinding",
):
    '''Base class for an API Binding, which attaches an integration to an API and authorizes principals to invoke the integration via the API attachment.

    Defined abstractly since there are different types of APIs to attach integrations with
    and different principals to allow.
    '''

    def __init__(self, url_safe_name: builtins.str) -> None:
        '''
        :param url_safe_name: A name suitable for use in an integration's URL. Can contain slashes.
        '''
        jsii.create(self.__class__, self, [url_safe_name])

    @jsii.member(jsii_name="addHeaders")
    def add_headers(self) -> None:
        headers = ApiBindingHeaders()

        return typing.cast(None, jsii.invoke(self, "addHeaders", [headers]))

    @jsii.member(jsii_name="authorizePrincipalArn") # type: ignore[misc]
    @abc.abstractmethod
    def authorize_principal_arn(self, principal_arn: builtins.str) -> None:
        '''Give permission to a principal to call this API using this binding.

        This should be called after the binding has been added to all APIs.

        :param principal_arn: Principal to give calling permissions to.
        '''
        ...

    @jsii.member(jsii_name="bindTargetToApi") # type: ignore[misc]
    @abc.abstractmethod
    def bind_target_to_api(
        self,
        api: Api,
        target: "IIntegrationTarget",
    ) -> builtins.str:
        '''Bind this target to the API.

        :param api: -
        :param target: -

        :return: url
        '''
        ...

    @jsii.member(jsii_name="makeIntegrationForIntegrationTarget") # type: ignore[misc]
    @abc.abstractmethod
    def _make_integration_for_integration_target(
        self,
        target: "IIntegrationTarget",
    ) -> typing.Any:
        '''- Return an integration built for the integration target.

        :param target: -
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiType")
    @abc.abstractmethod
    def api_type(self) -> AwsApiType:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlSafeName")
    def url_safe_name(self) -> builtins.str:
        '''A name suitable for use in an integration's URL.

        Can contain slashes.
        '''
        return typing.cast(builtins.str, jsii.get(self, "urlSafeName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    @abc.abstractmethod
    def url(self) -> typing.Optional[builtins.str]:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headers")
    def _headers(self) -> ApiBindingHeaders:
        return typing.cast(ApiBindingHeaders, jsii.get(self, "headers"))

    @_headers.setter
    def _headers(self, value: ApiBindingHeaders) -> None:
        jsii.set(self, "headers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="method")
    def method(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "method"))

    @method.setter
    def method(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "method", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "path"))

    @path.setter
    def path(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "path", value)


class _BaseApiBindingProxy(BaseApiBinding):
    @jsii.member(jsii_name="authorizePrincipalArn")
    def authorize_principal_arn(self, principal_arn: builtins.str) -> None:
        '''Give permission to a principal to call this API using this binding.

        This should be called after the binding has been added to all APIs.

        :param principal_arn: Principal to give calling permissions to.
        '''
        return typing.cast(None, jsii.invoke(self, "authorizePrincipalArn", [principal_arn]))

    @jsii.member(jsii_name="bindTargetToApi")
    def bind_target_to_api(
        self,
        api: Api,
        target: "IIntegrationTarget",
    ) -> builtins.str:
        '''Bind this target to the API.

        :param api: -
        :param target: -

        :return: url
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "bindTargetToApi", [api, target]))

    @jsii.member(jsii_name="makeIntegrationForIntegrationTarget")
    def _make_integration_for_integration_target(
        self,
        target: "IIntegrationTarget",
    ) -> typing.Any:
        '''- Return an integration built for the integration target.

        :param target: -
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "makeIntegrationForIntegrationTarget", [target]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiType")
    def api_type(self) -> AwsApiType:
        return typing.cast(AwsApiType, jsii.get(self, "apiType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseApiBinding).__jsii_proxy_class__ = lambda : _BaseApiBindingProxy


@jsii.data_type(
    jsii_type="control-broker.BaseApiBindingProps",
    jsii_struct_bases=[],
    name_mapping={"integration": "integration"},
)
class BaseApiBindingProps:
    def __init__(self, *, integration: typing.Any) -> None:
        '''
        :param integration: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "integration": integration,
        }

    @builtins.property
    def integration(self) -> typing.Any:
        result = self._values.get("integration")
        assert result is not None, "Required property 'integration' is missing"
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseApiBindingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="control-broker.BaseEvalEngineProps",
    jsii_struct_bases=[],
    name_mapping={"binding": "binding"},
)
class BaseEvalEngineProps:
    def __init__(self, *, binding: BaseApiBinding) -> None:
        '''
        :param binding: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "binding": binding,
        }

    @builtins.property
    def binding(self) -> BaseApiBinding:
        result = self._values.get("binding")
        assert result is not None, "Required property 'binding' is missing"
        return typing.cast(BaseApiBinding, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseEvalEngineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="control-broker.BaseInputHandlerProps",
    jsii_struct_bases=[],
    name_mapping={"binding": "binding"},
)
class BaseInputHandlerProps:
    def __init__(self, *, binding: BaseApiBinding) -> None:
        '''
        :param binding: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "binding": binding,
        }

    @builtins.property
    def binding(self) -> BaseApiBinding:
        result = self._values.get("binding")
        assert result is not None, "Required property 'binding' is missing"
        return typing.cast(BaseApiBinding, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseInputHandlerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ControlBroker(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.ControlBroker",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api: Api,
        eval_engine: "BaseEvalEngine",
        input_bucket: aws_cdk.aws_s3.Bucket,
        input_handlers: typing.Sequence["BaseInputHandler"],
        results_bucket: aws_cdk.aws_s3.Bucket,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api: 
        :param eval_engine: 
        :param input_bucket: 
        :param input_handlers: 
        :param results_bucket: 
        '''
        props = ControlBrokerProps(
            api=api,
            eval_engine=eval_engine,
            input_bucket=input_bucket,
            input_handlers=input_handlers,
            results_bucket=results_bucket,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addInputHandler")
    def add_input_handler(
        self,
        input_handler: "BaseInputHandler",
    ) -> typing.Optional[builtins.str]:
        '''
        :param input_handler: -
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "addInputHandler", [input_handler]))

    @jsii.member(jsii_name="getUrlForInputHandler")
    def get_url_for_input_handler(
        self,
        input_handler: "BaseInputHandler",
    ) -> typing.Optional[builtins.str]:
        '''
        :param input_handler: -
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "getUrlForInputHandler", [input_handler]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="api")
    def api(self) -> Api:
        return typing.cast(Api, jsii.get(self, "api"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="params")
    def _params(self) -> "ControlBrokerParams":
        return typing.cast("ControlBrokerParams", jsii.get(self, "params"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evalEngine")
    def eval_engine(self) -> typing.Optional["BaseEvalEngine"]:
        return typing.cast(typing.Optional["BaseEvalEngine"], jsii.get(self, "evalEngine"))

    @eval_engine.setter
    def eval_engine(self, value: typing.Optional["BaseEvalEngine"]) -> None:
        jsii.set(self, "evalEngine", value)


@jsii.data_type(
    jsii_type="control-broker.ControlBrokerParams",
    jsii_struct_bases=[],
    name_mapping={"input_bucket": "inputBucket", "results_bucket": "resultsBucket"},
)
class ControlBrokerParams:
    def __init__(
        self,
        *,
        input_bucket: aws_cdk.aws_s3.Bucket,
        results_bucket: aws_cdk.aws_s3.Bucket,
    ) -> None:
        '''Parameters that components of Control Broker may need.

        :param input_bucket: 
        :param results_bucket: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "input_bucket": input_bucket,
            "results_bucket": results_bucket,
        }

    @builtins.property
    def input_bucket(self) -> aws_cdk.aws_s3.Bucket:
        result = self._values.get("input_bucket")
        assert result is not None, "Required property 'input_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.Bucket, result)

    @builtins.property
    def results_bucket(self) -> aws_cdk.aws_s3.Bucket:
        result = self._values.get("results_bucket")
        assert result is not None, "Required property 'results_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.Bucket, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ControlBrokerParams(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="control-broker.ControlBrokerProps",
    jsii_struct_bases=[],
    name_mapping={
        "api": "api",
        "eval_engine": "evalEngine",
        "input_bucket": "inputBucket",
        "input_handlers": "inputHandlers",
        "results_bucket": "resultsBucket",
    },
)
class ControlBrokerProps:
    def __init__(
        self,
        *,
        api: Api,
        eval_engine: "BaseEvalEngine",
        input_bucket: aws_cdk.aws_s3.Bucket,
        input_handlers: typing.Sequence["BaseInputHandler"],
        results_bucket: aws_cdk.aws_s3.Bucket,
    ) -> None:
        '''
        :param api: 
        :param eval_engine: 
        :param input_bucket: 
        :param input_handlers: 
        :param results_bucket: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api": api,
            "eval_engine": eval_engine,
            "input_bucket": input_bucket,
            "input_handlers": input_handlers,
            "results_bucket": results_bucket,
        }

    @builtins.property
    def api(self) -> Api:
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(Api, result)

    @builtins.property
    def eval_engine(self) -> "BaseEvalEngine":
        result = self._values.get("eval_engine")
        assert result is not None, "Required property 'eval_engine' is missing"
        return typing.cast("BaseEvalEngine", result)

    @builtins.property
    def input_bucket(self) -> aws_cdk.aws_s3.Bucket:
        result = self._values.get("input_bucket")
        assert result is not None, "Required property 'input_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.Bucket, result)

    @builtins.property
    def input_handlers(self) -> typing.List["BaseInputHandler"]:
        result = self._values.get("input_handlers")
        assert result is not None, "Required property 'input_handlers' is missing"
        return typing.cast(typing.List["BaseInputHandler"], result)

    @builtins.property
    def results_bucket(self) -> aws_cdk.aws_s3.Bucket:
        result = self._values.get("results_bucket")
        assert result is not None, "Required property 'results_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.Bucket, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ControlBrokerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="control-broker.EvalEngineBindingConfiguration",
    jsii_struct_bases=[],
    name_mapping={"binding": "binding", "eval_engine": "evalEngine"},
)
class EvalEngineBindingConfiguration:
    def __init__(
        self,
        *,
        binding: typing.Optional[BaseApiBinding] = None,
        eval_engine: typing.Optional["BaseEvalEngine"] = None,
    ) -> None:
        '''
        :param binding: 
        :param eval_engine: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if binding is not None:
            self._values["binding"] = binding
        if eval_engine is not None:
            self._values["eval_engine"] = eval_engine

    @builtins.property
    def binding(self) -> typing.Optional[BaseApiBinding]:
        result = self._values.get("binding")
        return typing.cast(typing.Optional[BaseApiBinding], result)

    @builtins.property
    def eval_engine(self) -> typing.Optional["BaseEvalEngine"]:
        result = self._values.get("eval_engine")
        return typing.cast(typing.Optional["BaseEvalEngine"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EvalEngineBindingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HttpApiBinding(
    BaseApiBinding,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.HttpApiBinding",
):
    def __init__(self, url_safe_name: builtins.str) -> None:
        '''
        :param url_safe_name: -
        '''
        jsii.create(self.__class__, self, [url_safe_name])

    @jsii.member(jsii_name="authorizePrincipalArn")
    def authorize_principal_arn(self, principal_arn: builtins.str) -> None:
        '''Give permission to a principal to call this API using this binding.

        This should be called after the binding has been added to all APIs.

        :param principal_arn: -
        '''
        return typing.cast(None, jsii.invoke(self, "authorizePrincipalArn", [principal_arn]))

    @jsii.member(jsii_name="bindTargetToApi")
    def bind_target_to_api(
        self,
        api: Api,
        target: "IIntegrationTarget",
    ) -> builtins.str:
        '''Bind this target to the API.

        :param api: -
        :param target: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "bindTargetToApi", [api, target]))

    @jsii.member(jsii_name="makeIntegrationForIntegrationTarget")
    def _make_integration_for_integration_target(
        self,
        target: "IIntegrationTarget",
    ) -> typing.Any:
        '''Note: JSII complains if we make the return type HTTPRouteIntegration, ostensibly because of its restrictions on Generics.

        :param target: -
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "makeIntegrationForIntegrationTarget", [target]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiType")
    def api_type(self) -> AwsApiType:
        return typing.cast(AwsApiType, jsii.get(self, "apiType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizedPrincipalArns")
    def _authorized_principal_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "authorizedPrincipalArns"))

    @_authorized_principal_arns.setter
    def _authorized_principal_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "authorizedPrincipalArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routes")
    def _routes(self) -> typing.List[aws_cdk.aws_apigatewayv2_alpha.HttpRoute]:
        return typing.cast(typing.List[aws_cdk.aws_apigatewayv2_alpha.HttpRoute], jsii.get(self, "routes"))

    @_routes.setter
    def _routes(
        self,
        value: typing.List[aws_cdk.aws_apigatewayv2_alpha.HttpRoute],
    ) -> None:
        jsii.set(self, "routes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="api")
    def _api(self) -> typing.Optional[Api]:
        return typing.cast(typing.Optional[Api], jsii.get(self, "api"))

    @_api.setter
    def _api(self, value: typing.Optional[Api]) -> None:
        jsii.set(self, "api", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="method")
    def method(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "method"))

    @method.setter
    def method(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "method", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "path"))

    @path.setter
    def path(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="route")
    def route(self) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpRoute]:
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpRoute], jsii.get(self, "route"))

    @route.setter
    def route(
        self,
        value: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpRoute],
    ) -> None:
        jsii.set(self, "route", value)


@jsii.data_type(
    jsii_type="control-broker.HttpApiBindingAddToApiOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class HttpApiBindingAddToApiOptions:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpApiBindingAddToApiOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="control-broker.IIntegrationTarget")
class IIntegrationTarget(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="binding")
    def binding(self) -> BaseApiBinding:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> "IntegrationTargetType":
        ...


class _IIntegrationTargetProxy:
    __jsii_type__: typing.ClassVar[str] = "control-broker.IIntegrationTarget"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="binding")
    def binding(self) -> BaseApiBinding:
        return typing.cast(BaseApiBinding, jsii.get(self, "binding"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> "IntegrationTargetType":
        return typing.cast("IntegrationTargetType", jsii.get(self, "integrationTargetType"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IIntegrationTarget).__jsii_proxy_class__ = lambda : _IIntegrationTargetProxy


@jsii.interface(jsii_type="control-broker.ILambdaIntegrationTarget")
class ILambdaIntegrationTarget(IIntegrationTarget, typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.Function:
        ...


class _ILambdaIntegrationTargetProxy(
    jsii.proxy_for(IIntegrationTarget) # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "control-broker.ILambdaIntegrationTarget"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "handler"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILambdaIntegrationTarget).__jsii_proxy_class__ = lambda : _ILambdaIntegrationTargetProxy


@jsii.data_type(
    jsii_type="control-broker.InputHandlerBindingConfiguration",
    jsii_struct_bases=[],
    name_mapping={"binding": "binding", "input_handler": "inputHandler"},
)
class InputHandlerBindingConfiguration:
    def __init__(
        self,
        *,
        binding: BaseApiBinding,
        input_handler: "BaseInputHandler",
    ) -> None:
        '''
        :param binding: 
        :param input_handler: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "binding": binding,
            "input_handler": input_handler,
        }

    @builtins.property
    def binding(self) -> BaseApiBinding:
        result = self._values.get("binding")
        assert result is not None, "Required property 'binding' is missing"
        return typing.cast(BaseApiBinding, result)

    @builtins.property
    def input_handler(self) -> "BaseInputHandler":
        result = self._values.get("input_handler")
        assert result is not None, "Required property 'input_handler' is missing"
        return typing.cast("BaseInputHandler", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InputHandlerBindingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="control-broker.InputHandlerBindingConfigurations",
    jsii_struct_bases=[],
    name_mapping={},
)
class InputHandlerBindingConfigurations:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InputHandlerBindingConfigurations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="control-broker.InputHandlerIntegrationContext",
    jsii_struct_bases=[],
    name_mapping={"external_url": "externalUrl"},
)
class InputHandlerIntegrationContext:
    def __init__(self, *, external_url: builtins.str) -> None:
        '''
        :param external_url: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "external_url": external_url,
        }

    @builtins.property
    def external_url(self) -> builtins.str:
        result = self._values.get("external_url")
        assert result is not None, "Required property 'external_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InputHandlerIntegrationContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="control-broker.IntegrationTargetType")
class IntegrationTargetType(enum.Enum):
    LAMBDA = "LAMBDA"
    STEP_FUNCTION = "STEP_FUNCTION"


@jsii.implements(IIntegrationTarget)
class BaseEvalEngine(
    constructs.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="control-broker.BaseEvalEngine",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        binding: BaseApiBinding,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param binding: 
        '''
        props = BaseEvalEngineProps(binding=binding)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="authorizePrincipalArn")
    def authorize_principal_arn(self, principal_arn: builtins.str) -> None:
        '''
        :param principal_arn: -
        '''
        return typing.cast(None, jsii.invoke(self, "authorizePrincipalArn", [principal_arn]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="binding")
    def binding(self) -> BaseApiBinding:
        return typing.cast(BaseApiBinding, jsii.get(self, "binding"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    @abc.abstractmethod
    def integration_target_type(self) -> IntegrationTargetType:
        ...


class _BaseEvalEngineProxy(BaseEvalEngine):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> IntegrationTargetType:
        return typing.cast(IntegrationTargetType, jsii.get(self, "integrationTargetType"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseEvalEngine).__jsii_proxy_class__ = lambda : _BaseEvalEngineProxy


@jsii.implements(IIntegrationTarget)
class BaseInputHandler(
    constructs.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="control-broker.BaseInputHandler",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        binding: BaseApiBinding,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param binding: 
        '''
        props = BaseInputHandlerProps(binding=binding)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="bindToApi") # type: ignore[misc]
    @abc.abstractmethod
    def bind_to_api(self, api: Api) -> None:
        '''
        :param api: -
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="binding")
    def binding(self) -> BaseApiBinding:
        return typing.cast(BaseApiBinding, jsii.get(self, "binding"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evalEngineCallerPrincipalArn")
    @abc.abstractmethod
    def eval_engine_caller_principal_arn(self) -> builtins.str:
        '''ARN of the principal that will call the EvalEngine endpoint.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    @abc.abstractmethod
    def integration_target_type(self) -> IntegrationTargetType:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlSafeName")
    @abc.abstractmethod
    def url_safe_name(self) -> builtins.str:
        '''Return a name for this input handler that is safe for use in the path of a URL.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="controlBrokerParams")
    @abc.abstractmethod
    def control_broker_params(self) -> ControlBrokerParams:
        ...

    @control_broker_params.setter
    @abc.abstractmethod
    def control_broker_params(self, value: ControlBrokerParams) -> None:
        ...


class _BaseInputHandlerProxy(BaseInputHandler):
    @jsii.member(jsii_name="bindToApi")
    def bind_to_api(self, api: Api) -> None:
        '''
        :param api: -
        '''
        return typing.cast(None, jsii.invoke(self, "bindToApi", [api]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evalEngineCallerPrincipalArn")
    def eval_engine_caller_principal_arn(self) -> builtins.str:
        '''ARN of the principal that will call the EvalEngine endpoint.'''
        return typing.cast(builtins.str, jsii.get(self, "evalEngineCallerPrincipalArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> IntegrationTargetType:
        return typing.cast(IntegrationTargetType, jsii.get(self, "integrationTargetType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlSafeName")
    def url_safe_name(self) -> builtins.str:
        '''Return a name for this input handler that is safe for use in the path of a URL.'''
        return typing.cast(builtins.str, jsii.get(self, "urlSafeName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="controlBrokerParams")
    def control_broker_params(self) -> ControlBrokerParams:
        return typing.cast(ControlBrokerParams, jsii.get(self, "controlBrokerParams"))

    @control_broker_params.setter
    def control_broker_params(self, value: ControlBrokerParams) -> None:
        jsii.set(self, "controlBrokerParams", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseInputHandler).__jsii_proxy_class__ = lambda : _BaseInputHandlerProxy


@jsii.implements(ILambdaIntegrationTarget)
class CloudFormationInputHandler(
    BaseInputHandler,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.CloudFormationInputHandler",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        binding: BaseApiBinding,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param binding: 
        '''
        props = BaseInputHandlerProps(binding=binding)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="bindToApi")
    def bind_to_api(self, api: Api) -> None:
        '''
        :param api: -
        '''
        return typing.cast(None, jsii.invoke(self, "bindToApi", [api]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evalEngineCallerPrincipalArn")
    def eval_engine_caller_principal_arn(self) -> builtins.str:
        '''ARN of the principal that will call the EvalEngine endpoint.'''
        return typing.cast(builtins.str, jsii.get(self, "evalEngineCallerPrincipalArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "handler"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> IntegrationTargetType:
        return typing.cast(IntegrationTargetType, jsii.get(self, "integrationTargetType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlSafeName")
    def url_safe_name(self) -> builtins.str:
        '''Return a name for this input handler that is safe for use in the path of a URL.'''
        return typing.cast(builtins.str, jsii.get(self, "urlSafeName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="controlBrokerParams")
    def control_broker_params(self) -> ControlBrokerParams:
        return typing.cast(ControlBrokerParams, jsii.get(self, "controlBrokerParams"))

    @control_broker_params.setter
    def control_broker_params(self, value: ControlBrokerParams) -> None:
        jsii.set(self, "controlBrokerParams", value)


@jsii.implements(ILambdaIntegrationTarget)
class OpaEvalEngine(
    BaseEvalEngine,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.OpaEvalEngine",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        binding: BaseApiBinding,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param binding: 
        '''
        props = BaseEvalEngineProps(binding=binding)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "handler"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> IntegrationTargetType:
        return typing.cast(IntegrationTargetType, jsii.get(self, "integrationTargetType"))


__all__ = [
    "Api",
    "ApiBindingHeaders",
    "ApiProps",
    "AwsApiType",
    "BaseApiBinding",
    "BaseApiBindingProps",
    "BaseEvalEngine",
    "BaseEvalEngineProps",
    "BaseInputHandler",
    "BaseInputHandlerProps",
    "CloudFormationInputHandler",
    "ControlBroker",
    "ControlBrokerParams",
    "ControlBrokerProps",
    "EvalEngineBindingConfiguration",
    "HttpApiBinding",
    "HttpApiBindingAddToApiOptions",
    "IIntegrationTarget",
    "ILambdaIntegrationTarget",
    "InputHandlerBindingConfiguration",
    "InputHandlerBindingConfigurations",
    "InputHandlerIntegrationContext",
    "IntegrationTargetType",
    "OpaEvalEngine",
]

publication.publish()
