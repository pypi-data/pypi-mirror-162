'''
## OpenAPI Gateway

Define your APIs using [OpenAPI v3](https://swagger.io/specification/), and leverage the power of generated clients and documentation, automatic input validation, and type safe client and server code!

This package vends a projen project type which allows you to define an API using [OpenAPI v3](https://swagger.io/specification/), and a construct which manages deploying this API in API Gateway, given a lambda integration for every operation.

The project will generate models and clients from your OpenAPI spec in your desired languages, and can be utilised both client side or server side in lambda handlers. The project type also generates a wrapper construct which adds type safety to ensure a lambda integration is provided for every API integration.

When you change your API specification, just run `npx projen` again to regenerate all of this!

### Project

#### Typescript

It's recommended that this project is used as part of an `nx_monorepo` project. You can still use this as a standalone project if you like (eg `npx projen new --from @aws-prototyping-sdk/open-api-gateway open-api-gateway-ts`), however you will need to manage build order (ie building the generated client first, followed by the project).

For usage in a monorepo:

Create the project in your .projenrc:

```python
import { ClientLanguage, DocumentationFormat, OpenApiGatewayTsProject } from "@aws-prototyping-sdk/open-api-gateway";

new OpenApiGatewayTsProject({
  parent: myNxMonorepo,
  defaultReleaseBranch: "mainline",
  name: "my-api",
  outdir: "packages/api",
  clientLanguages: [ClientLanguage.TYPESCRIPT, ClientLanguage.PYTHON, ClientLanguage.JAVA],
  documentationFormats: [DocumentationFormat.HTML2, DocumentationFormat.PLANTUML, DocumentationFormat.MARKDOWN],
});
```

In the output directory (`outdir`), you'll find a few files to get you started.

```
|_ src/
    |_ spec/
        |_ spec.yaml - The OpenAPI specification - edit this to define your API
        |_ .parsed-spec.json - A json spec generated from your spec.yaml.
    |_ api/
        |_ api.ts - A CDK construct which defines the API Gateway resources to deploy your API.
        |           This wraps the OpenApiGatewayLambdaApi construct and provides typed interfaces for integrations specific
        |           to your API. You shouldn't need to modify this, instead just extend it as in sample-api.ts.
        |_ sample-api.ts - Example usage of the construct defined in api.ts.
        |_ sample-api.say-hello.ts - An example lambda handler for the operation defined in spec.yaml, making use of the
                                     generated lambda handler wrappers for marshalling and type safety.
|_ generated/
    |_ typescript/ - A generated typescript API client, including generated lambda handler wrappers
    |_ python/ - A generated python API client.
    |_ java/ - A generated java API client.
    |_ documentation/
        |_ html2/ - Generated html documentation
        |_ markdown/ - Generated markdown documentation
        |_ plantuml/ - Generated plant uml documentation
```

If you would prefer to not generate the sample code, you can pass `sampleCode: false` to `OpenApiGatewayTsProject`.

To make changes to your api, simply update `spec.yaml` and run `npx projen` to synthesize all the typesafe client/server code!

The `SampleApi` construct uses `NodejsFunction` to declare the example lambda, but you are free to change this!

#### Python

As well as typescript, you can choose to generate the cdk construct and sample handler in python.

```python
new OpenApiGatewayPythonProject({
  parent: myNxMonorepo,
  outdir: 'packages/myapi',
  name: 'myapi',
  moduleName: 'myapi',
  version: '1.0.0',
  authorName: 'jack',
  authorEmail: 'me@example.com',
  clientLanguages: [ClientLanguage.TYPESCRIPT, ClientLanguage.PYTHON, ClientLanguage.JAVA],
});
```

You will need to set up a shared virtual environment and configure dependencies via the monorepo (see README.md for the nx-monorepo package). An example of a full `.projenrc.ts` might be:

```python
import { nx_monorepo } from "aws-prototyping-sdk";
import { ClientLanguage, OpenApiGatewayPythonProject } from "@aws-prototyping-sdk/open-api-gateway";
import { AwsCdkPythonApp } from "projen/lib/awscdk";

const monorepo = new nx_monorepo.NxMonorepoProject({
  defaultReleaseBranch: "main",
  devDeps: ["aws-prototyping-sdk", "@aws-prototyping-sdk/open-api-gateway"],
  name: "open-api-test",
});

const api = new OpenApiGatewayPythonProject({
  parent: monorepo,
  outdir: 'packages/myapi',
  name: 'myapi',
  moduleName: 'myapi',
  version: '1.0.0',
  authorName: 'jack',
  authorEmail: 'me@example.com',
  clientLanguages: [ClientLanguage.TYPESCRIPT],
  venvOptions: {
    // Use a shared virtual env dir.
    // The generated python client will also use this virtual env dir
    envdir: '../../.env',
  },
});

// Install into virtual env so it's available for the cdk app
api.tasks.tryFind('install')!.exec('pip install --editable .');

const app = new AwsCdkPythonApp({
  authorName: "jack",
  authorEmail: "me@example.com",
  cdkVersion: "2.1.0",
  moduleName: "myapp",
  name: "myapp",
  version: "1.0.0",
  parent: monorepo,
  outdir: "packages/myapp",
  deps: [api.moduleName],
  venvOptions: {
    envdir: '../../.env',
  },
});

monorepo.addImplicitDependency(app, api);

monorepo.synth();
```

You'll find the following directory structure in `packages/myapi`:

```
|_ myapi/
    |_ spec/
        |_ spec.yaml - The OpenAPI specification - edit this to define your API
        |_ .parsed-spec.json - A json spec generated from your spec.yaml.
    |_ api/
        |_ api.py - A CDK construct which defines the API Gateway resources to deploy your API.
        |           This wraps the OpenApiGatewayLambdaApi construct and provides typed interfaces for integrations specific
        |           to your API. You shouldn't need to modify this, instead just extend it as in sample_api.py.
        |_ sample_api.py - Example usage of the construct defined in api.py.
        |_ handlers/
             |_ say_hello_handler_sample.py - An example lambda handler for the operation defined in spec.yaml, making use of the
                                              generated lambda handler wrappers for marshalling and type safety.
|_ generated/
    |_ typescript/ - A generated typescript API client.
    |_ python/ - A generated python API client, including generated lambda handler wrappers.
    |_ java/ - A generated java API client.
```

For simplicity, the generated code deploys a lambda layer for the generated code and its dependencies. You may choose to define an entirely separate projen `PythonProject` for your lambda handlers should you wish to add more dependencies than just the generated code.

### OpenAPI Specification

Your `spec.yaml` file defines your api using [OpenAPI Version 3.0.3](https://swagger.io/specification/). An example spec might look like:

```yaml
openapi: 3.0.3
info:
  version: 1.0.0
  title: Example API
paths:
  /hello:
    get:
      operationId: sayHello
      parameters:
        - in: query
          name: name
          schema:
            type: string
          required: true
      responses:
        '200':
          description: Successful response
          content:
            'application/json':
              schema:
                $ref: '#/components/schemas/HelloResponse'
components:
  schemas:
    HelloResponse:
      type: object
      properties:
        message:
          type: string
      required:
        - message
```

You can divide your specification into multiple files using `$ref`.

For example, you might choose to structure your spec as follows:

```
|_ spec/
    |_ spec.yaml
    |_ paths/
        |_ index.yaml
        |_ sayHello.yaml
    |_ schemas/
        |_ index.yaml
        |_ helloResponse.yaml
```

Where `spec.yaml` looks as follows:

```yaml
openapi: 3.0.3
info:
  version: 1.0.0
  title: Example API
paths:
  $ref: './paths/index.yaml'
components:
  schemas:
    $ref: './schemas/index.yaml'
```

`paths/index.yaml`:

```yaml
/hello:
  get:
    $ref: './sayHello.yaml'
```

`paths/sayHello.yaml`:

```yaml
operationId: sayHello
parameters:
 - in: query
   name: name
   schema:
     type: string
   required: true
responses:
  '200':
    description: Successful response
    content:
      'application/json':
        schema:
          $ref: '../schemas/helloResponse.yaml'
```

`schemas/index.yaml`:

```yaml
HelloResponse:
  $ref: './helloResponse.yaml'
```

`schemas/helloResponse.yaml`:

```yaml
type: object
properties:
  message:
    type: string
required:
  - message
```

### Construct

A sample construct is generated which provides a type-safe interface for creating an API Gateway API based on your OpenAPI specification. You'll get a type error if you forget to define an integration for an operation defined in your api.

```python
import * as path from 'path';
import { Authorizers } from '@aws-prototyping-sdk/open-api-gateway';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import { Construct } from 'constructs';
import { Api } from './api';

/**
 * An example of how to wire lambda handler functions to the API
 */
export class SampleApi extends Api {
  constructor(scope: Construct, id: string) {
    super(scope, id, {
      defaultAuthorizer: Authorizers.iam(),
      integrations: {
        // Every operation defined in your API must have an integration defined!
        sayHello: {
          function: new NodejsFunction(scope, 'say-hello'),
        },
      },
    });
  }
}
```

#### Authorizers

The `Api` construct allows you to define one or more authorizers for securing your API. An integration will use the `defaultAuthorizer` unless an `authorizer` is specified at the integration level. The following authorizers are supported:

* `Authorizers.none` - No auth
* `Authorizers.iam` - AWS IAM (Signature Version 4)
* `Authorizers.cognito` - Cognito user pool
* `Authorizers.custom` - A custom authorizer

##### Cognito Authorizer

To use the Cognito authorizer, one or more user pools must be provided. You can optionally specify the scopes to check if using an access token. You can use the `withScopes` method to use the same authorizer but verify different scopes for individual integrations, for example:

```python
export class SampleApi extends Api {
  constructor(scope: Construct, id: string) {
    const cognitoAuthorizer = Authorizers.cognito({
      authorizerId: 'myCognitoAuthorizer',
      userPools: [new UserPool(scope, 'UserPool')],
    });

    super(scope, id, {
      defaultAuthorizer: cognitoAuthorizer,
      integrations: {
        // Everyone in the user pool can call this operation:
        sayHello: {
          function: new NodejsFunction(scope, 'say-hello'),
        },
        // Only users with the given scopes can call this operation
        myRestrictedOperation: {
          function: new NodejsFunction(scope, 'my-restricted-operation'),
          authorizer: cognitoAuthorizer.withScopes('my-resource-server/my-scope'),
        },
      },
    });
  }
}
```

For more information about scopes or identity and access tokens, please see the [API Gateway documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html).

##### Custom Authorizer

Custom authorizers use lambda functions to handle authorizing requests. These can either be simple token-based authorizers, or more complex request-based authorizers. See the [API Gateway documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html) for more details.

An example token-based authorizer (default):

```python
Authorizers.custom({
  authorizerId: 'myTokenAuthorizer',
  function: new NodejsFunction(scope, 'authorizer'),
});
```

An example request-based handler. By default the identitySource will be `method.request.header.Authorization`, however you can customise this as per [the API Gateway documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-identitysource).

```python
Authorizers.custom({
  authorizerId: 'myRequestAuthorizer',
  type: CustomAuthorizerType.REQUEST,
  identitySource: 'method.request.header.MyCustomHeader, method.request.querystring.myQueryString',
  function: new NodejsFunction(scope, 'authorizer'),
});
```

### Generated Client

#### Typescript

The [typescript-fetch](https://openapi-generator.tech/docs/generators/typescript-fetch/) OpenAPI generator is used to generate OpenAPI clients for typescript. This requires an implementation of `fetch` to be passed to the client. In the browser one can pass the built in fetch, or in NodeJS you can use an implementation such as [node-fetch](https://www.npmjs.com/package/node-fetch).

Example usage of the client in a website:

```python
import { Configuration, DefaultApi } from "my-api-typescript-client";

const client = new DefaultApi(new Configuration({
  basePath: "https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com",
  fetchApi: window.fetch.bind(window),
}));

await client.sayHello({ name: "Jack" });
```

#### Python

The [python-experimental](https://openapi-generator.tech/docs/generators/python-experimental) OpenAPI generator is used to generate OpenAPI clients for python.

Example usage:

```python
from my_api_python import ApiClient, Configuration
from my_api_python.api.default_api import DefaultApi

configuration = Configuration(
    host = "https://xxxxxxxxxx.execute-api.ap-southeast-2.amazonaws.com"
)

with ApiClient(configuration) as api_client:
    client = DefaultApi(api_client)

    client.say_hello(
        query_params={
            'name': "name_example",
        },
    )
```

You'll find details about how to use the python client in the README.md alongside your generated client.

### Lambda Handler Wrappers

Lambda handler wrappers are also importable from the generated client. These provide input/output type safety, as well as allowing you to define a custom type for API error responses.

#### Typescript

```python
import { sayHelloHandler, ApiError } from "my-api-typescript-client";

export const handler = sayHelloHandler<ApiError>(async (input) => {
  return {
    statusCode: 200,
    body: {
      message: `Hello ${input.requestParameters.name}!`,
    },
  };
});
```

#### Python

```python
from myapi_python.api.default_api_operation_config import say_hello_handler, SayHelloRequest, ApiResponse
from myapi_python.model.api_error import ApiError
from myapi_python.model.hello_response import HelloResponse

@say_hello_handler
def handler(input: SayHelloRequest, **kwargs) -> ApiResponse[HelloResponse, ApiError]:
    return ApiResponse(
        status_code=200,
        body=HelloResponse(message="Hello {}!".format(input.request_parameters["name"])),
        headers={}
    )
```

### Interceptors

The lambda handler wrappers allow you to pass in a *chain* of handler functions to handle the request. This allows you to implement middleware / interceptors for handling requests. Each handler function may choose whether or not to continue the handler chain by invoking `chain.next(input, event, context)`. Note that the last handler in the chain (ie the actual request handler which transforms the input to the output) should not call `chain.next`.

#### Typescript

In typescript, interceptors are passed as separate arguments to the generated handler wrapper, in the order in which they should be executed.

```python
import {
  sayHelloHandler,
  ApiError,
  LambdaRequestParameters,
  LambdaHandlerChain,
  OperationResponse
} from "my-api-typescript-client";

// Interceptor to wrap invocations in a try/catch, returning a 500 error for any unhandled exceptions.
const tryCatchInterceptor = async <
  RequestParameters,
  RequestArrayParameters,
  RequestBody,
  RequestOutput,
  TError
>(
  input: LambdaRequestParameters<RequestParameters, RequestArrayParameters, RequestBody>,
  event: any,
  context: any,
  chain: LambdaHandlerChain<RequestParameters, RequestArrayParameters, RequestBody, RequestOutput, TError>,
): Promise<OperationResponse<RequestOutput, TError>> => {
  try {
    return await chain.next(input, event, context);
  } catch (e) {
    return { statusCode: 500, body: { errorMessage: e.message }};
  }
};

// tryCatchInterceptor is passed first, so it runs first and calls the second argument function (the request handler) via chain.next
export const handler = sayHelloHandler<ApiError>(tryCatchInterceptor, async (input) => {
  return {
    statusCode: 200,
    body: {
      message: `Hello ${input.requestParameters.name}!`,
    },
  };
});
```

Another example interceptor might be to record request time metrics. The example below includes the full generic type signature for an interceptor:

```python
import {
  LambdaRequestParameters,
  LambdaHandlerChain,
  OperationResponse,
} from 'my-api-typescript-client';

const timingInterceptor = async <
  RequestParameters,
  RequestArrayParameters,
  RequestBody,
  RequestOutput,
  TError
>(
  input: LambdaRequestParameters<RequestParameters, RequestArrayParameters, RequestBody>,
  event: any,
  context: any,
  chain: LambdaHandlerChain<RequestParameters, RequestArrayParameters, RequestBody, RequestOutput, TError>,
): Promise<OperationResponse<RequestOutput, TError>> => {
  const start = Date.now();
  const response = await chain.next(input, event, context);
  const end = Date.now();
  console.log(`Took ${end - start}ms`);
  return response;
};
```

### Other Details

#### Workspaces and `OpenApiGatewayTsProject`

`OpenApiGatewayTsProject` can be used as part of a monorepo using YARN/NPM/PNPM workspaces. When used in a monorepo, a dependency is established between `OpenApiGatewayTsProject` and the generated typescript client, which is expected to be managed by the parent monorepo (ie both `OpenApiGatewayTsProject` and the generated typescript client are parented by the monorepo).

During initial project synthesis, the dependency between `OpenApiGatewayTsProject` and the generated client is established via workspace configuration local to `OpenApiGatewayTsProject`, since the parent monorepo will not have updated to include the new packages in time for the initial "install".

When the package manager is PNPM, this initial workspace is configured by creating a local `pnpm-workspace.yaml` file, and thus if you specify your own for an instance of `OpenApiGatewayTsProject`, synthesis will fail. It is most likely that you will not need to define this file locally in `OpenApiGatewayTsProject` since the monorepo copy should be used to manage all packages within the repo, however if managing this file at the `OpenApiGatewayTsProject` level is required, please use the `pnpmWorkspace` property of `OpenApiGatewayTsProject`.

#### Customising Generated Client Projects

By default, the generated clients are configured automatically, including project names. You can customise the generated client code using the `<language>ProjectOptions` properties when constructing your projen project.

##### Python Shared Virtual Environment

For adding dependencies between python projects within a monorepo you can use a single shared virtual environment, and install your python projects into that environment with `pip install --editable .` in the dependee. The generated python client will automatically do this if it detects it is within a monorepo.

The following example shows how to configure the generated client to use a shared virtual environment:

```python
const api = new OpenApiGatewayTsProject({
  parent: monorepo,
  name: 'api',
  outdir: 'packages/api',
  defaultReleaseBranch: 'main',
  clientLanguages: [ClientLanguage.PYTHON],
  pythonClientOptions: {
    moduleName: 'my_api_python',
    name: 'my_api_python',
    authorName: 'jack',
    authorEmail: 'me@example.com',
    version: '1.0.0',
    venvOptions: {
      // Directory relative to the generated python client (in this case packages/api/generated/python)
      envdir: '../../../../.env',
    },
  },
});

new PythonProject({
  parent: monorepo,
  outdir: 'packages/my-python-lib',
  moduleName: 'my_python_lib',
  name: 'my_python_lib',
  authorName: 'jack',
  authorEmail: 'me@example.com',
  version: '1.0.0',
  venvOptions: {
    // Directory relative to the python lib (in this case packages/my-python-lib)
    envdir: '../../.env',
  },
  // Generated client can be safely cast to a PythonProject
  deps: [(api.generatedClients[ClientLanguage.PYTHON] as PythonProject).moduleName],
});
```
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
import aws_cdk.aws_cognito
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import constructs
import projen
import projen.github
import projen.github.workflows
import projen.java
import projen.javascript
import projen.python
import projen.release
import projen.typescript


class Authorizer(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-prototyping-sdk/open-api-gateway.Authorizer",
):
    '''(experimental) An authorizer for authorizing API requests.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        authorization_type: aws_cdk.aws_apigateway.AuthorizationType,
        authorizer_id: builtins.str,
    ) -> None:
        '''
        :param authorization_type: (experimental) The type of the authorizer.
        :param authorizer_id: (experimental) The unique identifier for the authorizer.

        :stability: experimental
        '''
        props = AuthorizerProps(
            authorization_type=authorization_type, authorizer_id=authorizer_id
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizationType")
    def authorization_type(self) -> aws_cdk.aws_apigateway.AuthorizationType:
        '''(experimental) The type of the authorizer.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigateway.AuthorizationType, jsii.get(self, "authorizationType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerId")
    def authorizer_id(self) -> builtins.str:
        '''(experimental) The unique identifier for the authorizer.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "authorizerId"))


