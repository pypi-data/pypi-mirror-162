# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities
from . import outputs
from ._enums import *
from ._inputs import *

__all__ = ['EnvironmentArgs', 'Environment']

@pulumi.input_type
class EnvironmentArgs:
    def __init__(__self__, *,
                 organization_id: pulumi.Input[str],
                 api_proxy_type: Optional[pulumi.Input['EnvironmentApiProxyType']] = None,
                 deployment_type: Optional[pulumi.Input['EnvironmentDeploymentType']] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 forward_proxy_uri: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 properties: Optional[pulumi.Input['GoogleCloudApigeeV1PropertiesArgs']] = None):
        """
        The set of arguments for constructing a Environment resource.
        :param pulumi.Input['EnvironmentApiProxyType'] api_proxy_type: Optional. API Proxy type supported by the environment. The type can be set when creating the Environment and cannot be changed.
        :param pulumi.Input['EnvironmentDeploymentType'] deployment_type: Optional. Deployment type supported by the environment. The deployment type can be set when creating the environment and cannot be changed. When you enable archive deployment, you will be **prevented from performing** a [subset of actions](/apigee/docs/api-platform/local-development/overview#prevented-actions) within the environment, including: * Managing the deployment of API proxy or shared flow revisions * Creating, updating, or deleting resource files * Creating, updating, or deleting target servers
        :param pulumi.Input[str] description: Optional. Description of the environment.
        :param pulumi.Input[str] display_name: Optional. Display name for this environment.
        :param pulumi.Input[str] forward_proxy_uri: Optional. Url of the forward proxy to be applied to the runtime instances in this environment. Must be in the format of {scheme}://{hostname}:{port}. Note that scheme must be one of "http" or "https", and port must be supplied.
        :param pulumi.Input[str] name: Name of the environment. Values must match the regular expression `^[.\\\\p{Alnum}-_]{1,255}$`
        :param pulumi.Input['GoogleCloudApigeeV1PropertiesArgs'] properties: Optional. Key-value pairs that may be used for customizing the environment.
        """
        pulumi.set(__self__, "organization_id", organization_id)
        if api_proxy_type is not None:
            pulumi.set(__self__, "api_proxy_type", api_proxy_type)
        if deployment_type is not None:
            pulumi.set(__self__, "deployment_type", deployment_type)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if display_name is not None:
            pulumi.set(__self__, "display_name", display_name)
        if forward_proxy_uri is not None:
            pulumi.set(__self__, "forward_proxy_uri", forward_proxy_uri)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if properties is not None:
            pulumi.set(__self__, "properties", properties)

    @property
    @pulumi.getter(name="organizationId")
    def organization_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "organization_id")

    @organization_id.setter
    def organization_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "organization_id", value)

    @property
    @pulumi.getter(name="apiProxyType")
    def api_proxy_type(self) -> Optional[pulumi.Input['EnvironmentApiProxyType']]:
        """
        Optional. API Proxy type supported by the environment. The type can be set when creating the Environment and cannot be changed.
        """
        return pulumi.get(self, "api_proxy_type")

    @api_proxy_type.setter
    def api_proxy_type(self, value: Optional[pulumi.Input['EnvironmentApiProxyType']]):
        pulumi.set(self, "api_proxy_type", value)

    @property
    @pulumi.getter(name="deploymentType")
    def deployment_type(self) -> Optional[pulumi.Input['EnvironmentDeploymentType']]:
        """
        Optional. Deployment type supported by the environment. The deployment type can be set when creating the environment and cannot be changed. When you enable archive deployment, you will be **prevented from performing** a [subset of actions](/apigee/docs/api-platform/local-development/overview#prevented-actions) within the environment, including: * Managing the deployment of API proxy or shared flow revisions * Creating, updating, or deleting resource files * Creating, updating, or deleting target servers
        """
        return pulumi.get(self, "deployment_type")

    @deployment_type.setter
    def deployment_type(self, value: Optional[pulumi.Input['EnvironmentDeploymentType']]):
        pulumi.set(self, "deployment_type", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. Description of the environment.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. Display name for this environment.
        """
        return pulumi.get(self, "display_name")

    @display_name.setter
    def display_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "display_name", value)

    @property
    @pulumi.getter(name="forwardProxyUri")
    def forward_proxy_uri(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. Url of the forward proxy to be applied to the runtime instances in this environment. Must be in the format of {scheme}://{hostname}:{port}. Note that scheme must be one of "http" or "https", and port must be supplied.
        """
        return pulumi.get(self, "forward_proxy_uri")

    @forward_proxy_uri.setter
    def forward_proxy_uri(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "forward_proxy_uri", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the environment. Values must match the regular expression `^[.\\\\p{Alnum}-_]{1,255}$`
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def properties(self) -> Optional[pulumi.Input['GoogleCloudApigeeV1PropertiesArgs']]:
        """
        Optional. Key-value pairs that may be used for customizing the environment.
        """
        return pulumi.get(self, "properties")

    @properties.setter
    def properties(self, value: Optional[pulumi.Input['GoogleCloudApigeeV1PropertiesArgs']]):
        pulumi.set(self, "properties", value)


class Environment(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 api_proxy_type: Optional[pulumi.Input['EnvironmentApiProxyType']] = None,
                 deployment_type: Optional[pulumi.Input['EnvironmentDeploymentType']] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 forward_proxy_uri: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 organization_id: Optional[pulumi.Input[str]] = None,
                 properties: Optional[pulumi.Input[pulumi.InputType['GoogleCloudApigeeV1PropertiesArgs']]] = None,
                 __props__=None):
        """
        Creates an environment in an organization.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input['EnvironmentApiProxyType'] api_proxy_type: Optional. API Proxy type supported by the environment. The type can be set when creating the Environment and cannot be changed.
        :param pulumi.Input['EnvironmentDeploymentType'] deployment_type: Optional. Deployment type supported by the environment. The deployment type can be set when creating the environment and cannot be changed. When you enable archive deployment, you will be **prevented from performing** a [subset of actions](/apigee/docs/api-platform/local-development/overview#prevented-actions) within the environment, including: * Managing the deployment of API proxy or shared flow revisions * Creating, updating, or deleting resource files * Creating, updating, or deleting target servers
        :param pulumi.Input[str] description: Optional. Description of the environment.
        :param pulumi.Input[str] display_name: Optional. Display name for this environment.
        :param pulumi.Input[str] forward_proxy_uri: Optional. Url of the forward proxy to be applied to the runtime instances in this environment. Must be in the format of {scheme}://{hostname}:{port}. Note that scheme must be one of "http" or "https", and port must be supplied.
        :param pulumi.Input[str] name: Name of the environment. Values must match the regular expression `^[.\\\\p{Alnum}-_]{1,255}$`
        :param pulumi.Input[pulumi.InputType['GoogleCloudApigeeV1PropertiesArgs']] properties: Optional. Key-value pairs that may be used for customizing the environment.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: EnvironmentArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates an environment in an organization.

        :param str resource_name: The name of the resource.
        :param EnvironmentArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(EnvironmentArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 api_proxy_type: Optional[pulumi.Input['EnvironmentApiProxyType']] = None,
                 deployment_type: Optional[pulumi.Input['EnvironmentDeploymentType']] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 forward_proxy_uri: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 organization_id: Optional[pulumi.Input[str]] = None,
                 properties: Optional[pulumi.Input[pulumi.InputType['GoogleCloudApigeeV1PropertiesArgs']]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = EnvironmentArgs.__new__(EnvironmentArgs)

            __props__.__dict__["api_proxy_type"] = api_proxy_type
            __props__.__dict__["deployment_type"] = deployment_type
            __props__.__dict__["description"] = description
            __props__.__dict__["display_name"] = display_name
            __props__.__dict__["forward_proxy_uri"] = forward_proxy_uri
            __props__.__dict__["name"] = name
            if organization_id is None and not opts.urn:
                raise TypeError("Missing required property 'organization_id'")
            __props__.__dict__["organization_id"] = organization_id
            __props__.__dict__["properties"] = properties
            __props__.__dict__["created_at"] = None
            __props__.__dict__["last_modified_at"] = None
            __props__.__dict__["state"] = None
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["organization_id"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(Environment, __self__).__init__(
            'google-native:apigee/v1:Environment',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Environment':
        """
        Get an existing Environment resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = EnvironmentArgs.__new__(EnvironmentArgs)

        __props__.__dict__["api_proxy_type"] = None
        __props__.__dict__["created_at"] = None
        __props__.__dict__["deployment_type"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["display_name"] = None
        __props__.__dict__["forward_proxy_uri"] = None
        __props__.__dict__["last_modified_at"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["organization_id"] = None
        __props__.__dict__["properties"] = None
        __props__.__dict__["state"] = None
        return Environment(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="apiProxyType")
    def api_proxy_type(self) -> pulumi.Output[str]:
        """
        Optional. API Proxy type supported by the environment. The type can be set when creating the Environment and cannot be changed.
        """
        return pulumi.get(self, "api_proxy_type")

    @property
    @pulumi.getter(name="createdAt")
    def created_at(self) -> pulumi.Output[str]:
        """
        Creation time of this environment as milliseconds since epoch.
        """
        return pulumi.get(self, "created_at")

    @property
    @pulumi.getter(name="deploymentType")
    def deployment_type(self) -> pulumi.Output[str]:
        """
        Optional. Deployment type supported by the environment. The deployment type can be set when creating the environment and cannot be changed. When you enable archive deployment, you will be **prevented from performing** a [subset of actions](/apigee/docs/api-platform/local-development/overview#prevented-actions) within the environment, including: * Managing the deployment of API proxy or shared flow revisions * Creating, updating, or deleting resource files * Creating, updating, or deleting target servers
        """
        return pulumi.get(self, "deployment_type")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        Optional. Description of the environment.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> pulumi.Output[str]:
        """
        Optional. Display name for this environment.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter(name="forwardProxyUri")
    def forward_proxy_uri(self) -> pulumi.Output[str]:
        """
        Optional. Url of the forward proxy to be applied to the runtime instances in this environment. Must be in the format of {scheme}://{hostname}:{port}. Note that scheme must be one of "http" or "https", and port must be supplied.
        """
        return pulumi.get(self, "forward_proxy_uri")

    @property
    @pulumi.getter(name="lastModifiedAt")
    def last_modified_at(self) -> pulumi.Output[str]:
        """
        Last modification time of this environment as milliseconds since epoch.
        """
        return pulumi.get(self, "last_modified_at")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Optional. Name of the environment. Alternatively, the name may be specified in the request body in the name field.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="organizationId")
    def organization_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "organization_id")

    @property
    @pulumi.getter
    def properties(self) -> pulumi.Output['outputs.GoogleCloudApigeeV1PropertiesResponse']:
        """
        Optional. Key-value pairs that may be used for customizing the environment.
        """
        return pulumi.get(self, "properties")

    @property
    @pulumi.getter
    def state(self) -> pulumi.Output[str]:
        """
        State of the environment. Values other than ACTIVE means the resource is not ready to use.
        """
        return pulumi.get(self, "state")

