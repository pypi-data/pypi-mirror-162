'''
# cdk-codeartifact

CDK Construct to create an AWS Codeartifact repository.  Construct combines creating both Domain and one or more Repositories into one construct and also provides an enumerated type for public external connections.

There are some additional validations built-in to ensure the construct will deploy correctly:

* Naming convention checks for Codeartifact Domain Name.
* Naming convention checks for Codeartifact Repository Name.
* Passing in more than 1 external repository will throw an error - only 1 external repository is supported by Codeartifact.

## External Connection Type

When adding an External Connection to your CodeArtifact repository ensure to make use of the `ExternalRepository` type to define the public external repository comnnection.

```python
export enum ExternalRepository {
  NPM = 'public:npmjs',
  PYPI = 'public:pypi',
  MAVEN_CENTRAL = 'public:msven-central',
  MAVEN_GOOGLE_ANDROID = 'public:maven-googleandroid',
  MAVEN_GRADLE_PLUGINS = 'public:maven-gradleplugins',
  MAVEN_COMMONSWARE = 'public:maven-commonsware',
  NUGET = 'public:nuget-org'
}
```

Currently this construct has been published as an NPM package.

## Installation and Usage

### Typescript

#### Installation

```bash
$ npm install --save cdk-codeartifact
```

#### Usage for CDK V2

```python
import { App, Stack, StackProps } from 'aws-cdk-lib';
import { CodeArtifact, ExternalRepository } from 'cdk-codeartifact';
import { Construct } from 'constructs';

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    new CodeArtifact(this, id, {
      domainName: 'test-domain',
      repositories: [{
        repositoryName: 'test-repo',
        externalConnections: [ExternalRepository.NPM],
      },
      {
        repositoryName: 'test-repo2',
        externalConnections: [ExternalRepository.PYPI],
      }],
    });
  }
}
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

from typeguard import check_type

from ._jsii import *

import aws_cdk
import aws_cdk.aws_codeartifact
import constructs


class CodeArtifact(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-codeartifact.CodeArtifact",
):
    '''A Construct that will allow easy setup of an AWS CodeArtifact Repository within a domain.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        repositories: typing.Optional[typing.Sequence[typing.Union["RepositoryProps", typing.Dict[str, typing.Any]]]] = None,
        domain_name: builtins.str,
        encryption_key: typing.Optional[builtins.str] = None,
        permissions_policy_document: typing.Any = None,
        tags: typing.Optional[typing.Sequence[typing.Union[aws_cdk.CfnTag, typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param repositories: a list of Repositories to create.
        :param domain_name: A string that specifies the name of the requested domain.
        :param encryption_key: The key used to encrypt the domain.
        :param permissions_policy_document: The document that defines the resource policy that is set on a domain.
        :param tags: A list of tags to be applied to the domain.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CodeArtifact.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CodeArtifactProps(
            repositories=repositories,
            domain_name=domain_name,
            encryption_key=encryption_key,
            permissions_policy_document=permissions_policy_document,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> aws_cdk.aws_codeartifact.CfnDomain:
        return typing.cast(aws_cdk.aws_codeartifact.CfnDomain, jsii.get(self, "domain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="props")
    def props(self) -> "CodeArtifactProps":
        return typing.cast("CodeArtifactProps", jsii.get(self, "props"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositories")
    def repositories(self) -> typing.List[aws_cdk.aws_codeartifact.CfnRepository]:
        return typing.cast(typing.List[aws_cdk.aws_codeartifact.CfnRepository], jsii.get(self, "repositories"))


@jsii.data_type(
    jsii_type="cdk-codeartifact.CodeArtifactProps",
    jsii_struct_bases=[aws_cdk.aws_codeartifact.CfnDomainProps],
    name_mapping={
        "domain_name": "domainName",
        "encryption_key": "encryptionKey",
        "permissions_policy_document": "permissionsPolicyDocument",
        "tags": "tags",
        "repositories": "repositories",
    },
)
class CodeArtifactProps(aws_cdk.aws_codeartifact.CfnDomainProps):
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        encryption_key: typing.Optional[builtins.str] = None,
        permissions_policy_document: typing.Any = None,
        tags: typing.Optional[typing.Sequence[typing.Union[aws_cdk.CfnTag, typing.Dict[str, typing.Any]]]] = None,
        repositories: typing.Optional[typing.Sequence[typing.Union["RepositoryProps", typing.Dict[str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for creating CodeArtifact repositories based on a domain.

        :param domain_name: A string that specifies the name of the requested domain.
        :param encryption_key: The key used to encrypt the domain.
        :param permissions_policy_document: The document that defines the resource policy that is set on a domain.
        :param tags: A list of tags to be applied to the domain.
        :param repositories: a list of Repositories to create.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CodeArtifactProps.__init__)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument permissions_policy_document", value=permissions_policy_document, expected_type=type_hints["permissions_policy_document"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument repositories", value=repositories, expected_type=type_hints["repositories"])
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
        }
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if permissions_policy_document is not None:
            self._values["permissions_policy_document"] = permissions_policy_document
        if tags is not None:
            self._values["tags"] = tags
        if repositories is not None:
            self._values["repositories"] = repositories

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''A string that specifies the name of the requested domain.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-domainname
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[builtins.str]:
        '''The key used to encrypt the domain.

        :link: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-encryptionkey
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_policy_document(self) -> typing.Any:
        '''The document that defines the resource policy that is set on a domain.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-permissionspolicydocument
        '''
        result = self._values.get("permissions_policy_document")
        return typing.cast(typing.Any, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.CfnTag]]:
        '''A list of tags to be applied to the domain.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.CfnTag]], result)

    @builtins.property
    def repositories(self) -> typing.Optional[typing.List["RepositoryProps"]]:
        '''a list of Repositories to create.'''
        result = self._values.get("repositories")
        return typing.cast(typing.Optional[typing.List["RepositoryProps"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeArtifactProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-codeartifact.ExternalRepository")
class ExternalRepository(enum.Enum):
    NPM = "NPM"
    PYPI = "PYPI"
    MAVEN_CENTRAL = "MAVEN_CENTRAL"
    MAVEN_GOOGLE_ANDROID = "MAVEN_GOOGLE_ANDROID"
    MAVEN_GRADLE_PLUGINS = "MAVEN_GRADLE_PLUGINS"
    MAVEN_COMMONSWARE = "MAVEN_COMMONSWARE"
    NUGET = "NUGET"


@jsii.data_type(
    jsii_type="cdk-codeartifact.RepositoryProps",
    jsii_struct_bases=[],
    name_mapping={
        "repository_name": "repositoryName",
        "description": "description",
        "domain_owner": "domainOwner",
        "external_connections": "externalConnections",
        "permissions_policy_document": "permissionsPolicyDocument",
        "tags": "tags",
        "upstreams": "upstreams",
    },
)
class RepositoryProps:
    def __init__(
        self,
        *,
        repository_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        domain_owner: typing.Optional[builtins.str] = None,
        external_connections: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_policy_document: typing.Any = None,
        tags: typing.Optional[typing.Sequence[typing.Union[aws_cdk.CfnTag, typing.Dict[str, typing.Any]]]] = None,
        upstreams: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param repository_name: The name of an upstream repository.
        :param description: A text description of the repository.
        :param domain_owner: The 12-digit account number of the AWS account that owns the domain that contains the repository. It does not include dashes or spaces.
        :param external_connections: An array of external connections associated with the repository.
        :param permissions_policy_document: The document that defines the resource policy that is set on a repository.
        :param tags: A list of tags to be applied to the repository.
        :param upstreams: A list of upstream repositories to associate with the repository. The order of the upstream repositories in the list determines their priority order when AWS CodeArtifact looks for a requested package version. For more information, see `Working with upstream repositories <https://docs.aws.amazon.com/codeartifact/latest/ug/repos-upstream.html>`_ .
        '''
        if __debug__:
            type_hints = typing.get_type_hints(RepositoryProps.__init__)
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument domain_owner", value=domain_owner, expected_type=type_hints["domain_owner"])
            check_type(argname="argument external_connections", value=external_connections, expected_type=type_hints["external_connections"])
            check_type(argname="argument permissions_policy_document", value=permissions_policy_document, expected_type=type_hints["permissions_policy_document"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument upstreams", value=upstreams, expected_type=type_hints["upstreams"])
        self._values: typing.Dict[str, typing.Any] = {
            "repository_name": repository_name,
        }
        if description is not None:
            self._values["description"] = description
        if domain_owner is not None:
            self._values["domain_owner"] = domain_owner
        if external_connections is not None:
            self._values["external_connections"] = external_connections
        if permissions_policy_document is not None:
            self._values["permissions_policy_document"] = permissions_policy_document
        if tags is not None:
            self._values["tags"] = tags
        if upstreams is not None:
            self._values["upstreams"] = upstreams

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''The name of an upstream repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-repositoryname
        '''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A text description of the repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_owner(self) -> typing.Optional[builtins.str]:
        '''The 12-digit account number of the AWS account that owns the domain that contains the repository.

        It does not include dashes or spaces.

        :link: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-domainowner
        '''
        result = self._values.get("domain_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_connections(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An array of external connections associated with the repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-externalconnections
        '''
        result = self._values.get("external_connections")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_policy_document(self) -> typing.Any:
        '''The document that defines the resource policy that is set on a repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-permissionspolicydocument
        '''
        result = self._values.get("permissions_policy_document")
        return typing.cast(typing.Any, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.CfnTag]]:
        '''A list of tags to be applied to the repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.CfnTag]], result)

    @builtins.property
    def upstreams(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of upstream repositories to associate with the repository.

        The order of the upstream repositories in the list determines their priority order when AWS CodeArtifact looks for a requested package version. For more information, see `Working with upstream repositories <https://docs.aws.amazon.com/codeartifact/latest/ug/repos-upstream.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-upstreams
        '''
        result = self._values.get("upstreams")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CodeArtifact",
    "CodeArtifactProps",
    "ExternalRepository",
    "RepositoryProps",
]

publication.publish()