class _AuthorizerProxy(Authorizer):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Authorizer).__jsii_proxy_class__ = lambda : _AuthorizerProxy


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/open-api-gateway.AuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorization_type": "authorizationType",
        "authorizer_id": "authorizerId",
    },
)
class AuthorizerProps:
    def __init__(
        self,
        *,
        authorization_type: aws_cdk.aws_apigateway.AuthorizationType,
        authorizer_id: builtins.str,
    ) -> None:
        '''(experimental) Properties for an authorizer.

        :param authorization_type: (experimental) The type of the authorizer.
        :param authorizer_id: (experimental) The unique identifier for the authorizer.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authorization_type": authorization_type,
            "authorizer_id": authorizer_id,
        }

    @builtins.property
    def authorization_type(self) -> aws_cdk.aws_apigateway.AuthorizationType:
        '''(experimental) The type of the authorizer.

        :stability: experimental
        '''
        result = self._values.get("authorization_type")
        assert result is not None, "Required property 'authorization_type' is missing"
        return typing.cast(aws_cdk.aws_apigateway.AuthorizationType, result)

    @builtins.property
    def authorizer_id(self) -> builtins.str:
        '''(experimental) The unique identifier for the authorizer.

        :stability: experimental
        '''
        result = self._values.get("authorizer_id")
        assert result is not None, "Required property 'authorizer_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Authorizers(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/open-api-gateway.Authorizers",
):
    '''(experimental) Class used to construct authorizers for use in the OpenApiGatewayLambdaApi construct.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="cognito") # type: ignore[misc]
    @builtins.classmethod
    def cognito(
        cls,
        *,
        authorizer_id: builtins.str,
        user_pools: typing.Sequence[aws_cdk.aws_cognito.IUserPool],
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "CognitoAuthorizer":
        '''(experimental) A Cognito User Pools authorizer.

        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param user_pools: (experimental) The Cognito user pools associated with this authorizer.
        :param authorization_scopes: (experimental) A list of authorization scopes configured on the method. When used as the default authorizer, these scopes will be applied to all methods without an authorizer at the integration level. Default: []

        :stability: experimental
        '''
        props = CognitoAuthorizerProps(
            authorizer_id=authorizer_id,
            user_pools=user_pools,
            authorization_scopes=authorization_scopes,
        )

        return typing.cast("CognitoAuthorizer", jsii.sinvoke(cls, "cognito", [props]))

    @jsii.member(jsii_name="custom") # type: ignore[misc]
    @builtins.classmethod
    def custom(
        cls,
        *,
        authorizer_id: builtins.str,
        function: aws_cdk.aws_lambda.IFunction,
        authorizer_result_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        identity_source: typing.Optional[builtins.str] = None,
        type: typing.Optional["CustomAuthorizerType"] = None,
    ) -> "CustomAuthorizer":
        '''(experimental) A custom authorizer.

        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param function: (experimental) The lambda function used to authorize requests.
        :param authorizer_result_ttl_in_seconds: (experimental) The number of seconds during which the authorizer result is cached. Default: 300
        :param identity_source: (experimental) The source of the identity in an incoming request. Default: "method.request.header.Authorization"
        :param type: (experimental) The type of custom authorizer. Default: CustomAuthorizerType.TOKEN

        :stability: experimental
        '''
        props = CustomAuthorizerProps(
            authorizer_id=authorizer_id,
            function=function,
            authorizer_result_ttl_in_seconds=authorizer_result_ttl_in_seconds,
            identity_source=identity_source,
            type=type,
        )

        return typing.cast("CustomAuthorizer", jsii.sinvoke(cls, "custom", [props]))

    @jsii.member(jsii_name="iam") # type: ignore[misc]
    @builtins.classmethod
    def iam(cls) -> "IamAuthorizer":
        '''(experimental) An IAM authorizer which uses AWS signature version 4 to authorize requests.

        :stability: experimental
        '''
        return typing.cast("IamAuthorizer", jsii.sinvoke(cls, "iam", []))

    @jsii.member(jsii_name="none") # type: ignore[misc]
    @builtins.classmethod
    def none(cls) -> "NoneAuthorizer":
        '''(experimental) No authorizer.

        :stability: experimental
        '''
        return typing.cast("NoneAuthorizer", jsii.sinvoke(cls, "none", []))


@jsii.enum(jsii_type="@aws-prototyping-sdk/open-api-gateway.ClientLanguage")
class ClientLanguage(enum.Enum):
    '''(experimental) Supported languages for client generation.

    :stability: experimental
    '''

    TYPESCRIPT = "TYPESCRIPT"
    '''
    :stability: experimental
    '''
    PYTHON = "PYTHON"
    '''
    :stability: experimental
    '''
    JAVA = "JAVA"
    '''
    :stability: experimental
    '''


class CognitoAuthorizer(
    Authorizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/open-api-gateway.CognitoAuthorizer",
):
    '''(experimental) An authorizer that uses Cognito identity or access tokens.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        authorizer_id: builtins.str,
        user_pools: typing.Sequence[aws_cdk.aws_cognito.IUserPool],
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param user_pools: (experimental) The Cognito user pools associated with this authorizer.
        :param authorization_scopes: (experimental) A list of authorization scopes configured on the method. When used as the default authorizer, these scopes will be applied to all methods without an authorizer at the integration level. Default: []

        :stability: experimental
        '''
        props = CognitoAuthorizerProps(
            authorizer_id=authorizer_id,
            user_pools=user_pools,
            authorization_scopes=authorization_scopes,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="withScopes")
    def with_scopes(self, *authorization_scopes: builtins.str) -> "CognitoAuthorizer":
        '''(experimental) Returns this authorizer with scopes applied, intended for usage in individual operations where scopes may differ on a per-operation basis.

        :param authorization_scopes: the scopes to apply.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-authorizationscopes
        :stability: experimental
        '''
        return typing.cast("CognitoAuthorizer", jsii.invoke(self, "withScopes", [*authorization_scopes]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizationScopes")
    def authorization_scopes(self) -> typing.List[builtins.str]:
        '''(experimental) A list of authorization scopes configured on the method.

        When used as the default authorizer, these scopes will be
        applied to all methods without an authorizer at the integration level.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-authorizationscopes
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "authorizationScopes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPools")
    def user_pools(self) -> typing.List[aws_cdk.aws_cognito.IUserPool]:
        '''(experimental) The Cognito user pools associated with this authorizer.

        :stability: experimental
        '''
        return typing.cast(typing.List[aws_cdk.aws_cognito.IUserPool], jsii.get(self, "userPools"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/open-api-gateway.CognitoAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_id": "authorizerId",
        "user_pools": "userPools",
        "authorization_scopes": "authorizationScopes",
    },
)
class CognitoAuthorizerProps:
    def __init__(
        self,
        *,
        authorizer_id: builtins.str,
        user_pools: typing.Sequence[aws_cdk.aws_cognito.IUserPool],
        authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties used to configure a cognito authorizer.

        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param user_pools: (experimental) The Cognito user pools associated with this authorizer.
        :param authorization_scopes: (experimental) A list of authorization scopes configured on the method. When used as the default authorizer, these scopes will be applied to all methods without an authorizer at the integration level. Default: []

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authorizer_id": authorizer_id,
            "user_pools": user_pools,
        }
        if authorization_scopes is not None:
            self._values["authorization_scopes"] = authorization_scopes

    @builtins.property
    def authorizer_id(self) -> builtins.str:
        '''(experimental) Unique identifier for this authorizer.

        :stability: experimental
        '''
        result = self._values.get("authorizer_id")
        assert result is not None, "Required property 'authorizer_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pools(self) -> typing.List[aws_cdk.aws_cognito.IUserPool]:
        '''(experimental) The Cognito user pools associated with this authorizer.

        :stability: experimental
        '''
        result = self._values.get("user_pools")
        assert result is not None, "Required property 'user_pools' is missing"
        return typing.cast(typing.List[aws_cdk.aws_cognito.IUserPool], result)

    @builtins.property
    def authorization_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of authorization scopes configured on the method.

        When used as the default authorizer, these scopes will be
        applied to all methods without an authorizer at the integration level.

        :default: []

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html#cfn-apigateway-method-authorizationscopes
        :stability: experimental
        '''
        result = self._values.get("authorization_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CognitoAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CustomAuthorizer(
    Authorizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/open-api-gateway.CustomAuthorizer",
):
    '''(experimental) An authorizer that uses a lambda function to authorize requests.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        authorizer_id: builtins.str,
        function: aws_cdk.aws_lambda.IFunction,
        authorizer_result_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        identity_source: typing.Optional[builtins.str] = None,
        type: typing.Optional["CustomAuthorizerType"] = None,
    ) -> None:
        '''
        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param function: (experimental) The lambda function used to authorize requests.
        :param authorizer_result_ttl_in_seconds: (experimental) The number of seconds during which the authorizer result is cached. Default: 300
        :param identity_source: (experimental) The source of the identity in an incoming request. Default: "method.request.header.Authorization"
        :param type: (experimental) The type of custom authorizer. Default: CustomAuthorizerType.TOKEN

        :stability: experimental
        '''
        props = CustomAuthorizerProps(
            authorizer_id=authorizer_id,
            function=function,
            authorizer_result_ttl_in_seconds=authorizer_result_ttl_in_seconds,
            identity_source=identity_source,
            type=type,
        )

        jsii.create(self.__class__, self, [props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerResultTtlInSeconds")
    def authorizer_result_ttl_in_seconds(self) -> jsii.Number:
        '''(experimental) The number of seconds during which the authorizer result is cached.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "authorizerResultTtlInSeconds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="function")
    def function(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) The lambda function used to authorize requests.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "function"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identitySource")
    def identity_source(self) -> builtins.str:
        '''(experimental) The source of the identity in an incoming request.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-identitysource
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "identitySource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> "CustomAuthorizerType":
        '''(experimental) The type of custom authorizer.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-type
        :stability: experimental
        '''
        return typing.cast("CustomAuthorizerType", jsii.get(self, "type"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/open-api-gateway.CustomAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_id": "authorizerId",
        "function": "function",
        "authorizer_result_ttl_in_seconds": "authorizerResultTtlInSeconds",
        "identity_source": "identitySource",
        "type": "type",
    },
)
class CustomAuthorizerProps:
    def __init__(
        self,
        *,
        authorizer_id: builtins.str,
        function: aws_cdk.aws_lambda.IFunction,
        authorizer_result_ttl_in_seconds: typing.Optional[jsii.Number] = None,
        identity_source: typing.Optional[builtins.str] = None,
        type: typing.Optional["CustomAuthorizerType"] = None,
    ) -> None:
        '''(experimental) Properties used to configure a custom authorizer.

        :param authorizer_id: (experimental) Unique identifier for this authorizer.
        :param function: (experimental) The lambda function used to authorize requests.
        :param authorizer_result_ttl_in_seconds: (experimental) The number of seconds during which the authorizer result is cached. Default: 300
        :param identity_source: (experimental) The source of the identity in an incoming request. Default: "method.request.header.Authorization"
        :param type: (experimental) The type of custom authorizer. Default: CustomAuthorizerType.TOKEN

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authorizer_id": authorizer_id,
            "function": function,
        }
        if authorizer_result_ttl_in_seconds is not None:
            self._values["authorizer_result_ttl_in_seconds"] = authorizer_result_ttl_in_seconds
        if identity_source is not None:
            self._values["identity_source"] = identity_source
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def authorizer_id(self) -> builtins.str:
        '''(experimental) Unique identifier for this authorizer.

        :stability: experimental
        '''
        result = self._values.get("authorizer_id")
        assert result is not None, "Required property 'authorizer_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) The lambda function used to authorize requests.

        :stability: experimental
        '''
        result = self._values.get("function")
        assert result is not None, "Required property 'function' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    @builtins.property
    def authorizer_result_ttl_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of seconds during which the authorizer result is cached.

        :default: 300

        :stability: experimental
        '''
        result = self._values.get("authorizer_result_ttl_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def identity_source(self) -> typing.Optional[builtins.str]:
        '''(experimental) The source of the identity in an incoming request.

        :default: "method.request.header.Authorization"

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-identitysource
        :stability: experimental
        '''
        result = self._values.get("identity_source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional["CustomAuthorizerType"]:
        '''(experimental) The type of custom authorizer.

        :default: CustomAuthorizerType.TOKEN

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-type
        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["CustomAuthorizerType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-prototyping-sdk/open-api-gateway.CustomAuthorizerType")
class CustomAuthorizerType(enum.Enum):
    '''(experimental) The type of custom authorizer.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-authorizer.html#cfn-apigateway-authorizer-type
    :stability: experimental
    '''

    TOKEN = "TOKEN"
    '''(experimental) A custom authorizer that uses a Lambda function.

    :stability: experimental
    '''
    REQUEST = "REQUEST"
    '''(experimental) An authorizer that uses a Lambda function using incoming request parameters.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-prototyping-sdk/open-api-gateway.DocumentationFormat")
class DocumentationFormat(enum.Enum):
    '''(experimental) Formats for documentation generation.

    :stability: experimental
    '''

    HTML2 = "HTML2"
    '''
    :stability: experimental
    '''
    MARKDOWN = "MARKDOWN"
    '''
    :stability: experimental
    '''
    PLANTUML = "PLANTUML"
    '''
    :stability: experimental
    '''


class IamAuthorizer(
    Authorizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/open-api-gateway.IamAuthorizer",
):
    '''(experimental) An IAM authorizer.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/open-api-gateway.MethodAndPath",
    jsii_struct_bases=[],
    name_mapping={"method": "method", "path": "path"},
)
class MethodAndPath:
    def __init__(self, *, method: builtins.str, path: builtins.str) -> None:
        '''(experimental) Structure to contain an API operation's method and path.

        :param method: (experimental) The http method of this operation.
        :param path: (experimental) The path of this operation in the api.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "method": method,
            "path": path,
        }

    @builtins.property
    def method(self) -> builtins.str:
        '''(experimental) The http method of this operation.

        :stability: experimental
        '''
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) The path of this operation in the api.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MethodAndPath(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NoneAuthorizer(
    Authorizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/open-api-gateway.NoneAuthorizer",
):
    '''(experimental) No authorizer.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])


class OpenApiGatewayLambdaApi(
    aws_cdk.aws_apigateway.SpecRestApi,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/open-api-gateway.OpenApiGatewayLambdaApi",
):
    '''(experimental) A construct for creating an api gateway api based on the definition in the OpenAPI spec.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        spec: typing.Any,
        cloud_watch_role: typing.Optional[builtins.bool] = None,
        deploy: typing.Optional[builtins.bool] = None,
        deploy_options: typing.Optional[aws_cdk.aws_apigateway.StageOptions] = None,
        disable_execute_api_endpoint: typing.Optional[builtins.bool] = None,
        domain_name: typing.Optional[aws_cdk.aws_apigateway.DomainNameOptions] = None,
        endpoint_export_name: typing.Optional[builtins.str] = None,
        endpoint_types: typing.Optional[typing.Sequence[aws_cdk.aws_apigateway.EndpointType]] = None,
        fail_on_warnings: typing.Optional[builtins.bool] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        policy: typing.Optional[aws_cdk.aws_iam.PolicyDocument] = None,
        rest_api_name: typing.Optional[builtins.str] = None,
        retain_deployments: typing.Optional[builtins.bool] = None,
        integrations: typing.Mapping[builtins.str, "OpenApiIntegration"],
        operation_lookup: typing.Mapping[builtins.str, MethodAndPath],
        cors_options: typing.Optional[aws_cdk.aws_apigateway.CorsOptions] = None,
        default_authorizer: typing.Optional[Authorizer] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param spec: (experimental) The parsed OpenAPI specification.
        :param cloud_watch_role: Automatically configure an AWS CloudWatch role for API Gateway. Default: true
        :param deploy: Indicates if a Deployment should be automatically created for this API, and recreated when the API model (resources, methods) changes. Since API Gateway deployments are immutable, When this option is enabled (by default), an AWS::ApiGateway::Deployment resource will automatically created with a logical ID that hashes the API model (methods, resources and options). This means that when the model changes, the logical ID of this CloudFormation resource will change, and a new deployment will be created. If this is set, ``latestDeployment`` will refer to the ``Deployment`` object and ``deploymentStage`` will refer to a ``Stage`` that points to this deployment. To customize the stage options, use the ``deployOptions`` property. A CloudFormation Output will also be defined with the root URL endpoint of this REST API. Default: true
        :param deploy_options: Options for the API Gateway stage that will always point to the latest deployment when ``deploy`` is enabled. If ``deploy`` is disabled, this value cannot be set. Default: - Based on defaults of ``StageOptions``.
        :param disable_execute_api_endpoint: Specifies whether clients can invoke the API using the default execute-api endpoint. To require that clients use a custom domain name to invoke the API, disable the default endpoint. Default: false
        :param domain_name: Configure a custom domain name and map it to this API. Default: - no domain name is defined, use ``addDomainName`` or directly define a ``DomainName``.
        :param endpoint_export_name: Export name for the CfnOutput containing the API endpoint. Default: - when no export name is given, output will be created without export
        :param endpoint_types: A list of the endpoint types of the API. Use this property when creating an API. Default: EndpointType.EDGE
        :param fail_on_warnings: Indicates whether to roll back the resource if a warning occurs while API Gateway is creating the RestApi resource. Default: false
        :param parameters: Custom header parameters for the request. Default: - No parameters.
        :param policy: A policy document that contains the permissions for this RestApi. Default: - No policy.
        :param rest_api_name: A name for the API Gateway RestApi resource. Default: - ID of the RestApi construct.
        :param retain_deployments: Retains old deployment resources when the API changes. This allows manually reverting stages to point to old deployments via the AWS Console. Default: false
        :param integrations: (experimental) A mapping of API operation to its integration.
        :param operation_lookup: (experimental) Details about each operation.
        :param cors_options: (experimental) Cross Origin Resource Sharing options for the API.
        :param default_authorizer: (experimental) The default authorizer to use for your api. When omitted, no authorizer is used. Authorizers specified at the integration level will override this for that operation.

        :stability: experimental
        '''
        props = OpenApiGatewayLambdaApiProps(
            spec=spec,
            cloud_watch_role=cloud_watch_role,
            deploy=deploy,
            deploy_options=deploy_options,
            disable_execute_api_endpoint=disable_execute_api_endpoint,
            domain_name=domain_name,
            endpoint_export_name=endpoint_export_name,
            endpoint_types=endpoint_types,
            fail_on_warnings=fail_on_warnings,
            parameters=parameters,
            policy=policy,
            rest_api_name=rest_api_name,
            retain_deployments=retain_deployments,
            integrations=integrations,
            operation_lookup=operation_lookup,
            cors_options=cors_options,
            default_authorizer=default_authorizer,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/open-api-gateway.OpenApiGatewayProjectOptions",
    jsii_struct_bases=[],
    name_mapping={
        "client_languages": "clientLanguages",
        "api_src_dir": "apiSrcDir",
        "documentation_formats": "documentationFormats",
        "generated_code_dir": "generatedCodeDir",
        "java_client_options": "javaClientOptions",
        "parsed_spec_file_name": "parsedSpecFileName",
        "python_client_options": "pythonClientOptions",
        "spec_file": "specFile",
        "typescript_client_options": "typescriptClientOptions",
    },
)
class OpenApiGatewayProjectOptions:
    def __init__(
        self,
        *,
        client_languages: typing.Sequence[ClientLanguage],
        api_src_dir: typing.Optional[builtins.str] = None,
        documentation_formats: typing.Optional[typing.Sequence[DocumentationFormat]] = None,
        generated_code_dir: typing.Optional[builtins.str] = None,
        java_client_options: typing.Optional[projen.java.JavaProjectOptions] = None,
        parsed_spec_file_name: typing.Optional[builtins.str] = None,
        python_client_options: typing.Optional[projen.python.PythonProjectOptions] = None,
        spec_file: typing.Optional[builtins.str] = None,
        typescript_client_options: typing.Optional[projen.typescript.TypeScriptProjectOptions] = None,
    ) -> None:
        '''(experimental) Options common to all open api gateway projects.

        :param client_languages: (experimental) The list of languages for which clients will be generated. A typescript client will always be generated.
        :param api_src_dir: (experimental) The directory in which the api generated code will reside, relative to the project srcdir.
        :param documentation_formats: (experimental) Formats to generate documentation in.
        :param generated_code_dir: (experimental) The directory in which generated client code will be generated, relative to the outdir of this project. Default: "generated"
        :param java_client_options: (experimental) Options for the generated java client (if specified in clientLanguages). These override the default inferred options.
        :param parsed_spec_file_name: (experimental) The name of the output parsed OpenAPI specification file. Must end with .json. Default: ".parsed-spec.json"
        :param python_client_options: (experimental) Options for the generated python client (if specified in clientLanguages). These override the default inferred options.
        :param spec_file: (experimental) The path to the OpenAPI specification file, relative to the project source directory (srcdir). Default: "spec/spec.yaml"
        :param typescript_client_options: (experimental) Options for the generated typescript client. These override the default inferred options.

        :stability: experimental
        '''
        if isinstance(java_client_options, dict):
            java_client_options = projen.java.JavaProjectOptions(**java_client_options)
        if isinstance(python_client_options, dict):
            python_client_options = projen.python.PythonProjectOptions(**python_client_options)
        if isinstance(typescript_client_options, dict):
            typescript_client_options = projen.typescript.TypeScriptProjectOptions(**typescript_client_options)
        self._values: typing.Dict[str, typing.Any] = {
            "client_languages": client_languages,
        }
        if api_src_dir is not None:
            self._values["api_src_dir"] = api_src_dir
        if documentation_formats is not None:
            self._values["documentation_formats"] = documentation_formats
        if generated_code_dir is not None:
            self._values["generated_code_dir"] = generated_code_dir
        if java_client_options is not None:
            self._values["java_client_options"] = java_client_options
        if parsed_spec_file_name is not None:
            self._values["parsed_spec_file_name"] = parsed_spec_file_name
        if python_client_options is not None:
            self._values["python_client_options"] = python_client_options
        if spec_file is not None:
            self._values["spec_file"] = spec_file
        if typescript_client_options is not None:
            self._values["typescript_client_options"] = typescript_client_options

    @builtins.property
    def client_languages(self) -> typing.List[ClientLanguage]:
        '''(experimental) The list of languages for which clients will be generated.

        A typescript client will always be generated.

        :stability: experimental
        '''
        result = self._values.get("client_languages")
        assert result is not None, "Required property 'client_languages' is missing"
        return typing.cast(typing.List[ClientLanguage], result)

    @builtins.property
    def api_src_dir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The directory in which the api generated code will reside, relative to the project srcdir.

        :stability: experimental
        '''
        result = self._values.get("api_src_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def documentation_formats(
        self,
    ) -> typing.Optional[typing.List[DocumentationFormat]]:
        '''(experimental) Formats to generate documentation in.

        :stability: experimental
        '''
        result = self._values.get("documentation_formats")
        return typing.cast(typing.Optional[typing.List[DocumentationFormat]], result)

    @builtins.property
    def generated_code_dir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The directory in which generated client code will be generated, relative to the outdir of this project.

        :default: "generated"

        :stability: experimental
        '''
        result = self._values.get("generated_code_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def java_client_options(self) -> typing.Optional[projen.java.JavaProjectOptions]:
        '''(experimental) Options for the generated java client (if specified in clientLanguages).

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("java_client_options")
        return typing.cast(typing.Optional[projen.java.JavaProjectOptions], result)

    @builtins.property
    def parsed_spec_file_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the output parsed OpenAPI specification file.

        Must end with .json.

        :default: ".parsed-spec.json"

        :stability: experimental
        '''
        result = self._values.get("parsed_spec_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def python_client_options(
        self,
    ) -> typing.Optional[projen.python.PythonProjectOptions]:
        '''(experimental) Options for the generated python client (if specified in clientLanguages).

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("python_client_options")
        return typing.cast(typing.Optional[projen.python.PythonProjectOptions], result)

    @builtins.property
    def spec_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The path to the OpenAPI specification file, relative to the project source directory (srcdir).

        :default: "spec/spec.yaml"

        :stability: experimental
        '''
        result = self._values.get("spec_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def typescript_client_options(
        self,
    ) -> typing.Optional[projen.typescript.TypeScriptProjectOptions]:
        '''(experimental) Options for the generated typescript client.

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("typescript_client_options")
        return typing.cast(typing.Optional[projen.typescript.TypeScriptProjectOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenApiGatewayProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpenApiGatewayPythonProject(
    projen.python.PythonProject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/open-api-gateway.OpenApiGatewayPythonProject",
):
    '''(experimental) Synthesizes a Python Project with an OpenAPI spec, generated clients, a CDK construct for deploying the API with API Gateway, and generated lambda handler wrappers for type-safe handling of requests.

    :stability: experimental
    :pjid: open-api-gateway-py
    '''

    def __init__(
        self,
        *,
        module_name: builtins.str,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pip: typing.Optional[builtins.bool] = None,
        poetry: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[projen.javascript.ProjenrcOptions] = None,
        projenrc_python: typing.Optional[builtins.bool] = None,
        projenrc_python_options: typing.Optional[projen.python.ProjenrcOptions] = None,
        pytest: typing.Optional[builtins.bool] = None,
        pytest_options: typing.Optional[projen.python.PytestOptions] = None,
        sample: typing.Optional[builtins.bool] = None,
        setuptools: typing.Optional[builtins.bool] = None,
        venv: typing.Optional[builtins.bool] = None,
        venv_options: typing.Optional[projen.python.VenvOptions] = None,
        client_languages: typing.Sequence[ClientLanguage],
        api_src_dir: typing.Optional[builtins.str] = None,
        documentation_formats: typing.Optional[typing.Sequence[DocumentationFormat]] = None,
        generated_code_dir: typing.Optional[builtins.str] = None,
        java_client_options: typing.Optional[projen.java.JavaProjectOptions] = None,
        parsed_spec_file_name: typing.Optional[builtins.str] = None,
        python_client_options: typing.Optional[projen.python.PythonProjectOptions] = None,
        spec_file: typing.Optional[builtins.str] = None,
        typescript_client_options: typing.Optional[projen.typescript.TypeScriptProjectOptions] = None,
        auto_approve_options: typing.Optional[projen.github.AutoApproveOptions] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[projen.github.AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[projen.github.GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        projen_credentials: typing.Optional[projen.github.GithubCredentials] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[projen.github.StaleOptions] = None,
        vscode: typing.Optional[builtins.bool] = None,
        author_email: builtins.str,
        author_name: builtins.str,
        version: builtins.str,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        poetry_options: typing.Optional[projen.python.PoetryPyprojectOptionsWithoutDeps] = None,
        setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        name: builtins.str,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[projen.ProjenrcOptions] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[projen.RenovatebotOptions] = None,
    ) -> None:
        '''
        :param module_name: (experimental) Name of the python package as used in imports and filenames. Must only consist of alphanumeric characters and underscores. Default: $PYTHON_MODULE_NAME
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param dev_deps: (experimental) List of dev dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDevDependency()``. Default: []
        :param pip: (experimental) Use pip with a requirements.txt file to track project dependencies. Default: true
        :param poetry: (experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing. Default: false
        :param projenrc_js: (experimental) Use projenrc in javascript. This will install ``projen`` as a JavaScript dependency and add a ``synth`` task which will run ``.projenrc.js``. Default: false
        :param projenrc_js_options: (experimental) Options related to projenrc in JavaScript. Default: - default options
        :param projenrc_python: (experimental) Use projenrc in Python. This will install ``projen`` as a Python dependency and add a ``synth`` task which will run ``.projenrc.py``. Default: true
        :param projenrc_python_options: (experimental) Options related to projenrc in python. Default: - default options
        :param pytest: (experimental) Include pytest tests. Default: true
        :param pytest_options: (experimental) pytest options. Default: - defaults
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist. Default: true
        :param setuptools: (experimental) Use setuptools with a setup.py script for packaging and publishing. Default: - true if the project type is library
        :param venv: (experimental) Use venv to manage a virtual environment for installing dependencies inside. Default: true
        :param venv_options: (experimental) Venv options. Default: - defaults
        :param client_languages: (experimental) The list of languages for which clients will be generated. A typescript client will always be generated.
        :param api_src_dir: (experimental) The directory in which the api generated code will reside, relative to the project srcdir.
        :param documentation_formats: (experimental) Formats to generate documentation in.
        :param generated_code_dir: (experimental) The directory in which generated client code will be generated, relative to the outdir of this project. Default: "generated"
        :param java_client_options: (experimental) Options for the generated java client (if specified in clientLanguages). These override the default inferred options.
        :param parsed_spec_file_name: (experimental) The name of the output parsed OpenAPI specification file. Must end with .json. Default: ".parsed-spec.json"
        :param python_client_options: (experimental) Options for the generated python client (if specified in clientLanguages). These override the default inferred options.
        :param spec_file: (experimental) The path to the OpenAPI specification file, relative to the project source directory (srcdir). Default: "spec/spec.yaml"
        :param typescript_client_options: (experimental) Options for the generated typescript client. These override the default inferred options.
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param author_email: (experimental) Author's e-mail. Default: $GIT_USER_EMAIL
        :param author_name: (experimental) Author's name. Default: $GIT_USER_NAME
        :param version: (experimental) Version of the package. Default: "0.1.0"
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package.
        :param homepage: (experimental) A URL to the website of the project.
        :param license: (experimental) License of this package as an SPDX identifier.
        :param poetry_options: (experimental) Additional options to set for poetry if using poetry.
        :param setup_config: (experimental) Additional fields to pass in the setup() function if using setuptools.
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options

        :stability: experimental
        '''
        options = OpenApiGatewayPythonProjectOptions(
            module_name=module_name,
            deps=deps,
            dev_deps=dev_deps,
            pip=pip,
            poetry=poetry,
            projenrc_js=projenrc_js,
            projenrc_js_options=projenrc_js_options,
            projenrc_python=projenrc_python,
            projenrc_python_options=projenrc_python_options,
            pytest=pytest,
            pytest_options=pytest_options,
            sample=sample,
            setuptools=setuptools,
            venv=venv,
            venv_options=venv_options,
            client_languages=client_languages,
            api_src_dir=api_src_dir,
            documentation_formats=documentation_formats,
            generated_code_dir=generated_code_dir,
            java_client_options=java_client_options,
            parsed_spec_file_name=parsed_spec_file_name,
            python_client_options=python_client_options,
            spec_file=spec_file,
            typescript_client_options=typescript_client_options,
            auto_approve_options=auto_approve_options,
            auto_merge=auto_merge,
            auto_merge_options=auto_merge_options,
            clobber=clobber,
            dev_container=dev_container,
            github=github,
            github_options=github_options,
            gitpod=gitpod,
            mergify=mergify,
            mergify_options=mergify_options,
            project_type=project_type,
            projen_credentials=projen_credentials,
            projen_token_secret=projen_token_secret,
            readme=readme,
            stale=stale,
            stale_options=stale_options,
            vscode=vscode,
            author_email=author_email,
            author_name=author_name,
            version=version,
            classifiers=classifiers,
            description=description,
            homepage=homepage,
            license=license,
            poetry_options=poetry_options,
            setup_config=setup_config,
            name=name,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
            renovatebot=renovatebot,
            renovatebot_options=renovatebot_options,
        )

        jsii.create(self.__class__, self, [options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiSrcDir")
    def api_src_dir(self) -> builtins.str:
        '''(experimental) The directory in which the api generated code will reside, relative to the project srcdir.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiSrcDir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generatedClients")
    def generated_clients(self) -> typing.Mapping[builtins.str, projen.Project]:
        '''(experimental) References to the client projects that were generated, keyed by language.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, projen.Project], jsii.get(self, "generatedClients"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generatedCodeDir")
    def generated_code_dir(self) -> builtins.str:
        '''(experimental) The directory in which generated client code will be generated, relative to the outdir of this project.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "generatedCodeDir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generatedPythonClient")
    def generated_python_client(self) -> projen.python.PythonProject:
        '''(experimental) A reference to the generated python client.

        :stability: experimental
        '''
        return typing.cast(projen.python.PythonProject, jsii.get(self, "generatedPythonClient"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="specDir")
    def spec_dir(self) -> builtins.str:
        '''(experimental) The directory in which the OpenAPI spec file(s) reside, relative to the project srcdir.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "specDir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="specFileName")
    def spec_file_name(self) -> builtins.str:
        '''(experimental) The name of the spec file.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "specFileName"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/open-api-gateway.OpenApiGatewayPythonProjectOptions",
    jsii_struct_bases=[
        projen.python.PythonProjectOptions, OpenApiGatewayProjectOptions
    ],
    name_mapping={
        "name": "name",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "renovatebot": "renovatebot",
        "renovatebot_options": "renovatebotOptions",
        "auto_approve_options": "autoApproveOptions",
        "auto_merge": "autoMerge",
        "auto_merge_options": "autoMergeOptions",
        "clobber": "clobber",
        "dev_container": "devContainer",
        "github": "github",
        "github_options": "githubOptions",
        "gitpod": "gitpod",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "project_type": "projectType",
        "projen_credentials": "projenCredentials",
        "projen_token_secret": "projenTokenSecret",
        "readme": "readme",
        "stale": "stale",
        "stale_options": "staleOptions",
        "vscode": "vscode",
        "author_email": "authorEmail",
        "author_name": "authorName",
        "version": "version",
        "classifiers": "classifiers",
        "description": "description",
        "homepage": "homepage",
        "license": "license",
        "poetry_options": "poetryOptions",
        "setup_config": "setupConfig",
        "module_name": "moduleName",
        "deps": "deps",
        "dev_deps": "devDeps",
        "pip": "pip",
        "poetry": "poetry",
        "projenrc_js": "projenrcJs",
        "projenrc_js_options": "projenrcJsOptions",
        "projenrc_python": "projenrcPython",
        "projenrc_python_options": "projenrcPythonOptions",
        "pytest": "pytest",
        "pytest_options": "pytestOptions",
        "sample": "sample",
        "setuptools": "setuptools",
        "venv": "venv",
        "venv_options": "venvOptions",
        "client_languages": "clientLanguages",
        "api_src_dir": "apiSrcDir",
        "documentation_formats": "documentationFormats",
        "generated_code_dir": "generatedCodeDir",
        "java_client_options": "javaClientOptions",
        "parsed_spec_file_name": "parsedSpecFileName",
        "python_client_options": "pythonClientOptions",
        "spec_file": "specFile",
        "typescript_client_options": "typescriptClientOptions",
    },
)
class OpenApiGatewayPythonProjectOptions(
    projen.python.PythonProjectOptions,
    OpenApiGatewayProjectOptions,
):
    def __init__(
        self,
        *,
        name: builtins.str,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[projen.ProjenrcOptions] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[projen.RenovatebotOptions] = None,
        auto_approve_options: typing.Optional[projen.github.AutoApproveOptions] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[projen.github.AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[projen.github.GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        projen_credentials: typing.Optional[projen.github.GithubCredentials] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[projen.github.StaleOptions] = None,
        vscode: typing.Optional[builtins.bool] = None,
        author_email: builtins.str,
        author_name: builtins.str,
        version: builtins.str,
        classifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        poetry_options: typing.Optional[projen.python.PoetryPyprojectOptionsWithoutDeps] = None,
        setup_config: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        module_name: builtins.str,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        pip: typing.Optional[builtins.bool] = None,
        poetry: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[projen.javascript.ProjenrcOptions] = None,
        projenrc_python: typing.Optional[builtins.bool] = None,
        projenrc_python_options: typing.Optional[projen.python.ProjenrcOptions] = None,
        pytest: typing.Optional[builtins.bool] = None,
        pytest_options: typing.Optional[projen.python.PytestOptions] = None,
        sample: typing.Optional[builtins.bool] = None,
        setuptools: typing.Optional[builtins.bool] = None,
        venv: typing.Optional[builtins.bool] = None,
        venv_options: typing.Optional[projen.python.VenvOptions] = None,
        client_languages: typing.Sequence[ClientLanguage],
        api_src_dir: typing.Optional[builtins.str] = None,
        documentation_formats: typing.Optional[typing.Sequence[DocumentationFormat]] = None,
        generated_code_dir: typing.Optional[builtins.str] = None,
        java_client_options: typing.Optional[projen.java.JavaProjectOptions] = None,
        parsed_spec_file_name: typing.Optional[builtins.str] = None,
        python_client_options: typing.Optional[projen.python.PythonProjectOptions] = None,
        spec_file: typing.Optional[builtins.str] = None,
        typescript_client_options: typing.Optional[projen.typescript.TypeScriptProjectOptions] = None,
    ) -> None:
        '''(experimental) Configuration for the OpenApiGatewayPythonProject.

        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param author_email: (experimental) Author's e-mail. Default: $GIT_USER_EMAIL
        :param author_name: (experimental) Author's name. Default: $GIT_USER_NAME
        :param version: (experimental) Version of the package. Default: "0.1.0"
        :param classifiers: (experimental) A list of PyPI trove classifiers that describe the project.
        :param description: (experimental) A short description of the package.
        :param homepage: (experimental) A URL to the website of the project.
        :param license: (experimental) License of this package as an SPDX identifier.
        :param poetry_options: (experimental) Additional options to set for poetry if using poetry.
        :param setup_config: (experimental) Additional fields to pass in the setup() function if using setuptools.
        :param module_name: (experimental) Name of the python package as used in imports and filenames. Must only consist of alphanumeric characters and underscores. Default: $PYTHON_MODULE_NAME
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param dev_deps: (experimental) List of dev dependencies for this project. Dependencies use the format: ``<module>@<semver>`` Additional dependencies can be added via ``project.addDevDependency()``. Default: []
        :param pip: (experimental) Use pip with a requirements.txt file to track project dependencies. Default: true
        :param poetry: (experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing. Default: false
        :param projenrc_js: (experimental) Use projenrc in javascript. This will install ``projen`` as a JavaScript dependency and add a ``synth`` task which will run ``.projenrc.js``. Default: false
        :param projenrc_js_options: (experimental) Options related to projenrc in JavaScript. Default: - default options
        :param projenrc_python: (experimental) Use projenrc in Python. This will install ``projen`` as a Python dependency and add a ``synth`` task which will run ``.projenrc.py``. Default: true
        :param projenrc_python_options: (experimental) Options related to projenrc in python. Default: - default options
        :param pytest: (experimental) Include pytest tests. Default: true
        :param pytest_options: (experimental) pytest options. Default: - defaults
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist. Default: true
        :param setuptools: (experimental) Use setuptools with a setup.py script for packaging and publishing. Default: - true if the project type is library
        :param venv: (experimental) Use venv to manage a virtual environment for installing dependencies inside. Default: true
        :param venv_options: (experimental) Venv options. Default: - defaults
        :param client_languages: (experimental) The list of languages for which clients will be generated. A typescript client will always be generated.
        :param api_src_dir: (experimental) The directory in which the api generated code will reside, relative to the project srcdir.
        :param documentation_formats: (experimental) Formats to generate documentation in.
        :param generated_code_dir: (experimental) The directory in which generated client code will be generated, relative to the outdir of this project. Default: "generated"
        :param java_client_options: (experimental) Options for the generated java client (if specified in clientLanguages). These override the default inferred options.
        :param parsed_spec_file_name: (experimental) The name of the output parsed OpenAPI specification file. Must end with .json. Default: ".parsed-spec.json"
        :param python_client_options: (experimental) Options for the generated python client (if specified in clientLanguages). These override the default inferred options.
        :param spec_file: (experimental) The path to the OpenAPI specification file, relative to the project source directory (srcdir). Default: "spec/spec.yaml"
        :param typescript_client_options: (experimental) Options for the generated typescript client. These override the default inferred options.

        :stability: experimental
        '''
        if isinstance(logging, dict):
            logging = projen.LoggerOptions(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = projen.ProjenrcOptions(**projenrc_json_options)
        if isinstance(renovatebot_options, dict):
            renovatebot_options = projen.RenovatebotOptions(**renovatebot_options)
        if isinstance(auto_approve_options, dict):
            auto_approve_options = projen.github.AutoApproveOptions(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = projen.github.AutoMergeOptions(**auto_merge_options)
        if isinstance(github_options, dict):
            github_options = projen.github.GitHubOptions(**github_options)
        if isinstance(mergify_options, dict):
            mergify_options = projen.github.MergifyOptions(**mergify_options)
        if isinstance(readme, dict):
            readme = projen.SampleReadmeProps(**readme)
        if isinstance(stale_options, dict):
            stale_options = projen.github.StaleOptions(**stale_options)
        if isinstance(poetry_options, dict):
            poetry_options = projen.python.PoetryPyprojectOptionsWithoutDeps(**poetry_options)
        if isinstance(projenrc_js_options, dict):
            projenrc_js_options = projen.javascript.ProjenrcOptions(**projenrc_js_options)
        if isinstance(projenrc_python_options, dict):
            projenrc_python_options = projen.python.ProjenrcOptions(**projenrc_python_options)
        if isinstance(pytest_options, dict):
            pytest_options = projen.python.PytestOptions(**pytest_options)
        if isinstance(venv_options, dict):
            venv_options = projen.python.VenvOptions(**venv_options)
        if isinstance(java_client_options, dict):
            java_client_options = projen.java.JavaProjectOptions(**java_client_options)
        if isinstance(python_client_options, dict):
            python_client_options = projen.python.PythonProjectOptions(**python_client_options)
        if isinstance(typescript_client_options, dict):
            typescript_client_options = projen.typescript.TypeScriptProjectOptions(**typescript_client_options)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "author_email": author_email,
            "author_name": author_name,
            "version": version,
            "module_name": module_name,
            "client_languages": client_languages,
        }
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if renovatebot is not None:
            self._values["renovatebot"] = renovatebot
        if renovatebot_options is not None:
            self._values["renovatebot_options"] = renovatebot_options
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_merge is not None:
            self._values["auto_merge"] = auto_merge
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if clobber is not None:
            self._values["clobber"] = clobber
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_credentials is not None:
            self._values["projen_credentials"] = projen_credentials
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if readme is not None:
            self._values["readme"] = readme
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if vscode is not None:
            self._values["vscode"] = vscode
        if classifiers is not None:
            self._values["classifiers"] = classifiers
        if description is not None:
            self._values["description"] = description
        if homepage is not None:
            self._values["homepage"] = homepage
        if license is not None:
            self._values["license"] = license
        if poetry_options is not None:
            self._values["poetry_options"] = poetry_options
        if setup_config is not None:
            self._values["setup_config"] = setup_config
        if deps is not None:
            self._values["deps"] = deps
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if pip is not None:
            self._values["pip"] = pip
        if poetry is not None:
            self._values["poetry"] = poetry
        if projenrc_js is not None:
            self._values["projenrc_js"] = projenrc_js
        if projenrc_js_options is not None:
            self._values["projenrc_js_options"] = projenrc_js_options
        if projenrc_python is not None:
            self._values["projenrc_python"] = projenrc_python
        if projenrc_python_options is not None:
            self._values["projenrc_python_options"] = projenrc_python_options
        if pytest is not None:
            self._values["pytest"] = pytest
        if pytest_options is not None:
            self._values["pytest_options"] = pytest_options
        if sample is not None:
            self._values["sample"] = sample
        if setuptools is not None:
            self._values["setuptools"] = setuptools
        if venv is not None:
            self._values["venv"] = venv
        if venv_options is not None:
            self._values["venv_options"] = venv_options
        if api_src_dir is not None:
            self._values["api_src_dir"] = api_src_dir
        if documentation_formats is not None:
            self._values["documentation_formats"] = documentation_formats
        if generated_code_dir is not None:
            self._values["generated_code_dir"] = generated_code_dir
        if java_client_options is not None:
            self._values["java_client_options"] = java_client_options
        if parsed_spec_file_name is not None:
            self._values["parsed_spec_file_name"] = parsed_spec_file_name
        if python_client_options is not None:
            self._values["python_client_options"] = python_client_options
        if spec_file is not None:
            self._values["spec_file"] = spec_file
        if typescript_client_options is not None:
            self._values["typescript_client_options"] = typescript_client_options

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logging(self) -> typing.Optional[projen.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[projen.LoggerOptions], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[projen.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[projen.Project], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(self) -> typing.Optional[projen.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[projen.ProjenrcOptions], result)

    @builtins.property
    def renovatebot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use renovatebot to handle dependency upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("renovatebot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def renovatebot_options(self) -> typing.Optional[projen.RenovatebotOptions]:
        '''(experimental) Options for renovatebot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("renovatebot_options")
        return typing.cast(typing.Optional[projen.RenovatebotOptions], result)

    @builtins.property
    def auto_approve_options(self) -> typing.Optional[projen.github.AutoApproveOptions]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[projen.github.AutoApproveOptions], result)

    @builtins.property
    def auto_merge(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable automatic merging on GitHub.

        Has no effect if ``github.mergify``
        is set to false.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_merge_options(self) -> typing.Optional[projen.github.AutoMergeOptions]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` or ``autoMerge`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[projen.github.AutoMergeOptions], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[projen.github.GitHubOptions]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[projen.github.GitHubOptions], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(self) -> typing.Optional[projen.github.MergifyOptions]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[projen.github.MergifyOptions], result)

    @builtins.property
    def project_type(self) -> typing.Optional[projen.ProjectType]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[projen.ProjectType], result)

    @builtins.property
    def projen_credentials(self) -> typing.Optional[projen.github.GithubCredentials]:
        '''(experimental) Choose a method of providing GitHub API access for projen workflows.

        :default: - use a personal access token named PROJEN_GITHUB_TOKEN

        :stability: experimental
        '''
        result = self._values.get("projen_credentials")
        return typing.cast(typing.Optional[projen.github.GithubCredentials], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :deprecated: use ``projenCredentials``

        :stability: deprecated
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme(self) -> typing.Optional[projen.SampleReadmeProps]:
        '''(experimental) The README setup.

        :default: - { filename: 'README.md', contents: '# replace this' }

        :stability: experimental

        Example::

            "{ filename: 'readme.md', contents: '# title' }"
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[projen.SampleReadmeProps], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[projen.github.StaleOptions]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[projen.github.StaleOptions], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_email(self) -> builtins.str:
        '''(experimental) Author's e-mail.

        :default: $GIT_USER_EMAIL

        :stability: experimental
        '''
        result = self._values.get("author_email")
        assert result is not None, "Required property 'author_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def author_name(self) -> builtins.str:
        '''(experimental) Author's name.

        :default: $GIT_USER_NAME

        :stability: experimental
        '''
        result = self._values.get("author_name")
        assert result is not None, "Required property 'author_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) Version of the package.

        :default: "0.1.0"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def classifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of PyPI trove classifiers that describe the project.

        :see: https://pypi.org/classifiers/
        :stability: experimental
        '''
        result = self._values.get("classifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A short description of the package.

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) A URL to the website of the project.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License of this package as an SPDX identifier.

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def poetry_options(
        self,
    ) -> typing.Optional[projen.python.PoetryPyprojectOptionsWithoutDeps]:
        '''(experimental) Additional options to set for poetry if using poetry.

        :stability: experimental
        '''
        result = self._values.get("poetry_options")
        return typing.cast(typing.Optional[projen.python.PoetryPyprojectOptionsWithoutDeps], result)

    @builtins.property
    def setup_config(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional fields to pass in the setup() function if using setuptools.

        :stability: experimental
        '''
        result = self._values.get("setup_config")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def module_name(self) -> builtins.str:
        '''(experimental) Name of the python package as used in imports and filenames.

        Must only consist of alphanumeric characters and underscores.

        :default: $PYTHON_MODULE_NAME

        :stability: experimental
        '''
        result = self._values.get("module_name")
        assert result is not None, "Required property 'module_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of runtime dependencies for this project.

        Dependencies use the format: ``<module>@<semver>``

        Additional dependencies can be added via ``project.addDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dev dependencies for this project.

        Dependencies use the format: ``<module>@<semver>``

        Additional dependencies can be added via ``project.addDevDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pip(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use pip with a requirements.txt file to track project dependencies.

        :default: true

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("pip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def poetry(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use poetry to manage your project dependencies, virtual environment, and (optional) packaging/publishing.

        :default: false

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("poetry")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use projenrc in javascript.

        This will install ``projen`` as a JavaScript dependency and add a ``synth``
        task which will run ``.projenrc.js``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_js")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js_options(self) -> typing.Optional[projen.javascript.ProjenrcOptions]:
        '''(experimental) Options related to projenrc in JavaScript.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_js_options")
        return typing.cast(typing.Optional[projen.javascript.ProjenrcOptions], result)

    @builtins.property
    def projenrc_python(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use projenrc in Python.

        This will install ``projen`` as a Python dependency and add a ``synth``
        task which will run ``.projenrc.py``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projenrc_python")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_python_options(self) -> typing.Optional[projen.python.ProjenrcOptions]:
        '''(experimental) Options related to projenrc in python.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_python_options")
        return typing.cast(typing.Optional[projen.python.ProjenrcOptions], result)

    @builtins.property
    def pytest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include pytest tests.

        :default: true

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("pytest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pytest_options(self) -> typing.Optional[projen.python.PytestOptions]:
        '''(experimental) pytest options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("pytest_options")
        return typing.cast(typing.Optional[projen.python.PytestOptions], result)

    @builtins.property
    def sample(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include sample code and test if the relevant directories don't exist.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def setuptools(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use setuptools with a setup.py script for packaging and publishing.

        :default: - true if the project type is library

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("setuptools")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def venv(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use venv to manage a virtual environment for installing dependencies inside.

        :default: true

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("venv")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def venv_options(self) -> typing.Optional[projen.python.VenvOptions]:
        '''(experimental) Venv options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("venv_options")
        return typing.cast(typing.Optional[projen.python.VenvOptions], result)

    @builtins.property
    def client_languages(self) -> typing.List[ClientLanguage]:
        '''(experimental) The list of languages for which clients will be generated.

        A typescript client will always be generated.

        :stability: experimental
        '''
        result = self._values.get("client_languages")
        assert result is not None, "Required property 'client_languages' is missing"
        return typing.cast(typing.List[ClientLanguage], result)

    @builtins.property
    def api_src_dir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The directory in which the api generated code will reside, relative to the project srcdir.

        :stability: experimental
        '''
        result = self._values.get("api_src_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def documentation_formats(
        self,
    ) -> typing.Optional[typing.List[DocumentationFormat]]:
        '''(experimental) Formats to generate documentation in.

        :stability: experimental
        '''
        result = self._values.get("documentation_formats")
        return typing.cast(typing.Optional[typing.List[DocumentationFormat]], result)

    @builtins.property
    def generated_code_dir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The directory in which generated client code will be generated, relative to the outdir of this project.

        :default: "generated"

        :stability: experimental
        '''
        result = self._values.get("generated_code_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def java_client_options(self) -> typing.Optional[projen.java.JavaProjectOptions]:
        '''(experimental) Options for the generated java client (if specified in clientLanguages).

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("java_client_options")
        return typing.cast(typing.Optional[projen.java.JavaProjectOptions], result)

    @builtins.property
    def parsed_spec_file_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the output parsed OpenAPI specification file.

        Must end with .json.

        :default: ".parsed-spec.json"

        :stability: experimental
        '''
        result = self._values.get("parsed_spec_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def python_client_options(
        self,
    ) -> typing.Optional[projen.python.PythonProjectOptions]:
        '''(experimental) Options for the generated python client (if specified in clientLanguages).

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("python_client_options")
        return typing.cast(typing.Optional[projen.python.PythonProjectOptions], result)

    @builtins.property
    def spec_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The path to the OpenAPI specification file, relative to the project source directory (srcdir).

        :default: "spec/spec.yaml"

        :stability: experimental
        '''
        result = self._values.get("spec_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def typescript_client_options(
        self,
    ) -> typing.Optional[projen.typescript.TypeScriptProjectOptions]:
        '''(experimental) Options for the generated typescript client.

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("typescript_client_options")
        return typing.cast(typing.Optional[projen.typescript.TypeScriptProjectOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenApiGatewayPythonProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpenApiGatewayTsProject(
    projen.typescript.TypeScriptProject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-prototyping-sdk/open-api-gateway.OpenApiGatewayTsProject",
):
    '''(experimental) Synthesizes a Typescript Project with an OpenAPI spec, generated clients, a CDK construct for deploying the API with API Gateway, and generated lambda handler wrappers for type-safe handling of requests.

    :stability: experimental
    :pjid: open-api-gateway-ts
    '''

    def __init__(
        self,
        *,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[projen.javascript.EslintOptions] = None,
        libdir: typing.Optional[builtins.str] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[projen.typescript.ProjenrcOptions] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        srcdir: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        client_languages: typing.Sequence[ClientLanguage],
        api_src_dir: typing.Optional[builtins.str] = None,
        documentation_formats: typing.Optional[typing.Sequence[DocumentationFormat]] = None,
        generated_code_dir: typing.Optional[builtins.str] = None,
        java_client_options: typing.Optional[projen.java.JavaProjectOptions] = None,
        parsed_spec_file_name: typing.Optional[builtins.str] = None,
        python_client_options: typing.Optional[projen.python.PythonProjectOptions] = None,
        spec_file: typing.Optional[builtins.str] = None,
        typescript_client_options: typing.Optional[projen.typescript.TypeScriptProjectOptions] = None,
        default_release_branch: builtins.str,
        artifacts_directory: typing.Optional[builtins.str] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_triggers: typing.Optional[projen.github.workflows.Triggers] = None,
        bundler_options: typing.Optional[projen.javascript.BundlerOptions] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[projen.github.DependabotOptions] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[projen.javascript.UpgradeDependenciesOptions] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[projen.javascript.JestOptions] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        package: typing.Optional[builtins.bool] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[projen.javascript.PrettierOptions] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[projen.javascript.ProjenrcOptions] = None,
        projen_version: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        release: typing.Optional[builtins.bool] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        workflow_git_identity: typing.Optional[projen.github.GitIdentity] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        auto_approve_options: typing.Optional[projen.github.AutoApproveOptions] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[projen.github.AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[projen.github.GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        projen_credentials: typing.Optional[projen.github.GithubCredentials] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[projen.github.StaleOptions] = None,
        vscode: typing.Optional[builtins.bool] = None,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_artifact_options: typing.Optional[projen.javascript.CodeArtifactOptions] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[projen.javascript.NpmAccess] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        package_manager: typing.Optional[projen.javascript.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        peer_dependency_options: typing.Optional[projen.javascript.PeerDependencyOptions] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        scoped_packages_options: typing.Optional[typing.Sequence[projen.javascript.ScopedPackagesOptions]] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stability: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_trigger: typing.Optional[projen.release.ReleaseTrigger] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: builtins.str,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[projen.ProjenrcOptions] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[projen.RenovatebotOptions] = None,
    ) -> None:
        '''
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param client_languages: (experimental) The list of languages for which clients will be generated. A typescript client will always be generated.
        :param api_src_dir: (experimental) The directory in which the api generated code will reside, relative to the project srcdir.
        :param documentation_formats: (experimental) Formats to generate documentation in.
        :param generated_code_dir: (experimental) The directory in which generated client code will be generated, relative to the outdir of this project. Default: "generated"
        :param java_client_options: (experimental) Options for the generated java client (if specified in clientLanguages). These override the default inferred options.
        :param parsed_spec_file_name: (experimental) The name of the output parsed OpenAPI specification file. Must end with .json. Default: ".parsed-spec.json"
        :param python_client_options: (experimental) Options for the generated python client (if specified in clientLanguages). These override the default inferred options.
        :param spec_file: (experimental) The path to the OpenAPI specification file, relative to the project source directory (srcdir). Default: "spec/spec.yaml"
        :param typescript_client_options: (experimental) Options for the generated typescript client. These override the default inferred options.
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_triggers: (experimental) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps_upgrade: (experimental) Use github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for ``UpgradeDependencies``. Default: - default options
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: true
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version to use in GitHub workflows. Default: - same as ``minNodeVersion``
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Author's Organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param code_artifact_options: (experimental) Options for npm packages using AWS CodeArtifact. This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact Default: - undefined
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json Default: "lib/index.js"
        :param homepage: (experimental) Package's Homepage / Website.
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param max_node_version: (experimental) Minimum node.js version to require via ``engines`` (inclusive). Default: - no max
        :param min_node_version: (experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive). Default: - no "engines" specified
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param scoped_packages_options: (experimental) Options for privately hosted scoped packages. Default: - fetch all scoped packages from the public npm registry
        :param scripts: (experimental) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Default: {}
        :param stability: (experimental) Package's Stability.
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: - no prefix
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with standard-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options

        :stability: experimental
        '''
        options = OpenApiGatewayTsProjectOptions(
            disable_tsconfig=disable_tsconfig,
            docgen=docgen,
            docs_directory=docs_directory,
            entrypoint_types=entrypoint_types,
            eslint=eslint,
            eslint_options=eslint_options,
            libdir=libdir,
            projenrc_ts=projenrc_ts,
            projenrc_ts_options=projenrc_ts_options,
            sample_code=sample_code,
            srcdir=srcdir,
            testdir=testdir,
            tsconfig=tsconfig,
            tsconfig_dev=tsconfig_dev,
            tsconfig_dev_file=tsconfig_dev_file,
            typescript_version=typescript_version,
            client_languages=client_languages,
            api_src_dir=api_src_dir,
            documentation_formats=documentation_formats,
            generated_code_dir=generated_code_dir,
            java_client_options=java_client_options,
            parsed_spec_file_name=parsed_spec_file_name,
            python_client_options=python_client_options,
            spec_file=spec_file,
            typescript_client_options=typescript_client_options,
            default_release_branch=default_release_branch,
            artifacts_directory=artifacts_directory,
            auto_approve_upgrades=auto_approve_upgrades,
            build_workflow=build_workflow,
            build_workflow_triggers=build_workflow_triggers,
            bundler_options=bundler_options,
            code_cov=code_cov,
            code_cov_token_secret=code_cov_token_secret,
            copyright_owner=copyright_owner,
            copyright_period=copyright_period,
            dependabot=dependabot,
            dependabot_options=dependabot_options,
            deps_upgrade=deps_upgrade,
            deps_upgrade_options=deps_upgrade_options,
            gitignore=gitignore,
            jest=jest,
            jest_options=jest_options,
            mutable_build=mutable_build,
            npmignore=npmignore,
            npmignore_enabled=npmignore_enabled,
            package=package,
            prettier=prettier,
            prettier_options=prettier_options,
            projen_dev_dependency=projen_dev_dependency,
            projenrc_js=projenrc_js,
            projenrc_js_options=projenrc_js_options,
            projen_version=projen_version,
            pull_request_template=pull_request_template,
            pull_request_template_contents=pull_request_template_contents,
            release=release,
            release_to_npm=release_to_npm,
            release_workflow=release_workflow,
            workflow_bootstrap_steps=workflow_bootstrap_steps,
            workflow_git_identity=workflow_git_identity,
            workflow_node_version=workflow_node_version,
            auto_approve_options=auto_approve_options,
            auto_merge=auto_merge,
            auto_merge_options=auto_merge_options,
            clobber=clobber,
            dev_container=dev_container,
            github=github,
            github_options=github_options,
            gitpod=gitpod,
            mergify=mergify,
            mergify_options=mergify_options,
            project_type=project_type,
            projen_credentials=projen_credentials,
            projen_token_secret=projen_token_secret,
            readme=readme,
            stale=stale,
            stale_options=stale_options,
            vscode=vscode,
            allow_library_dependencies=allow_library_dependencies,
            author_email=author_email,
            author_name=author_name,
            author_organization=author_organization,
            author_url=author_url,
            auto_detect_bin=auto_detect_bin,
            bin=bin,
            bugs_email=bugs_email,
            bugs_url=bugs_url,
            bundled_deps=bundled_deps,
            code_artifact_options=code_artifact_options,
            deps=deps,
            description=description,
            dev_deps=dev_deps,
            entrypoint=entrypoint,
            homepage=homepage,
            keywords=keywords,
            license=license,
            licensed=licensed,
            max_node_version=max_node_version,
            min_node_version=min_node_version,
            npm_access=npm_access,
            npm_registry=npm_registry,
            npm_registry_url=npm_registry_url,
            npm_token_secret=npm_token_secret,
            package_manager=package_manager,
            package_name=package_name,
            peer_dependency_options=peer_dependency_options,
            peer_deps=peer_deps,
            repository=repository,
            repository_directory=repository_directory,
            scoped_packages_options=scoped_packages_options,
            scripts=scripts,
            stability=stability,
            jsii_release_version=jsii_release_version,
            major_version=major_version,
            npm_dist_tag=npm_dist_tag,
            post_build_steps=post_build_steps,
            prerelease=prerelease,
            publish_dry_run=publish_dry_run,
            publish_tasks=publish_tasks,
            release_branches=release_branches,
            release_every_commit=release_every_commit,
            release_failure_issue=release_failure_issue,
            release_failure_issue_label=release_failure_issue_label,
            release_schedule=release_schedule,
            release_tag_prefix=release_tag_prefix,
            release_trigger=release_trigger,
            release_workflow_name=release_workflow_name,
            release_workflow_setup_steps=release_workflow_setup_steps,
            versionrc_options=versionrc_options,
            workflow_container_image=workflow_container_image,
            workflow_runs_on=workflow_runs_on,
            name=name,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
            renovatebot=renovatebot,
            renovatebot_options=renovatebot_options,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="postSynthesize")
    def post_synthesize(self) -> None:
        '''(experimental) Called after all components are synthesized.

        Order is *not* guaranteed.

        :stability: experimental
        :inheritDoc: true
        '''
        return typing.cast(None, jsii.invoke(self, "postSynthesize", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiSrcDir")
    def api_src_dir(self) -> builtins.str:
        '''(experimental) The directory in which the api generated code will reside, relative to the project srcdir.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiSrcDir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generatedClients")
    def generated_clients(self) -> typing.Mapping[builtins.str, projen.Project]:
        '''(experimental) References to the client projects that were generated, keyed by language.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, projen.Project], jsii.get(self, "generatedClients"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generatedCodeDir")
    def generated_code_dir(self) -> builtins.str:
        '''(experimental) The directory in which generated client code will be generated, relative to the outdir of this project.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "generatedCodeDir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generatedTypescriptClient")
    def generated_typescript_client(self) -> projen.typescript.TypeScriptProject:
        '''(experimental) A reference to the generated typescript client.

        :stability: experimental
        '''
        return typing.cast(projen.typescript.TypeScriptProject, jsii.get(self, "generatedTypescriptClient"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="specDir")
    def spec_dir(self) -> builtins.str:
        '''(experimental) The directory in which the OpenAPI spec file(s) reside, relative to the project srcdir.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "specDir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="specFileName")
    def spec_file_name(self) -> builtins.str:
        '''(experimental) The name of the spec file.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "specFileName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pnpmWorkspace")
    def pnpm_workspace(self) -> typing.Optional[projen.YamlFile]:
        '''(experimental) Reference to the PNPM workspace yaml file which adds the dependency between this project and the generated typescript client when this project is used in a monorepo, and the package manager is PNPM.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[projen.YamlFile], jsii.get(self, "pnpmWorkspace"))


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/open-api-gateway.OpenApiGatewayTsProjectOptions",
    jsii_struct_bases=[
        projen.typescript.TypeScriptProjectOptions, OpenApiGatewayProjectOptions
    ],
    name_mapping={
        "name": "name",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "renovatebot": "renovatebot",
        "renovatebot_options": "renovatebotOptions",
        "auto_approve_options": "autoApproveOptions",
        "auto_merge": "autoMerge",
        "auto_merge_options": "autoMergeOptions",
        "clobber": "clobber",
        "dev_container": "devContainer",
        "github": "github",
        "github_options": "githubOptions",
        "gitpod": "gitpod",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "project_type": "projectType",
        "projen_credentials": "projenCredentials",
        "projen_token_secret": "projenTokenSecret",
        "readme": "readme",
        "stale": "stale",
        "stale_options": "staleOptions",
        "vscode": "vscode",
        "allow_library_dependencies": "allowLibraryDependencies",
        "author_email": "authorEmail",
        "author_name": "authorName",
        "author_organization": "authorOrganization",
        "author_url": "authorUrl",
        "auto_detect_bin": "autoDetectBin",
        "bin": "bin",
        "bugs_email": "bugsEmail",
        "bugs_url": "bugsUrl",
        "bundled_deps": "bundledDeps",
        "code_artifact_options": "codeArtifactOptions",
        "deps": "deps",
        "description": "description",
        "dev_deps": "devDeps",
        "entrypoint": "entrypoint",
        "homepage": "homepage",
        "keywords": "keywords",
        "license": "license",
        "licensed": "licensed",
        "max_node_version": "maxNodeVersion",
        "min_node_version": "minNodeVersion",
        "npm_access": "npmAccess",
        "npm_registry": "npmRegistry",
        "npm_registry_url": "npmRegistryUrl",
        "npm_token_secret": "npmTokenSecret",
        "package_manager": "packageManager",
        "package_name": "packageName",
        "peer_dependency_options": "peerDependencyOptions",
        "peer_deps": "peerDeps",
        "repository": "repository",
        "repository_directory": "repositoryDirectory",
        "scoped_packages_options": "scopedPackagesOptions",
        "scripts": "scripts",
        "stability": "stability",
        "jsii_release_version": "jsiiReleaseVersion",
        "major_version": "majorVersion",
        "npm_dist_tag": "npmDistTag",
        "post_build_steps": "postBuildSteps",
        "prerelease": "prerelease",
        "publish_dry_run": "publishDryRun",
        "publish_tasks": "publishTasks",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_failure_issue": "releaseFailureIssue",
        "release_failure_issue_label": "releaseFailureIssueLabel",
        "release_schedule": "releaseSchedule",
        "release_tag_prefix": "releaseTagPrefix",
        "release_trigger": "releaseTrigger",
        "release_workflow_name": "releaseWorkflowName",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "versionrc_options": "versionrcOptions",
        "workflow_container_image": "workflowContainerImage",
        "workflow_runs_on": "workflowRunsOn",
        "default_release_branch": "defaultReleaseBranch",
        "artifacts_directory": "artifactsDirectory",
        "auto_approve_upgrades": "autoApproveUpgrades",
        "build_workflow": "buildWorkflow",
        "build_workflow_triggers": "buildWorkflowTriggers",
        "bundler_options": "bundlerOptions",
        "code_cov": "codeCov",
        "code_cov_token_secret": "codeCovTokenSecret",
        "copyright_owner": "copyrightOwner",
        "copyright_period": "copyrightPeriod",
        "dependabot": "dependabot",
        "dependabot_options": "dependabotOptions",
        "deps_upgrade": "depsUpgrade",
        "deps_upgrade_options": "depsUpgradeOptions",
        "gitignore": "gitignore",
        "jest": "jest",
        "jest_options": "jestOptions",
        "mutable_build": "mutableBuild",
        "npmignore": "npmignore",
        "npmignore_enabled": "npmignoreEnabled",
        "package": "package",
        "prettier": "prettier",
        "prettier_options": "prettierOptions",
        "projen_dev_dependency": "projenDevDependency",
        "projenrc_js": "projenrcJs",
        "projenrc_js_options": "projenrcJsOptions",
        "projen_version": "projenVersion",
        "pull_request_template": "pullRequestTemplate",
        "pull_request_template_contents": "pullRequestTemplateContents",
        "release": "release",
        "release_to_npm": "releaseToNpm",
        "release_workflow": "releaseWorkflow",
        "workflow_bootstrap_steps": "workflowBootstrapSteps",
        "workflow_git_identity": "workflowGitIdentity",
        "workflow_node_version": "workflowNodeVersion",
        "disable_tsconfig": "disableTsconfig",
        "docgen": "docgen",
        "docs_directory": "docsDirectory",
        "entrypoint_types": "entrypointTypes",
        "eslint": "eslint",
        "eslint_options": "eslintOptions",
        "libdir": "libdir",
        "projenrc_ts": "projenrcTs",
        "projenrc_ts_options": "projenrcTsOptions",
        "sample_code": "sampleCode",
        "srcdir": "srcdir",
        "testdir": "testdir",
        "tsconfig": "tsconfig",
        "tsconfig_dev": "tsconfigDev",
        "tsconfig_dev_file": "tsconfigDevFile",
        "typescript_version": "typescriptVersion",
        "client_languages": "clientLanguages",
        "api_src_dir": "apiSrcDir",
        "documentation_formats": "documentationFormats",
        "generated_code_dir": "generatedCodeDir",
        "java_client_options": "javaClientOptions",
        "parsed_spec_file_name": "parsedSpecFileName",
        "python_client_options": "pythonClientOptions",
        "spec_file": "specFile",
        "typescript_client_options": "typescriptClientOptions",
    },
)
class OpenApiGatewayTsProjectOptions(
    projen.typescript.TypeScriptProjectOptions,
    OpenApiGatewayProjectOptions,
):
    def __init__(
        self,
        *,
        name: builtins.str,
        logging: typing.Optional[projen.LoggerOptions] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[projen.Project] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[projen.ProjenrcOptions] = None,
        renovatebot: typing.Optional[builtins.bool] = None,
        renovatebot_options: typing.Optional[projen.RenovatebotOptions] = None,
        auto_approve_options: typing.Optional[projen.github.AutoApproveOptions] = None,
        auto_merge: typing.Optional[builtins.bool] = None,
        auto_merge_options: typing.Optional[projen.github.AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[projen.github.GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[projen.github.MergifyOptions] = None,
        project_type: typing.Optional[projen.ProjectType] = None,
        projen_credentials: typing.Optional[projen.github.GithubCredentials] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[projen.SampleReadmeProps] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[projen.github.StaleOptions] = None,
        vscode: typing.Optional[builtins.bool] = None,
        allow_library_dependencies: typing.Optional[builtins.bool] = None,
        author_email: typing.Optional[builtins.str] = None,
        author_name: typing.Optional[builtins.str] = None,
        author_organization: typing.Optional[builtins.bool] = None,
        author_url: typing.Optional[builtins.str] = None,
        auto_detect_bin: typing.Optional[builtins.bool] = None,
        bin: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bugs_email: typing.Optional[builtins.str] = None,
        bugs_url: typing.Optional[builtins.str] = None,
        bundled_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_artifact_options: typing.Optional[projen.javascript.CodeArtifactOptions] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        dev_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        entrypoint: typing.Optional[builtins.str] = None,
        homepage: typing.Optional[builtins.str] = None,
        keywords: typing.Optional[typing.Sequence[builtins.str]] = None,
        license: typing.Optional[builtins.str] = None,
        licensed: typing.Optional[builtins.bool] = None,
        max_node_version: typing.Optional[builtins.str] = None,
        min_node_version: typing.Optional[builtins.str] = None,
        npm_access: typing.Optional[projen.javascript.NpmAccess] = None,
        npm_registry: typing.Optional[builtins.str] = None,
        npm_registry_url: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        package_manager: typing.Optional[projen.javascript.NodePackageManager] = None,
        package_name: typing.Optional[builtins.str] = None,
        peer_dependency_options: typing.Optional[projen.javascript.PeerDependencyOptions] = None,
        peer_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        repository: typing.Optional[builtins.str] = None,
        repository_directory: typing.Optional[builtins.str] = None,
        scoped_packages_options: typing.Optional[typing.Sequence[projen.javascript.ScopedPackagesOptions]] = None,
        scripts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        stability: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_trigger: typing.Optional[projen.release.ReleaseTrigger] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_release_branch: builtins.str,
        artifacts_directory: typing.Optional[builtins.str] = None,
        auto_approve_upgrades: typing.Optional[builtins.bool] = None,
        build_workflow: typing.Optional[builtins.bool] = None,
        build_workflow_triggers: typing.Optional[projen.github.workflows.Triggers] = None,
        bundler_options: typing.Optional[projen.javascript.BundlerOptions] = None,
        code_cov: typing.Optional[builtins.bool] = None,
        code_cov_token_secret: typing.Optional[builtins.str] = None,
        copyright_owner: typing.Optional[builtins.str] = None,
        copyright_period: typing.Optional[builtins.str] = None,
        dependabot: typing.Optional[builtins.bool] = None,
        dependabot_options: typing.Optional[projen.github.DependabotOptions] = None,
        deps_upgrade: typing.Optional[builtins.bool] = None,
        deps_upgrade_options: typing.Optional[projen.javascript.UpgradeDependenciesOptions] = None,
        gitignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        jest: typing.Optional[builtins.bool] = None,
        jest_options: typing.Optional[projen.javascript.JestOptions] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        npmignore: typing.Optional[typing.Sequence[builtins.str]] = None,
        npmignore_enabled: typing.Optional[builtins.bool] = None,
        package: typing.Optional[builtins.bool] = None,
        prettier: typing.Optional[builtins.bool] = None,
        prettier_options: typing.Optional[projen.javascript.PrettierOptions] = None,
        projen_dev_dependency: typing.Optional[builtins.bool] = None,
        projenrc_js: typing.Optional[builtins.bool] = None,
        projenrc_js_options: typing.Optional[projen.javascript.ProjenrcOptions] = None,
        projen_version: typing.Optional[builtins.str] = None,
        pull_request_template: typing.Optional[builtins.bool] = None,
        pull_request_template_contents: typing.Optional[typing.Sequence[builtins.str]] = None,
        release: typing.Optional[builtins.bool] = None,
        release_to_npm: typing.Optional[builtins.bool] = None,
        release_workflow: typing.Optional[builtins.bool] = None,
        workflow_bootstrap_steps: typing.Optional[typing.Sequence[projen.github.workflows.JobStep]] = None,
        workflow_git_identity: typing.Optional[projen.github.GitIdentity] = None,
        workflow_node_version: typing.Optional[builtins.str] = None,
        disable_tsconfig: typing.Optional[builtins.bool] = None,
        docgen: typing.Optional[builtins.bool] = None,
        docs_directory: typing.Optional[builtins.str] = None,
        entrypoint_types: typing.Optional[builtins.str] = None,
        eslint: typing.Optional[builtins.bool] = None,
        eslint_options: typing.Optional[projen.javascript.EslintOptions] = None,
        libdir: typing.Optional[builtins.str] = None,
        projenrc_ts: typing.Optional[builtins.bool] = None,
        projenrc_ts_options: typing.Optional[projen.typescript.ProjenrcOptions] = None,
        sample_code: typing.Optional[builtins.bool] = None,
        srcdir: typing.Optional[builtins.str] = None,
        testdir: typing.Optional[builtins.str] = None,
        tsconfig: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev: typing.Optional[projen.javascript.TypescriptConfigOptions] = None,
        tsconfig_dev_file: typing.Optional[builtins.str] = None,
        typescript_version: typing.Optional[builtins.str] = None,
        client_languages: typing.Sequence[ClientLanguage],
        api_src_dir: typing.Optional[builtins.str] = None,
        documentation_formats: typing.Optional[typing.Sequence[DocumentationFormat]] = None,
        generated_code_dir: typing.Optional[builtins.str] = None,
        java_client_options: typing.Optional[projen.java.JavaProjectOptions] = None,
        parsed_spec_file_name: typing.Optional[builtins.str] = None,
        python_client_options: typing.Optional[projen.python.PythonProjectOptions] = None,
        spec_file: typing.Optional[builtins.str] = None,
        typescript_client_options: typing.Optional[projen.typescript.TypeScriptProjectOptions] = None,
    ) -> None:
        '''(experimental) Configuration for the OpenApiGatewayTsProject.

        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param renovatebot: (experimental) Use renovatebot to handle dependency upgrades. Default: false
        :param renovatebot_options: (experimental) Options for renovatebot. Default: - default options
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge: (experimental) Enable automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: true
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` or ``autoMerge`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_credentials: (experimental) Choose a method of providing GitHub API access for projen workflows. Default: - use a personal access token named PROJEN_GITHUB_TOKEN
        :param projen_token_secret: (deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: false
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param allow_library_dependencies: (experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``. This is normally only allowed for libraries. For apps, there's no meaning for specifying these. Default: true
        :param author_email: (experimental) Author's e-mail.
        :param author_name: (experimental) Author's name.
        :param author_organization: (experimental) Author's Organization.
        :param author_url: (experimental) Author's URL / Website.
        :param auto_detect_bin: (experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section. Default: true
        :param bin: (experimental) Binary programs vended with your module. You can use this option to add/customize how binaries are represented in your ``package.json``, but unless ``autoDetectBin`` is ``false``, every executable file under ``bin`` will automatically be added to this section.
        :param bugs_email: (experimental) The email address to which issues should be reported.
        :param bugs_url: (experimental) The url to your project's issue tracker.
        :param bundled_deps: (experimental) List of dependencies to bundle into this module. These modules will be added both to the ``dependencies`` section and ``bundledDependencies`` section of your ``package.json``. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include.
        :param code_artifact_options: (experimental) Options for npm packages using AWS CodeArtifact. This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact Default: - undefined
        :param deps: (experimental) Runtime dependencies of this module. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param description: (experimental) The description is just a string that helps people understand the purpose of the package. It can be used when searching for packages in a package manager as well. See https://classic.yarnpkg.com/en/docs/package-json/#toc-description
        :param dev_deps: (experimental) Build dependencies for this module. These dependencies will only be available in your build environment but will not be fetched when this module is consumed. The recommendation is to only specify the module name here (e.g. ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the sense that it will add the module as a dependency to your ``package.json`` file with the latest version (``^``). You can specify semver requirements in the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and this will be what you ``package.json`` will eventually include. Default: []
        :param entrypoint: (experimental) Module entrypoint (``main`` in ``package.json``). Set to an empty string to not include ``main`` in your package.json Default: "lib/index.js"
        :param homepage: (experimental) Package's Homepage / Website.
        :param keywords: (experimental) Keywords to include in ``package.json``.
        :param license: (experimental) License's SPDX identifier. See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses. Use the ``licensed`` option if you want to no license to be specified. Default: "Apache-2.0"
        :param licensed: (experimental) Indicates if a license should be added. Default: true
        :param max_node_version: (experimental) Minimum node.js version to require via ``engines`` (inclusive). Default: - no max
        :param min_node_version: (experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive). Default: - no "engines" specified
        :param npm_access: (experimental) Access level of the npm package. Default: - for scoped packages (e.g. ``foo@bar``), the default is ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is ``NpmAccess.PUBLIC``.
        :param npm_registry: (deprecated) The host name of the npm registry to publish to. Cannot be set together with ``npmRegistryUrl``.
        :param npm_registry_url: (experimental) The base URL of the npm package registry. Must be a URL (e.g. start with "https://" or "http://") Default: "https://registry.npmjs.org"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: "NPM_TOKEN"
        :param package_manager: (experimental) The Node Package Manager used to execute scripts. Default: NodePackageManager.YARN
        :param package_name: (experimental) The "name" in package.json. Default: - defaults to project name
        :param peer_dependency_options: (experimental) Options for ``peerDeps``.
        :param peer_deps: (experimental) Peer dependencies for this module. Dependencies listed here are required to be installed (and satisfied) by the *consumer* of this library. Using peer dependencies allows you to ensure that only a single module of a certain library exists in the ``node_modules`` tree of your consumers. Note that prior to npm@7, peer dependencies are *not* automatically installed, which means that adding peer dependencies to a library will be a breaking change for your customers. Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is enabled by default), projen will automatically add a dev dependency with a pinned version for each peer dependency. This will ensure that you build & test your module against the lowest peer version required. Default: []
        :param repository: (experimental) The repository is the location where the actual code for your package lives. See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository
        :param repository_directory: (experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.
        :param scoped_packages_options: (experimental) Options for privately hosted scoped packages. Default: - fetch all scoped packages from the public npm registry
        :param scripts: (experimental) npm scripts to include. If a script has the same name as a standard script, the standard script will be overwritten. Default: {}
        :param stability: (experimental) Package's Stability.
        :param jsii_release_version: (experimental) Version requirement of ``publib`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: - no prefix
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with standard-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param default_release_branch: (experimental) The name of the main release branch. Default: "main"
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param auto_approve_upgrades: (experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued). Throw if set to true but ``autoApproveOptions`` are not defined. Default: - true
        :param build_workflow: (experimental) Define a GitHub workflow for building PRs. Default: - true if not a subproject
        :param build_workflow_triggers: (experimental) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"
        :param bundler_options: (experimental) Options for ``Bundler``.
        :param code_cov: (experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret. Default: false
        :param code_cov_token_secret: (experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories. Default: - if this option is not specified, only public repositories are supported
        :param copyright_owner: (experimental) License copyright owner. Default: - defaults to the value of authorName or "" if ``authorName`` is undefined.
        :param copyright_period: (experimental) The copyright years to put in the LICENSE file. Default: - current year
        :param dependabot: (experimental) Use dependabot to handle dependency upgrades. Cannot be used in conjunction with ``depsUpgrade``. Default: false
        :param dependabot_options: (experimental) Options for dependabot. Default: - default options
        :param deps_upgrade: (experimental) Use github workflows to handle dependency upgrades. Cannot be used in conjunction with ``dependabot``. Default: true
        :param deps_upgrade_options: (experimental) Options for ``UpgradeDependencies``. Default: - default options
        :param gitignore: (experimental) Additional entries to .gitignore.
        :param jest: (experimental) Setup jest unit tests. Default: true
        :param jest_options: (experimental) Jest options. Default: - default options
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. Default: true
        :param npmignore: (deprecated) Additional entries to .npmignore.
        :param npmignore_enabled: (experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs. Default: true
        :param package: (experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``). Default: true
        :param prettier: (experimental) Setup prettier. Default: false
        :param prettier_options: (experimental) Prettier options. Default: - default options
        :param projen_dev_dependency: (experimental) Indicates of "projen" should be installed as a devDependency. Default: true
        :param projenrc_js: (experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation. Default: - true if projenrcJson is false
        :param projenrc_js_options: (experimental) Options for .projenrc.js. Default: - default options
        :param projen_version: (experimental) Version of projen to install. Default: - Defaults to the latest version.
        :param pull_request_template: (experimental) Include a GitHub pull request template. Default: true
        :param pull_request_template_contents: (experimental) The contents of the pull request template. Default: - default content
        :param release: (experimental) Add release management to this project. Default: - true (false for subprojects)
        :param release_to_npm: (experimental) Automatically release to npm when new versions are introduced. Default: false
        :param release_workflow: (deprecated) DEPRECATED: renamed to ``release``. Default: - true if not a subproject
        :param workflow_bootstrap_steps: (experimental) Workflow steps to use in order to bootstrap this repo. Default: "yarn install --frozen-lockfile && yarn projen"
        :param workflow_git_identity: (experimental) The git identity to use in workflows. Default: - GitHub Actions
        :param workflow_node_version: (experimental) The node version to use in GitHub workflows. Default: - same as ``minNodeVersion``
        :param disable_tsconfig: (experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler). Default: false
        :param docgen: (experimental) Docgen by Typedoc. Default: false
        :param docs_directory: (experimental) Docs directory. Default: "docs"
        :param entrypoint_types: (experimental) The .d.ts file that includes the type declarations for this module. Default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)
        :param eslint: (experimental) Setup eslint. Default: true
        :param eslint_options: (experimental) Eslint options. Default: - opinionated default options
        :param libdir: (experimental) Typescript artifacts output directory. Default: "lib"
        :param projenrc_ts: (experimental) Use TypeScript for your projenrc file (``.projenrc.ts``). Default: false
        :param projenrc_ts_options: (experimental) Options for .projenrc.ts.
        :param sample_code: (experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there. Default: true
        :param srcdir: (experimental) Typescript sources directory. Default: "src"
        :param testdir: (experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``. If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``), then tests are going to be compiled into ``lib/`` and executed as javascript. If the test directory is outside of ``src``, then we configure jest to compile the code in-memory. Default: "test"
        :param tsconfig: (experimental) Custom TSConfig. Default: - default options
        :param tsconfig_dev: (experimental) Custom tsconfig options for the development tsconfig.json file (used for testing). Default: - use the production tsconfig options
        :param tsconfig_dev_file: (experimental) The name of the development tsconfig.json file. Default: "tsconfig.dev.json"
        :param typescript_version: (experimental) TypeScript version to use. NOTE: Typescript is not semantically versioned and should remain on the same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``). Default: "latest"
        :param client_languages: (experimental) The list of languages for which clients will be generated. A typescript client will always be generated.
        :param api_src_dir: (experimental) The directory in which the api generated code will reside, relative to the project srcdir.
        :param documentation_formats: (experimental) Formats to generate documentation in.
        :param generated_code_dir: (experimental) The directory in which generated client code will be generated, relative to the outdir of this project. Default: "generated"
        :param java_client_options: (experimental) Options for the generated java client (if specified in clientLanguages). These override the default inferred options.
        :param parsed_spec_file_name: (experimental) The name of the output parsed OpenAPI specification file. Must end with .json. Default: ".parsed-spec.json"
        :param python_client_options: (experimental) Options for the generated python client (if specified in clientLanguages). These override the default inferred options.
        :param spec_file: (experimental) The path to the OpenAPI specification file, relative to the project source directory (srcdir). Default: "spec/spec.yaml"
        :param typescript_client_options: (experimental) Options for the generated typescript client. These override the default inferred options.

        :stability: experimental
        '''
        if isinstance(logging, dict):
            logging = projen.LoggerOptions(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = projen.ProjenrcOptions(**projenrc_json_options)
        if isinstance(renovatebot_options, dict):
            renovatebot_options = projen.RenovatebotOptions(**renovatebot_options)
        if isinstance(auto_approve_options, dict):
            auto_approve_options = projen.github.AutoApproveOptions(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = projen.github.AutoMergeOptions(**auto_merge_options)
        if isinstance(github_options, dict):
            github_options = projen.github.GitHubOptions(**github_options)
        if isinstance(mergify_options, dict):
            mergify_options = projen.github.MergifyOptions(**mergify_options)
        if isinstance(readme, dict):
            readme = projen.SampleReadmeProps(**readme)
        if isinstance(stale_options, dict):
            stale_options = projen.github.StaleOptions(**stale_options)
        if isinstance(code_artifact_options, dict):
            code_artifact_options = projen.javascript.CodeArtifactOptions(**code_artifact_options)
        if isinstance(peer_dependency_options, dict):
            peer_dependency_options = projen.javascript.PeerDependencyOptions(**peer_dependency_options)
        if isinstance(build_workflow_triggers, dict):
            build_workflow_triggers = projen.github.workflows.Triggers(**build_workflow_triggers)
        if isinstance(bundler_options, dict):
            bundler_options = projen.javascript.BundlerOptions(**bundler_options)
        if isinstance(dependabot_options, dict):
            dependabot_options = projen.github.DependabotOptions(**dependabot_options)
        if isinstance(deps_upgrade_options, dict):
            deps_upgrade_options = projen.javascript.UpgradeDependenciesOptions(**deps_upgrade_options)
        if isinstance(jest_options, dict):
            jest_options = projen.javascript.JestOptions(**jest_options)
        if isinstance(prettier_options, dict):
            prettier_options = projen.javascript.PrettierOptions(**prettier_options)
        if isinstance(projenrc_js_options, dict):
            projenrc_js_options = projen.javascript.ProjenrcOptions(**projenrc_js_options)
        if isinstance(workflow_git_identity, dict):
            workflow_git_identity = projen.github.GitIdentity(**workflow_git_identity)
        if isinstance(eslint_options, dict):
            eslint_options = projen.javascript.EslintOptions(**eslint_options)
        if isinstance(projenrc_ts_options, dict):
            projenrc_ts_options = projen.typescript.ProjenrcOptions(**projenrc_ts_options)
        if isinstance(tsconfig, dict):
            tsconfig = projen.javascript.TypescriptConfigOptions(**tsconfig)
        if isinstance(tsconfig_dev, dict):
            tsconfig_dev = projen.javascript.TypescriptConfigOptions(**tsconfig_dev)
        if isinstance(java_client_options, dict):
            java_client_options = projen.java.JavaProjectOptions(**java_client_options)
        if isinstance(python_client_options, dict):
            python_client_options = projen.python.PythonProjectOptions(**python_client_options)
        if isinstance(typescript_client_options, dict):
            typescript_client_options = projen.typescript.TypeScriptProjectOptions(**typescript_client_options)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "default_release_branch": default_release_branch,
            "client_languages": client_languages,
        }
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if renovatebot is not None:
            self._values["renovatebot"] = renovatebot
        if renovatebot_options is not None:
            self._values["renovatebot_options"] = renovatebot_options
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_merge is not None:
            self._values["auto_merge"] = auto_merge
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if clobber is not None:
            self._values["clobber"] = clobber
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_credentials is not None:
            self._values["projen_credentials"] = projen_credentials
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if readme is not None:
            self._values["readme"] = readme
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if vscode is not None:
            self._values["vscode"] = vscode
        if allow_library_dependencies is not None:
            self._values["allow_library_dependencies"] = allow_library_dependencies
        if author_email is not None:
            self._values["author_email"] = author_email
        if author_name is not None:
            self._values["author_name"] = author_name
        if author_organization is not None:
            self._values["author_organization"] = author_organization
        if author_url is not None:
            self._values["author_url"] = author_url
        if auto_detect_bin is not None:
            self._values["auto_detect_bin"] = auto_detect_bin
        if bin is not None:
            self._values["bin"] = bin
        if bugs_email is not None:
            self._values["bugs_email"] = bugs_email
        if bugs_url is not None:
            self._values["bugs_url"] = bugs_url
        if bundled_deps is not None:
            self._values["bundled_deps"] = bundled_deps
        if code_artifact_options is not None:
            self._values["code_artifact_options"] = code_artifact_options
        if deps is not None:
            self._values["deps"] = deps
        if description is not None:
            self._values["description"] = description
        if dev_deps is not None:
            self._values["dev_deps"] = dev_deps
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if homepage is not None:
            self._values["homepage"] = homepage
        if keywords is not None:
            self._values["keywords"] = keywords
        if license is not None:
            self._values["license"] = license
        if licensed is not None:
            self._values["licensed"] = licensed
        if max_node_version is not None:
            self._values["max_node_version"] = max_node_version
        if min_node_version is not None:
            self._values["min_node_version"] = min_node_version
        if npm_access is not None:
            self._values["npm_access"] = npm_access
        if npm_registry is not None:
            self._values["npm_registry"] = npm_registry
        if npm_registry_url is not None:
            self._values["npm_registry_url"] = npm_registry_url
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if package_manager is not None:
            self._values["package_manager"] = package_manager
        if package_name is not None:
            self._values["package_name"] = package_name
        if peer_dependency_options is not None:
            self._values["peer_dependency_options"] = peer_dependency_options
        if peer_deps is not None:
            self._values["peer_deps"] = peer_deps
        if repository is not None:
            self._values["repository"] = repository
        if repository_directory is not None:
            self._values["repository_directory"] = repository_directory
        if scoped_packages_options is not None:
            self._values["scoped_packages_options"] = scoped_packages_options
        if scripts is not None:
            self._values["scripts"] = scripts
        if stability is not None:
            self._values["stability"] = stability
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if major_version is not None:
            self._values["major_version"] = major_version
        if npm_dist_tag is not None:
            self._values["npm_dist_tag"] = npm_dist_tag
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if publish_dry_run is not None:
            self._values["publish_dry_run"] = publish_dry_run
        if publish_tasks is not None:
            self._values["publish_tasks"] = publish_tasks
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_failure_issue is not None:
            self._values["release_failure_issue"] = release_failure_issue
        if release_failure_issue_label is not None:
            self._values["release_failure_issue_label"] = release_failure_issue_label
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_tag_prefix is not None:
            self._values["release_tag_prefix"] = release_tag_prefix
        if release_trigger is not None:
            self._values["release_trigger"] = release_trigger
        if release_workflow_name is not None:
            self._values["release_workflow_name"] = release_workflow_name
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if versionrc_options is not None:
            self._values["versionrc_options"] = versionrc_options
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image
        if workflow_runs_on is not None:
            self._values["workflow_runs_on"] = workflow_runs_on
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if auto_approve_upgrades is not None:
            self._values["auto_approve_upgrades"] = auto_approve_upgrades
        if build_workflow is not None:
            self._values["build_workflow"] = build_workflow
        if build_workflow_triggers is not None:
            self._values["build_workflow_triggers"] = build_workflow_triggers
        if bundler_options is not None:
            self._values["bundler_options"] = bundler_options
        if code_cov is not None:
            self._values["code_cov"] = code_cov
        if code_cov_token_secret is not None:
            self._values["code_cov_token_secret"] = code_cov_token_secret
        if copyright_owner is not None:
            self._values["copyright_owner"] = copyright_owner
        if copyright_period is not None:
            self._values["copyright_period"] = copyright_period
        if dependabot is not None:
            self._values["dependabot"] = dependabot
        if dependabot_options is not None:
            self._values["dependabot_options"] = dependabot_options
        if deps_upgrade is not None:
            self._values["deps_upgrade"] = deps_upgrade
        if deps_upgrade_options is not None:
            self._values["deps_upgrade_options"] = deps_upgrade_options
        if gitignore is not None:
            self._values["gitignore"] = gitignore
        if jest is not None:
            self._values["jest"] = jest
        if jest_options is not None:
            self._values["jest_options"] = jest_options
        if mutable_build is not None:
            self._values["mutable_build"] = mutable_build
        if npmignore is not None:
            self._values["npmignore"] = npmignore
        if npmignore_enabled is not None:
            self._values["npmignore_enabled"] = npmignore_enabled
        if package is not None:
            self._values["package"] = package
        if prettier is not None:
            self._values["prettier"] = prettier
        if prettier_options is not None:
            self._values["prettier_options"] = prettier_options
        if projen_dev_dependency is not None:
            self._values["projen_dev_dependency"] = projen_dev_dependency
        if projenrc_js is not None:
            self._values["projenrc_js"] = projenrc_js
        if projenrc_js_options is not None:
            self._values["projenrc_js_options"] = projenrc_js_options
        if projen_version is not None:
            self._values["projen_version"] = projen_version
        if pull_request_template is not None:
            self._values["pull_request_template"] = pull_request_template
        if pull_request_template_contents is not None:
            self._values["pull_request_template_contents"] = pull_request_template_contents
        if release is not None:
            self._values["release"] = release
        if release_to_npm is not None:
            self._values["release_to_npm"] = release_to_npm
        if release_workflow is not None:
            self._values["release_workflow"] = release_workflow
        if workflow_bootstrap_steps is not None:
            self._values["workflow_bootstrap_steps"] = workflow_bootstrap_steps
        if workflow_git_identity is not None:
            self._values["workflow_git_identity"] = workflow_git_identity
        if workflow_node_version is not None:
            self._values["workflow_node_version"] = workflow_node_version
        if disable_tsconfig is not None:
            self._values["disable_tsconfig"] = disable_tsconfig
        if docgen is not None:
            self._values["docgen"] = docgen
        if docs_directory is not None:
            self._values["docs_directory"] = docs_directory
        if entrypoint_types is not None:
            self._values["entrypoint_types"] = entrypoint_types
        if eslint is not None:
            self._values["eslint"] = eslint
        if eslint_options is not None:
            self._values["eslint_options"] = eslint_options
        if libdir is not None:
            self._values["libdir"] = libdir
        if projenrc_ts is not None:
            self._values["projenrc_ts"] = projenrc_ts
        if projenrc_ts_options is not None:
            self._values["projenrc_ts_options"] = projenrc_ts_options
        if sample_code is not None:
            self._values["sample_code"] = sample_code
        if srcdir is not None:
            self._values["srcdir"] = srcdir
        if testdir is not None:
            self._values["testdir"] = testdir
        if tsconfig is not None:
            self._values["tsconfig"] = tsconfig
        if tsconfig_dev is not None:
            self._values["tsconfig_dev"] = tsconfig_dev
        if tsconfig_dev_file is not None:
            self._values["tsconfig_dev_file"] = tsconfig_dev_file
        if typescript_version is not None:
            self._values["typescript_version"] = typescript_version
        if api_src_dir is not None:
            self._values["api_src_dir"] = api_src_dir
        if documentation_formats is not None:
            self._values["documentation_formats"] = documentation_formats
        if generated_code_dir is not None:
            self._values["generated_code_dir"] = generated_code_dir
        if java_client_options is not None:
            self._values["java_client_options"] = java_client_options
        if parsed_spec_file_name is not None:
            self._values["parsed_spec_file_name"] = parsed_spec_file_name
        if python_client_options is not None:
            self._values["python_client_options"] = python_client_options
        if spec_file is not None:
            self._values["spec_file"] = spec_file
        if typescript_client_options is not None:
            self._values["typescript_client_options"] = typescript_client_options

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logging(self) -> typing.Optional[projen.LoggerOptions]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[projen.LoggerOptions], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[projen.Project]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[projen.Project], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(self) -> typing.Optional[projen.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[projen.ProjenrcOptions], result)

    @builtins.property
    def renovatebot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use renovatebot to handle dependency upgrades.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("renovatebot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def renovatebot_options(self) -> typing.Optional[projen.RenovatebotOptions]:
        '''(experimental) Options for renovatebot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("renovatebot_options")
        return typing.cast(typing.Optional[projen.RenovatebotOptions], result)

    @builtins.property
    def auto_approve_options(self) -> typing.Optional[projen.github.AutoApproveOptions]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[projen.github.AutoApproveOptions], result)

    @builtins.property
    def auto_merge(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable automatic merging on GitHub.

        Has no effect if ``github.mergify``
        is set to false.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_merge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_merge_options(self) -> typing.Optional[projen.github.AutoMergeOptions]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` or ``autoMerge`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[projen.github.AutoMergeOptions], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[projen.github.GitHubOptions]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[projen.github.GitHubOptions], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(self) -> typing.Optional[projen.github.MergifyOptions]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[projen.github.MergifyOptions], result)

    @builtins.property
    def project_type(self) -> typing.Optional[projen.ProjectType]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[projen.ProjectType], result)

    @builtins.property
    def projen_credentials(self) -> typing.Optional[projen.github.GithubCredentials]:
        '''(experimental) Choose a method of providing GitHub API access for projen workflows.

        :default: - use a personal access token named PROJEN_GITHUB_TOKEN

        :stability: experimental
        '''
        result = self._values.get("projen_credentials")
        return typing.cast(typing.Optional[projen.github.GithubCredentials], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :deprecated: use ``projenCredentials``

        :stability: deprecated
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme(self) -> typing.Optional[projen.SampleReadmeProps]:
        '''(experimental) The README setup.

        :default: - { filename: 'README.md', contents: '# replace this' }

        :stability: experimental

        Example::

            "{ filename: 'readme.md', contents: '# title' }"
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[projen.SampleReadmeProps], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[projen.github.StaleOptions]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[projen.github.StaleOptions], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_library_dependencies(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Allow the project to include ``peerDependencies`` and ``bundledDependencies``.

        This is normally only allowed for libraries. For apps, there's no meaning
        for specifying these.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("allow_library_dependencies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's e-mail.

        :stability: experimental
        '''
        result = self._values.get("author_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's name.

        :stability: experimental
        '''
        result = self._values.get("author_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def author_organization(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Author's Organization.

        :stability: experimental
        '''
        result = self._values.get("author_organization")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def author_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Author's URL / Website.

        :stability: experimental
        '''
        result = self._values.get("author_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_detect_bin(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically add all executables under the ``bin`` directory to your ``package.json`` file under the ``bin`` section.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_detect_bin")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bin(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Binary programs vended with your module.

        You can use this option to add/customize how binaries are represented in
        your ``package.json``, but unless ``autoDetectBin`` is ``false``, every
        executable file under ``bin`` will automatically be added to this section.

        :stability: experimental
        '''
        result = self._values.get("bin")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def bugs_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) The email address to which issues should be reported.

        :stability: experimental
        '''
        result = self._values.get("bugs_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bugs_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The url to your project's issue tracker.

        :stability: experimental
        '''
        result = self._values.get("bugs_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bundled_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of dependencies to bundle into this module.

        These modules will be
        added both to the ``dependencies`` section and ``bundledDependencies`` section of
        your ``package.json``.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :stability: experimental
        '''
        result = self._values.get("bundled_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def code_artifact_options(
        self,
    ) -> typing.Optional[projen.javascript.CodeArtifactOptions]:
        '''(experimental) Options for npm packages using AWS CodeArtifact.

        This is required if publishing packages to, or installing scoped packages from AWS CodeArtifact

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("code_artifact_options")
        return typing.cast(typing.Optional[projen.javascript.CodeArtifactOptions], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Runtime dependencies of this module.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true

        Example::

            [ 'express', 'lodash', 'foo@^2' ]
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description is just a string that helps people understand the purpose of the package.

        It can be used when searching for packages in a package manager as well.
        See https://classic.yarnpkg.com/en/docs/package-json/#toc-description

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dev_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Build dependencies for this module.

        These dependencies will only be
        available in your build environment but will not be fetched when this
        module is consumed.

        The recommendation is to only specify the module name here (e.g.
        ``express``). This will behave similar to ``yarn add`` or ``npm install`` in the
        sense that it will add the module as a dependency to your ``package.json``
        file with the latest version (``^``). You can specify semver requirements in
        the same syntax passed to ``npm i`` or ``yarn add`` (e.g. ``express@^2``) and
        this will be what you ``package.json`` will eventually include.

        :default: []

        :stability: experimental
        :featured: true

        Example::

            [ 'typescript', '@types/express' ]
        '''
        result = self._values.get("dev_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) Module entrypoint (``main`` in ``package.json``).

        Set to an empty string to not include ``main`` in your package.json

        :default: "lib/index.js"

        :stability: experimental
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Homepage / Website.

        :stability: experimental
        '''
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keywords(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Keywords to include in ``package.json``.

        :stability: experimental
        '''
        result = self._values.get("keywords")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''(experimental) License's SPDX identifier.

        See https://github.com/projen/projen/tree/main/license-text for a list of supported licenses.
        Use the ``licensed`` option if you want to no license to be specified.

        :default: "Apache-2.0"

        :stability: experimental
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def licensed(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates if a license should be added.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("licensed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def max_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum node.js version to require via ``engines`` (inclusive).

        :default: - no max

        :stability: experimental
        '''
        result = self._values.get("max_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Minimum Node.js version to require via package.json ``engines`` (inclusive).

        :default: - no "engines" specified

        :stability: experimental
        '''
        result = self._values.get("min_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_access(self) -> typing.Optional[projen.javascript.NpmAccess]:
        '''(experimental) Access level of the npm package.

        :default:

        - for scoped packages (e.g. ``foo@bar``), the default is
        ``NpmAccess.RESTRICTED``, for non-scoped packages, the default is
        ``NpmAccess.PUBLIC``.

        :stability: experimental
        '''
        result = self._values.get("npm_access")
        return typing.cast(typing.Optional[projen.javascript.NpmAccess], result)

    @builtins.property
    def npm_registry(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The host name of the npm registry to publish to.

        Cannot be set together with ``npmRegistryUrl``.

        :deprecated: use ``npmRegistryUrl`` instead

        :stability: deprecated
        '''
        result = self._values.get("npm_registry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The base URL of the npm package registry.

        Must be a URL (e.g. start with "https://" or "http://")

        :default: "https://registry.npmjs.org"

        :stability: experimental
        '''
        result = self._values.get("npm_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: "NPM_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package_manager(self) -> typing.Optional[projen.javascript.NodePackageManager]:
        '''(experimental) The Node Package Manager used to execute scripts.

        :default: NodePackageManager.YARN

        :stability: experimental
        '''
        result = self._values.get("package_manager")
        return typing.cast(typing.Optional[projen.javascript.NodePackageManager], result)

    @builtins.property
    def package_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The "name" in package.json.

        :default: - defaults to project name

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("package_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer_dependency_options(
        self,
    ) -> typing.Optional[projen.javascript.PeerDependencyOptions]:
        '''(experimental) Options for ``peerDeps``.

        :stability: experimental
        '''
        result = self._values.get("peer_dependency_options")
        return typing.cast(typing.Optional[projen.javascript.PeerDependencyOptions], result)

    @builtins.property
    def peer_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Peer dependencies for this module.

        Dependencies listed here are required to
        be installed (and satisfied) by the *consumer* of this library. Using peer
        dependencies allows you to ensure that only a single module of a certain
        library exists in the ``node_modules`` tree of your consumers.

        Note that prior to npm@7, peer dependencies are *not* automatically
        installed, which means that adding peer dependencies to a library will be a
        breaking change for your customers.

        Unless ``peerDependencyOptions.pinnedDevDependency`` is disabled (it is
        enabled by default), projen will automatically add a dev dependency with a
        pinned version for each peer dependency. This will ensure that you build &
        test your module against the lowest peer version required.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("peer_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository is the location where the actual code for your package lives.

        See https://classic.yarnpkg.com/en/docs/package-json/#toc-repository

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) If the package.json for your package is not in the root directory (for example if it is part of a monorepo), you can specify the directory in which it lives.

        :stability: experimental
        '''
        result = self._values.get("repository_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scoped_packages_options(
        self,
    ) -> typing.Optional[typing.List[projen.javascript.ScopedPackagesOptions]]:
        '''(experimental) Options for privately hosted scoped packages.

        :default: - fetch all scoped packages from the public npm registry

        :stability: experimental
        '''
        result = self._values.get("scoped_packages_options")
        return typing.cast(typing.Optional[typing.List[projen.javascript.ScopedPackagesOptions]], result)

    @builtins.property
    def scripts(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) npm scripts to include.

        If a script has the same name as a standard script,
        the standard script will be overwritten.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("scripts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def stability(self) -> typing.Optional[builtins.str]:
        '''(experimental) Package's Stability.

        :stability: experimental
        '''
        result = self._values.get("stability")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``publib`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Major version to release from the default branch.

        If this is specified, we bump the latest version of this major version line.
        If not specified, we bump the global latest version.

        :default: - Major version is not enforced.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def npm_dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The npmDistTag to use when publishing from the default branch.

        To set the npm dist-tag for release branches, set the ``npmDistTag`` property
        for each branch.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("npm_dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_build_steps(
        self,
    ) -> typing.Optional[typing.List[projen.github.workflows.JobStep]]:
        '''(experimental) Steps to execute after build as part of the release workflow.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[projen.github.workflows.JobStep]], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre").

        :default: - normal semantic versions

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_dry_run(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Instead of actually publishing to package managers, just print the publishing command.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_tasks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define publishing tasks that can be executed manually as well as workflows.

        Normally, publishing only happens within automated workflows. Enable this
        in order to create a publishing task for each publishing activity.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_branches(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]]:
        '''(experimental) Defines additional release branches.

        A workflow will be created for each
        release branch which will publish releases from commits in this branch.
        Each release branch *must* be assigned a major version number which is used
        to enforce that versions published from that branch always use that major
        version. If multiple branches are used, the ``majorVersion`` field must also
        be provided for the default branch.

        :default:

        - no additional branches are used for release. you can use
        ``addBranch()`` to add additional branches.

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, projen.release.BranchOptions]], result)

    @builtins.property
    def release_every_commit(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``.

        :default: true

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.continuous()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_every_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create a github issue on every failed publishing task.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to issues indicating publish failures.

        Only applies if ``releaseFailureIssue`` is true.

        :default: "failed-release"

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_schedule(self) -> typing.Optional[builtins.str]:
        '''(deprecated) CRON schedule to trigger new releases.

        :default: - no scheduled releases

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.scheduled()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_tag_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers.

        Note: this prefix is used to detect the latest tagged version
        when bumping, so if you change this on a project with an existing version
        history, you may need to manually tag your latest release
        with the new prefix.

        :default: - no prefix

        :stability: experimental
        '''
        result = self._values.get("release_tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_trigger(self) -> typing.Optional[projen.release.ReleaseTrigger]:
        '''(experimental) The release trigger to use.

        :default: - Continuous releases (``ReleaseTrigger.continuous()``)

        :stability: experimental
        '''
        result = self._values.get("release_trigger")
        return typing.cast(typing.Optional[projen.release.ReleaseTrigger], result)

    @builtins.property
    def release_workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the default release workflow.

        :default: "Release"

        :stability: experimental
        '''
        result = self._values.get("release_workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_setup_steps(
        self,
    ) -> typing.Optional[typing.List[projen.github.workflows.JobStep]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[projen.github.workflows.JobStep]], result)

    @builtins.property
    def versionrc_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Custom configuration used when creating changelog with standard-version package.

        Given values either append to default configuration or overwrite values in it.

        :default: - standard configuration applicable for GitHub repositories

        :stability: experimental
        '''
        result = self._values.get("versionrc_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("workflow_runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_release_branch(self) -> builtins.str:
        '''(experimental) The name of the main release branch.

        :default: "main"

        :stability: experimental
        '''
        result = self._values.get("default_release_branch")
        assert result is not None, "Required property 'default_release_branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory which will contain build artifacts.

        :default: "dist"

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_approve_upgrades(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically approve deps upgrade PRs, allowing them to be merged by mergify (if configued).

        Throw if set to true but ``autoApproveOptions`` are not defined.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("auto_approve_upgrades")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_workflow(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow for building PRs.

        :default: - true if not a subproject

        :stability: experimental
        '''
        result = self._values.get("build_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_workflow_triggers(
        self,
    ) -> typing.Optional[projen.github.workflows.Triggers]:
        '''(experimental) Build workflow triggers.

        :default: "{ pullRequest: {}, workflowDispatch: {} }"

        :stability: experimental
        '''
        result = self._values.get("build_workflow_triggers")
        return typing.cast(typing.Optional[projen.github.workflows.Triggers], result)

    @builtins.property
    def bundler_options(self) -> typing.Optional[projen.javascript.BundlerOptions]:
        '''(experimental) Options for ``Bundler``.

        :stability: experimental
        '''
        result = self._values.get("bundler_options")
        return typing.cast(typing.Optional[projen.javascript.BundlerOptions], result)

    @builtins.property
    def code_cov(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define a GitHub workflow step for sending code coverage metrics to https://codecov.io/ Uses codecov/codecov-action@v1 A secret is required for private repos. Configured with @codeCovTokenSecret.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("code_cov")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def code_cov_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) Define the secret name for a specified https://codecov.io/ token A secret is required to send coverage for private repositories.

        :default: - if this option is not specified, only public repositories are supported

        :stability: experimental
        '''
        result = self._values.get("code_cov_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_owner(self) -> typing.Optional[builtins.str]:
        '''(experimental) License copyright owner.

        :default: - defaults to the value of authorName or "" if ``authorName`` is undefined.

        :stability: experimental
        '''
        result = self._values.get("copyright_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copyright_period(self) -> typing.Optional[builtins.str]:
        '''(experimental) The copyright years to put in the LICENSE file.

        :default: - current year

        :stability: experimental
        '''
        result = self._values.get("copyright_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependabot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use dependabot to handle dependency upgrades.

        Cannot be used in conjunction with ``depsUpgrade``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dependabot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dependabot_options(self) -> typing.Optional[projen.github.DependabotOptions]:
        '''(experimental) Options for dependabot.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("dependabot_options")
        return typing.cast(typing.Optional[projen.github.DependabotOptions], result)

    @builtins.property
    def deps_upgrade(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use github workflows to handle dependency upgrades.

        Cannot be used in conjunction with ``dependabot``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deps_upgrade_options(
        self,
    ) -> typing.Optional[projen.javascript.UpgradeDependenciesOptions]:
        '''(experimental) Options for ``UpgradeDependencies``.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("deps_upgrade_options")
        return typing.cast(typing.Optional[projen.javascript.UpgradeDependenciesOptions], result)

    @builtins.property
    def gitignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional entries to .gitignore.

        :stability: experimental
        '''
        result = self._values.get("gitignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup jest unit tests.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("jest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def jest_options(self) -> typing.Optional[projen.javascript.JestOptions]:
        '''(experimental) Jest options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("jest_options")
        return typing.cast(typing.Optional[projen.javascript.JestOptions], result)

    @builtins.property
    def mutable_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically update files modified during builds to pull-request branches.

        This means
        that any files synthesized by projen or e.g. test snapshots will always be up-to-date
        before a PR is merged.

        Implies that PR builds do not have anti-tamper checks.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("mutable_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def npmignore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) Additional entries to .npmignore.

        :deprecated: - use ``project.addPackageIgnore``

        :stability: deprecated
        '''
        result = self._values.get("npmignore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def npmignore_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines an .npmignore file. Normally this is only needed for libraries that are packaged as tarballs.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("npmignore_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def package(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Defines a ``package`` task that will produce an npm tarball under the artifacts directory (e.g. ``dist``).

        :default: true

        :stability: experimental
        '''
        result = self._values.get("package")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prettier(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup prettier.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("prettier")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prettier_options(self) -> typing.Optional[projen.javascript.PrettierOptions]:
        '''(experimental) Prettier options.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("prettier_options")
        return typing.cast(typing.Optional[projen.javascript.PrettierOptions], result)

    @builtins.property
    def projen_dev_dependency(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates of "projen" should be installed as a devDependency.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projen_dev_dependency")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.js (in JavaScript). Set to ``false`` in order to disable .projenrc.js generation.

        :default: - true if projenrcJson is false

        :stability: experimental
        '''
        result = self._values.get("projenrc_js")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_js_options(self) -> typing.Optional[projen.javascript.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.js.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_js_options")
        return typing.cast(typing.Optional[projen.javascript.ProjenrcOptions], result)

    @builtins.property
    def projen_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of projen to install.

        :default: - Defaults to the latest version.

        :stability: experimental
        '''
        result = self._values.get("projen_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_template(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include a GitHub pull request template.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_template_contents(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The contents of the pull request template.

        :default: - default content

        :stability: experimental
        '''
        result = self._values.get("pull_request_template_contents")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def release(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add release management to this project.

        :default: - true (false for subprojects)

        :stability: experimental
        '''
        result = self._values.get("release")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_to_npm(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically release to npm when new versions are introduced.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_to_npm")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_workflow(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) DEPRECATED: renamed to ``release``.

        :default: - true if not a subproject

        :deprecated: see ``release``.

        :stability: deprecated
        '''
        result = self._values.get("release_workflow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflow_bootstrap_steps(
        self,
    ) -> typing.Optional[typing.List[projen.github.workflows.JobStep]]:
        '''(experimental) Workflow steps to use in order to bootstrap this repo.

        :default: "yarn install --frozen-lockfile && yarn projen"

        :stability: experimental
        '''
        result = self._values.get("workflow_bootstrap_steps")
        return typing.cast(typing.Optional[typing.List[projen.github.workflows.JobStep]], result)

    @builtins.property
    def workflow_git_identity(self) -> typing.Optional[projen.github.GitIdentity]:
        '''(experimental) The git identity to use in workflows.

        :default: - GitHub Actions

        :stability: experimental
        '''
        result = self._values.get("workflow_git_identity")
        return typing.cast(typing.Optional[projen.github.GitIdentity], result)

    @builtins.property
    def workflow_node_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The node version to use in GitHub workflows.

        :default: - same as ``minNodeVersion``

        :stability: experimental
        '''
        result = self._values.get("workflow_node_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_tsconfig(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not generate a ``tsconfig.json`` file (used by jsii projects since tsconfig.json is generated by the jsii compiler).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("disable_tsconfig")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docgen(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Docgen by Typedoc.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("docgen")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def docs_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docs directory.

        :default: "docs"

        :stability: experimental
        '''
        result = self._values.get("docs_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint_types(self) -> typing.Optional[builtins.str]:
        '''(experimental) The .d.ts file that includes the type declarations for this module.

        :default: - .d.ts file derived from the project's entrypoint (usually lib/index.d.ts)

        :stability: experimental
        '''
        result = self._values.get("entrypoint_types")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eslint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setup eslint.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("eslint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def eslint_options(self) -> typing.Optional[projen.javascript.EslintOptions]:
        '''(experimental) Eslint options.

        :default: - opinionated default options

        :stability: experimental
        '''
        result = self._values.get("eslint_options")
        return typing.cast(typing.Optional[projen.javascript.EslintOptions], result)

    @builtins.property
    def libdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript  artifacts output directory.

        :default: "lib"

        :stability: experimental
        '''
        result = self._values.get("libdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_ts(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use TypeScript for your projenrc file (``.projenrc.ts``).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_ts_options(self) -> typing.Optional[projen.typescript.ProjenrcOptions]:
        '''(experimental) Options for .projenrc.ts.

        :stability: experimental
        '''
        result = self._values.get("projenrc_ts_options")
        return typing.cast(typing.Optional[projen.typescript.ProjenrcOptions], result)

    @builtins.property
    def sample_code(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate one-time sample in ``src/`` and ``test/`` if there are no files there.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("sample_code")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def srcdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Typescript sources directory.

        :default: "src"

        :stability: experimental
        '''
        result = self._values.get("srcdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def testdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Jest tests directory. Tests files should be named ``xxx.test.ts``.

        If this directory is under ``srcdir`` (e.g. ``src/test``, ``src/__tests__``),
        then tests are going to be compiled into ``lib/`` and executed as javascript.
        If the test directory is outside of ``src``, then we configure jest to
        compile the code in-memory.

        :default: "test"

        :stability: experimental
        '''
        result = self._values.get("testdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tsconfig(self) -> typing.Optional[projen.javascript.TypescriptConfigOptions]:
        '''(experimental) Custom TSConfig.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("tsconfig")
        return typing.cast(typing.Optional[projen.javascript.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev(
        self,
    ) -> typing.Optional[projen.javascript.TypescriptConfigOptions]:
        '''(experimental) Custom tsconfig options for the development tsconfig.json file (used for testing).

        :default: - use the production tsconfig options

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev")
        return typing.cast(typing.Optional[projen.javascript.TypescriptConfigOptions], result)

    @builtins.property
    def tsconfig_dev_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the development tsconfig.json file.

        :default: "tsconfig.dev.json"

        :stability: experimental
        '''
        result = self._values.get("tsconfig_dev_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def typescript_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) TypeScript version to use.

        NOTE: Typescript is not semantically versioned and should remain on the
        same minor, so we recommend using a ``~`` dependency (e.g. ``~1.2.3``).

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("typescript_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_languages(self) -> typing.List[ClientLanguage]:
        '''(experimental) The list of languages for which clients will be generated.

        A typescript client will always be generated.

        :stability: experimental
        '''
        result = self._values.get("client_languages")
        assert result is not None, "Required property 'client_languages' is missing"
        return typing.cast(typing.List[ClientLanguage], result)

    @builtins.property
    def api_src_dir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The directory in which the api generated code will reside, relative to the project srcdir.

        :stability: experimental
        '''
        result = self._values.get("api_src_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def documentation_formats(
        self,
    ) -> typing.Optional[typing.List[DocumentationFormat]]:
        '''(experimental) Formats to generate documentation in.

        :stability: experimental
        '''
        result = self._values.get("documentation_formats")
        return typing.cast(typing.Optional[typing.List[DocumentationFormat]], result)

    @builtins.property
    def generated_code_dir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The directory in which generated client code will be generated, relative to the outdir of this project.

        :default: "generated"

        :stability: experimental
        '''
        result = self._values.get("generated_code_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def java_client_options(self) -> typing.Optional[projen.java.JavaProjectOptions]:
        '''(experimental) Options for the generated java client (if specified in clientLanguages).

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("java_client_options")
        return typing.cast(typing.Optional[projen.java.JavaProjectOptions], result)

    @builtins.property
    def parsed_spec_file_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the output parsed OpenAPI specification file.

        Must end with .json.

        :default: ".parsed-spec.json"

        :stability: experimental
        '''
        result = self._values.get("parsed_spec_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def python_client_options(
        self,
    ) -> typing.Optional[projen.python.PythonProjectOptions]:
        '''(experimental) Options for the generated python client (if specified in clientLanguages).

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("python_client_options")
        return typing.cast(typing.Optional[projen.python.PythonProjectOptions], result)

    @builtins.property
    def spec_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The path to the OpenAPI specification file, relative to the project source directory (srcdir).

        :default: "spec/spec.yaml"

        :stability: experimental
        '''
        result = self._values.get("spec_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def typescript_client_options(
        self,
    ) -> typing.Optional[projen.typescript.TypeScriptProjectOptions]:
        '''(experimental) Options for the generated typescript client.

        These override the default inferred options.

        :stability: experimental
        '''
        result = self._values.get("typescript_client_options")
        return typing.cast(typing.Optional[projen.typescript.TypeScriptProjectOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenApiGatewayTsProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/open-api-gateway.OpenApiIntegration",
    jsii_struct_bases=[],
    name_mapping={"function": "function", "authorizer": "authorizer"},
)
class OpenApiIntegration:
    def __init__(
        self,
        *,
        function: aws_cdk.aws_lambda.IFunction,
        authorizer: typing.Optional[Authorizer] = None,
    ) -> None:
        '''(experimental) Defines an integration for an individual API operation.

        :param function: (experimental) The lambda function to service the api operation.
        :param authorizer: (experimental) The authorizer to use for this api operation (overrides the default).

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "function": function,
        }
        if authorizer is not None:
            self._values["authorizer"] = authorizer

    @builtins.property
    def function(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) The lambda function to service the api operation.

        :stability: experimental
        '''
        result = self._values.get("function")
        assert result is not None, "Required property 'function' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    @builtins.property
    def authorizer(self) -> typing.Optional[Authorizer]:
        '''(experimental) The authorizer to use for this api operation (overrides the default).

        :stability: experimental
        '''
        result = self._values.get("authorizer")
        return typing.cast(typing.Optional[Authorizer], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenApiIntegration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/open-api-gateway.OpenApiOptions",
    jsii_struct_bases=[],
    name_mapping={
        "integrations": "integrations",
        "operation_lookup": "operationLookup",
        "cors_options": "corsOptions",
        "default_authorizer": "defaultAuthorizer",
    },
)
class OpenApiOptions:
    def __init__(
        self,
        *,
        integrations: typing.Mapping[builtins.str, OpenApiIntegration],
        operation_lookup: typing.Mapping[builtins.str, MethodAndPath],
        cors_options: typing.Optional[aws_cdk.aws_apigateway.CorsOptions] = None,
        default_authorizer: typing.Optional[Authorizer] = None,
    ) -> None:
        '''(experimental) Options required alongside an Open API specification to create API Gateway resources.

        :param integrations: (experimental) A mapping of API operation to its integration.
        :param operation_lookup: (experimental) Details about each operation.
        :param cors_options: (experimental) Cross Origin Resource Sharing options for the API.
        :param default_authorizer: (experimental) The default authorizer to use for your api. When omitted, no authorizer is used. Authorizers specified at the integration level will override this for that operation.

        :stability: experimental
        '''
        if isinstance(cors_options, dict):
            cors_options = aws_cdk.aws_apigateway.CorsOptions(**cors_options)
        self._values: typing.Dict[str, typing.Any] = {
            "integrations": integrations,
            "operation_lookup": operation_lookup,
        }
        if cors_options is not None:
            self._values["cors_options"] = cors_options
        if default_authorizer is not None:
            self._values["default_authorizer"] = default_authorizer

    @builtins.property
    def integrations(self) -> typing.Mapping[builtins.str, OpenApiIntegration]:
        '''(experimental) A mapping of API operation to its integration.

        :stability: experimental
        '''
        result = self._values.get("integrations")
        assert result is not None, "Required property 'integrations' is missing"
        return typing.cast(typing.Mapping[builtins.str, OpenApiIntegration], result)

    @builtins.property
    def operation_lookup(self) -> typing.Mapping[builtins.str, MethodAndPath]:
        '''(experimental) Details about each operation.

        :stability: experimental
        '''
        result = self._values.get("operation_lookup")
        assert result is not None, "Required property 'operation_lookup' is missing"
        return typing.cast(typing.Mapping[builtins.str, MethodAndPath], result)

    @builtins.property
    def cors_options(self) -> typing.Optional[aws_cdk.aws_apigateway.CorsOptions]:
        '''(experimental) Cross Origin Resource Sharing options for the API.

        :stability: experimental
        '''
        result = self._values.get("cors_options")
        return typing.cast(typing.Optional[aws_cdk.aws_apigateway.CorsOptions], result)

    @builtins.property
    def default_authorizer(self) -> typing.Optional[Authorizer]:
        '''(experimental) The default authorizer to use for your api.

        When omitted, no authorizer is used.
        Authorizers specified at the integration level will override this for that operation.

        :stability: experimental
        '''
        result = self._values.get("default_authorizer")
        return typing.cast(typing.Optional[Authorizer], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenApiOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-prototyping-sdk/open-api-gateway.OpenApiGatewayLambdaApiProps",
    jsii_struct_bases=[aws_cdk.aws_apigateway.RestApiBaseProps, OpenApiOptions],
    name_mapping={
        "cloud_watch_role": "cloudWatchRole",
        "deploy": "deploy",
        "deploy_options": "deployOptions",
        "disable_execute_api_endpoint": "disableExecuteApiEndpoint",
        "domain_name": "domainName",
        "endpoint_export_name": "endpointExportName",
        "endpoint_types": "endpointTypes",
        "fail_on_warnings": "failOnWarnings",
        "parameters": "parameters",
        "policy": "policy",
        "rest_api_name": "restApiName",
        "retain_deployments": "retainDeployments",
        "integrations": "integrations",
        "operation_lookup": "operationLookup",
        "cors_options": "corsOptions",
        "default_authorizer": "defaultAuthorizer",
        "spec": "spec",
    },
)
class OpenApiGatewayLambdaApiProps(
    aws_cdk.aws_apigateway.RestApiBaseProps,
    OpenApiOptions,
):
    def __init__(
        self,
        *,
        cloud_watch_role: typing.Optional[builtins.bool] = None,
        deploy: typing.Optional[builtins.bool] = None,
        deploy_options: typing.Optional[aws_cdk.aws_apigateway.StageOptions] = None,
        disable_execute_api_endpoint: typing.Optional[builtins.bool] = None,
        domain_name: typing.Optional[aws_cdk.aws_apigateway.DomainNameOptions] = None,
        endpoint_export_name: typing.Optional[builtins.str] = None,
        endpoint_types: typing.Optional[typing.Sequence[aws_cdk.aws_apigateway.EndpointType]] = None,
        fail_on_warnings: typing.Optional[builtins.bool] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        policy: typing.Optional[aws_cdk.aws_iam.PolicyDocument] = None,
        rest_api_name: typing.Optional[builtins.str] = None,
        retain_deployments: typing.Optional[builtins.bool] = None,
        integrations: typing.Mapping[builtins.str, OpenApiIntegration],
        operation_lookup: typing.Mapping[builtins.str, MethodAndPath],
        cors_options: typing.Optional[aws_cdk.aws_apigateway.CorsOptions] = None,
        default_authorizer: typing.Optional[Authorizer] = None,
        spec: typing.Any,
    ) -> None:
        '''(experimental) Configuration for the OpenApiGatewayLambdaApi construct.

        :param cloud_watch_role: Automatically configure an AWS CloudWatch role for API Gateway. Default: true
        :param deploy: Indicates if a Deployment should be automatically created for this API, and recreated when the API model (resources, methods) changes. Since API Gateway deployments are immutable, When this option is enabled (by default), an AWS::ApiGateway::Deployment resource will automatically created with a logical ID that hashes the API model (methods, resources and options). This means that when the model changes, the logical ID of this CloudFormation resource will change, and a new deployment will be created. If this is set, ``latestDeployment`` will refer to the ``Deployment`` object and ``deploymentStage`` will refer to a ``Stage`` that points to this deployment. To customize the stage options, use the ``deployOptions`` property. A CloudFormation Output will also be defined with the root URL endpoint of this REST API. Default: true
        :param deploy_options: Options for the API Gateway stage that will always point to the latest deployment when ``deploy`` is enabled. If ``deploy`` is disabled, this value cannot be set. Default: - Based on defaults of ``StageOptions``.
        :param disable_execute_api_endpoint: Specifies whether clients can invoke the API using the default execute-api endpoint. To require that clients use a custom domain name to invoke the API, disable the default endpoint. Default: false
        :param domain_name: Configure a custom domain name and map it to this API. Default: - no domain name is defined, use ``addDomainName`` or directly define a ``DomainName``.
        :param endpoint_export_name: Export name for the CfnOutput containing the API endpoint. Default: - when no export name is given, output will be created without export
        :param endpoint_types: A list of the endpoint types of the API. Use this property when creating an API. Default: EndpointType.EDGE
        :param fail_on_warnings: Indicates whether to roll back the resource if a warning occurs while API Gateway is creating the RestApi resource. Default: false
        :param parameters: Custom header parameters for the request. Default: - No parameters.
        :param policy: A policy document that contains the permissions for this RestApi. Default: - No policy.
        :param rest_api_name: A name for the API Gateway RestApi resource. Default: - ID of the RestApi construct.
        :param retain_deployments: Retains old deployment resources when the API changes. This allows manually reverting stages to point to old deployments via the AWS Console. Default: false
        :param integrations: (experimental) A mapping of API operation to its integration.
        :param operation_lookup: (experimental) Details about each operation.
        :param cors_options: (experimental) Cross Origin Resource Sharing options for the API.
        :param default_authorizer: (experimental) The default authorizer to use for your api. When omitted, no authorizer is used. Authorizers specified at the integration level will override this for that operation.
        :param spec: (experimental) The parsed OpenAPI specification.

        :stability: experimental
        '''
        if isinstance(deploy_options, dict):
            deploy_options = aws_cdk.aws_apigateway.StageOptions(**deploy_options)
        if isinstance(domain_name, dict):
            domain_name = aws_cdk.aws_apigateway.DomainNameOptions(**domain_name)
        if isinstance(cors_options, dict):
            cors_options = aws_cdk.aws_apigateway.CorsOptions(**cors_options)
        self._values: typing.Dict[str, typing.Any] = {
            "integrations": integrations,
            "operation_lookup": operation_lookup,
            "spec": spec,
        }
        if cloud_watch_role is not None:
            self._values["cloud_watch_role"] = cloud_watch_role
        if deploy is not None:
            self._values["deploy"] = deploy
        if deploy_options is not None:
            self._values["deploy_options"] = deploy_options
        if disable_execute_api_endpoint is not None:
            self._values["disable_execute_api_endpoint"] = disable_execute_api_endpoint
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if endpoint_export_name is not None:
            self._values["endpoint_export_name"] = endpoint_export_name
        if endpoint_types is not None:
            self._values["endpoint_types"] = endpoint_types
        if fail_on_warnings is not None:
            self._values["fail_on_warnings"] = fail_on_warnings
        if parameters is not None:
            self._values["parameters"] = parameters
        if policy is not None:
            self._values["policy"] = policy
        if rest_api_name is not None:
            self._values["rest_api_name"] = rest_api_name
        if retain_deployments is not None:
            self._values["retain_deployments"] = retain_deployments
        if cors_options is not None:
            self._values["cors_options"] = cors_options
        if default_authorizer is not None:
            self._values["default_authorizer"] = default_authorizer

    @builtins.property
    def cloud_watch_role(self) -> typing.Optional[builtins.bool]:
        '''Automatically configure an AWS CloudWatch role for API Gateway.

        :default: true
        '''
        result = self._values.get("cloud_watch_role")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy(self) -> typing.Optional[builtins.bool]:
        '''Indicates if a Deployment should be automatically created for this API, and recreated when the API model (resources, methods) changes.

        Since API Gateway deployments are immutable, When this option is enabled
        (by default), an AWS::ApiGateway::Deployment resource will automatically
        created with a logical ID that hashes the API model (methods, resources
        and options). This means that when the model changes, the logical ID of
        this CloudFormation resource will change, and a new deployment will be
        created.

        If this is set, ``latestDeployment`` will refer to the ``Deployment`` object
        and ``deploymentStage`` will refer to a ``Stage`` that points to this
        deployment. To customize the stage options, use the ``deployOptions``
        property.

        A CloudFormation Output will also be defined with the root URL endpoint
        of this REST API.

        :default: true
        '''
        result = self._values.get("deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy_options(self) -> typing.Optional[aws_cdk.aws_apigateway.StageOptions]:
        '''Options for the API Gateway stage that will always point to the latest deployment when ``deploy`` is enabled.

        If ``deploy`` is disabled,
        this value cannot be set.

        :default: - Based on defaults of ``StageOptions``.
        '''
        result = self._values.get("deploy_options")
        return typing.cast(typing.Optional[aws_cdk.aws_apigateway.StageOptions], result)

    @builtins.property
    def disable_execute_api_endpoint(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether clients can invoke the API using the default execute-api endpoint.

        To require that clients use a custom domain name to invoke the
        API, disable the default endpoint.

        :default: false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html
        '''
        result = self._values.get("disable_execute_api_endpoint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[aws_cdk.aws_apigateway.DomainNameOptions]:
        '''Configure a custom domain name and map it to this API.

        :default: - no domain name is defined, use ``addDomainName`` or directly define a ``DomainName``.
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[aws_cdk.aws_apigateway.DomainNameOptions], result)

    @builtins.property
    def endpoint_export_name(self) -> typing.Optional[builtins.str]:
        '''Export name for the CfnOutput containing the API endpoint.

        :default: - when no export name is given, output will be created without export
        '''
        result = self._values.get("endpoint_export_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_types(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_apigateway.EndpointType]]:
        '''A list of the endpoint types of the API.

        Use this property when creating
        an API.

        :default: EndpointType.EDGE
        '''
        result = self._values.get("endpoint_types")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_apigateway.EndpointType]], result)

    @builtins.property
    def fail_on_warnings(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether to roll back the resource if a warning occurs while API Gateway is creating the RestApi resource.

        :default: false
        '''
        result = self._values.get("fail_on_warnings")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Custom header parameters for the request.

        :default: - No parameters.

        :see: https://docs.aws.amazon.com/cli/latest/reference/apigateway/import-rest-api.html
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def policy(self) -> typing.Optional[aws_cdk.aws_iam.PolicyDocument]:
        '''A policy document that contains the permissions for this RestApi.

        :default: - No policy.
        '''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.PolicyDocument], result)

    @builtins.property
    def rest_api_name(self) -> typing.Optional[builtins.str]:
        '''A name for the API Gateway RestApi resource.

        :default: - ID of the RestApi construct.
        '''
        result = self._values.get("rest_api_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retain_deployments(self) -> typing.Optional[builtins.bool]:
        '''Retains old deployment resources when the API changes.

        This allows
        manually reverting stages to point to old deployments via the AWS
        Console.

        :default: false
        '''
        result = self._values.get("retain_deployments")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def integrations(self) -> typing.Mapping[builtins.str, OpenApiIntegration]:
        '''(experimental) A mapping of API operation to its integration.

        :stability: experimental
        '''
        result = self._values.get("integrations")
        assert result is not None, "Required property 'integrations' is missing"
        return typing.cast(typing.Mapping[builtins.str, OpenApiIntegration], result)

    @builtins.property
    def operation_lookup(self) -> typing.Mapping[builtins.str, MethodAndPath]:
        '''(experimental) Details about each operation.

        :stability: experimental
        '''
        result = self._values.get("operation_lookup")
        assert result is not None, "Required property 'operation_lookup' is missing"
        return typing.cast(typing.Mapping[builtins.str, MethodAndPath], result)

    @builtins.property
    def cors_options(self) -> typing.Optional[aws_cdk.aws_apigateway.CorsOptions]:
        '''(experimental) Cross Origin Resource Sharing options for the API.

        :stability: experimental
        '''
        result = self._values.get("cors_options")
        return typing.cast(typing.Optional[aws_cdk.aws_apigateway.CorsOptions], result)

    @builtins.property
    def default_authorizer(self) -> typing.Optional[Authorizer]:
        '''(experimental) The default authorizer to use for your api.

        When omitted, no authorizer is used.
        Authorizers specified at the integration level will override this for that operation.

        :stability: experimental
        '''
        result = self._values.get("default_authorizer")
        return typing.cast(typing.Optional[Authorizer], result)

    @builtins.property
    def spec(self) -> typing.Any:
        '''(experimental) The parsed OpenAPI specification.

        :stability: experimental
        '''
        result = self._values.get("spec")
        assert result is not None, "Required property 'spec' is missing"
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenApiGatewayLambdaApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Authorizer",
    "AuthorizerProps",
    "Authorizers",
    "ClientLanguage",
    "CognitoAuthorizer",
    "CognitoAuthorizerProps",
    "CustomAuthorizer",
    "CustomAuthorizerProps",
    "CustomAuthorizerType",
    "DocumentationFormat",
    "IamAuthorizer",
    "MethodAndPath",
    "NoneAuthorizer",
    "OpenApiGatewayLambdaApi",
    "OpenApiGatewayLambdaApiProps",
    "OpenApiGatewayProjectOptions",
    "OpenApiGatewayPythonProject",
    "OpenApiGatewayPythonProjectOptions",
    "OpenApiGatewayTsProject",
    "OpenApiGatewayTsProjectOptions",
    "OpenApiIntegration",
    "OpenApiOptions",
]

publication.publish()
