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

__all__ = ['AppConnectorArgs', 'AppConnector']

@pulumi.input_type
class AppConnectorArgs:
    def __init__(__self__, *,
                 principal_info: pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1alphaAppConnectorPrincipalInfoArgs'],
                 app_connector_id: Optional[pulumi.Input[str]] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 resource_info: Optional[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1alphaResourceInfoArgs']] = None,
                 validate_only: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a AppConnector resource.
        :param pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1alphaAppConnectorPrincipalInfoArgs'] principal_info: Principal information about the Identity of the AppConnector.
        :param pulumi.Input[str] app_connector_id: Optional. User-settable AppConnector resource ID. * Must start with a letter. * Must contain between 4-63 characters from `/a-z-/`. * Must end with a number or a letter.
        :param pulumi.Input[str] display_name: Optional. An arbitrary user-provided name for the AppConnector. Cannot exceed 64 characters.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: Optional. Resource labels to represent user provided metadata.
        :param pulumi.Input[str] name: Unique resource name of the AppConnector. The name is ignored when creating a AppConnector.
        :param pulumi.Input[str] request_id: Optional. An optional request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. The server will guarantee that for at least 60 minutes since the first request. For example, consider a situation where you make an initial request and t he request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported (00000000-0000-0000-0000-000000000000).
        :param pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1alphaResourceInfoArgs'] resource_info: Optional. Resource info of the connector.
        :param pulumi.Input[str] validate_only: Optional. If set, validates request by executing a dry-run which would not alter the resource in any way.
        """
        pulumi.set(__self__, "principal_info", principal_info)
        if app_connector_id is not None:
            pulumi.set(__self__, "app_connector_id", app_connector_id)
        if display_name is not None:
            pulumi.set(__self__, "display_name", display_name)
        if labels is not None:
            pulumi.set(__self__, "labels", labels)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if request_id is not None:
            pulumi.set(__self__, "request_id", request_id)
        if resource_info is not None:
            pulumi.set(__self__, "resource_info", resource_info)
        if validate_only is not None:
            pulumi.set(__self__, "validate_only", validate_only)

    @property
    @pulumi.getter(name="principalInfo")
    def principal_info(self) -> pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1alphaAppConnectorPrincipalInfoArgs']:
        """
        Principal information about the Identity of the AppConnector.
        """
        return pulumi.get(self, "principal_info")

    @principal_info.setter
    def principal_info(self, value: pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1alphaAppConnectorPrincipalInfoArgs']):
        pulumi.set(self, "principal_info", value)

    @property
    @pulumi.getter(name="appConnectorId")
    def app_connector_id(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. User-settable AppConnector resource ID. * Must start with a letter. * Must contain between 4-63 characters from `/a-z-/`. * Must end with a number or a letter.
        """
        return pulumi.get(self, "app_connector_id")

    @app_connector_id.setter
    def app_connector_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "app_connector_id", value)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. An arbitrary user-provided name for the AppConnector. Cannot exceed 64 characters.
        """
        return pulumi.get(self, "display_name")

    @display_name.setter
    def display_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "display_name", value)

    @property
    @pulumi.getter
    def labels(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Optional. Resource labels to represent user provided metadata.
        """
        return pulumi.get(self, "labels")

    @labels.setter
    def labels(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "labels", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Unique resource name of the AppConnector. The name is ignored when creating a AppConnector.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)

    @property
    @pulumi.getter(name="requestId")
    def request_id(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. An optional request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. The server will guarantee that for at least 60 minutes since the first request. For example, consider a situation where you make an initial request and t he request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported (00000000-0000-0000-0000-000000000000).
        """
        return pulumi.get(self, "request_id")

    @request_id.setter
    def request_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "request_id", value)

    @property
    @pulumi.getter(name="resourceInfo")
    def resource_info(self) -> Optional[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1alphaResourceInfoArgs']]:
        """
        Optional. Resource info of the connector.
        """
        return pulumi.get(self, "resource_info")

    @resource_info.setter
    def resource_info(self, value: Optional[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1alphaResourceInfoArgs']]):
        pulumi.set(self, "resource_info", value)

    @property
    @pulumi.getter(name="validateOnly")
    def validate_only(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. If set, validates request by executing a dry-run which would not alter the resource in any way.
        """
        return pulumi.get(self, "validate_only")

    @validate_only.setter
    def validate_only(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "validate_only", value)


class AppConnector(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 app_connector_id: Optional[pulumi.Input[str]] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 principal_info: Optional[pulumi.Input[pulumi.InputType['GoogleCloudBeyondcorpAppconnectorsV1alphaAppConnectorPrincipalInfoArgs']]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 resource_info: Optional[pulumi.Input[pulumi.InputType['GoogleCloudBeyondcorpAppconnectorsV1alphaResourceInfoArgs']]] = None,
                 validate_only: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Creates a new AppConnector in a given project and location.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] app_connector_id: Optional. User-settable AppConnector resource ID. * Must start with a letter. * Must contain between 4-63 characters from `/a-z-/`. * Must end with a number or a letter.
        :param pulumi.Input[str] display_name: Optional. An arbitrary user-provided name for the AppConnector. Cannot exceed 64 characters.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: Optional. Resource labels to represent user provided metadata.
        :param pulumi.Input[str] name: Unique resource name of the AppConnector. The name is ignored when creating a AppConnector.
        :param pulumi.Input[pulumi.InputType['GoogleCloudBeyondcorpAppconnectorsV1alphaAppConnectorPrincipalInfoArgs']] principal_info: Principal information about the Identity of the AppConnector.
        :param pulumi.Input[str] request_id: Optional. An optional request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. The server will guarantee that for at least 60 minutes since the first request. For example, consider a situation where you make an initial request and t he request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported (00000000-0000-0000-0000-000000000000).
        :param pulumi.Input[pulumi.InputType['GoogleCloudBeyondcorpAppconnectorsV1alphaResourceInfoArgs']] resource_info: Optional. Resource info of the connector.
        :param pulumi.Input[str] validate_only: Optional. If set, validates request by executing a dry-run which would not alter the resource in any way.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: AppConnectorArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a new AppConnector in a given project and location.

        :param str resource_name: The name of the resource.
        :param AppConnectorArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(AppConnectorArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 app_connector_id: Optional[pulumi.Input[str]] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 principal_info: Optional[pulumi.Input[pulumi.InputType['GoogleCloudBeyondcorpAppconnectorsV1alphaAppConnectorPrincipalInfoArgs']]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 resource_info: Optional[pulumi.Input[pulumi.InputType['GoogleCloudBeyondcorpAppconnectorsV1alphaResourceInfoArgs']]] = None,
                 validate_only: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = AppConnectorArgs.__new__(AppConnectorArgs)

            __props__.__dict__["app_connector_id"] = app_connector_id
            __props__.__dict__["display_name"] = display_name
            __props__.__dict__["labels"] = labels
            __props__.__dict__["location"] = location
            __props__.__dict__["name"] = name
            if principal_info is None and not opts.urn:
                raise TypeError("Missing required property 'principal_info'")
            __props__.__dict__["principal_info"] = principal_info
            __props__.__dict__["project"] = project
            __props__.__dict__["request_id"] = request_id
            __props__.__dict__["resource_info"] = resource_info
            __props__.__dict__["validate_only"] = validate_only
            __props__.__dict__["create_time"] = None
            __props__.__dict__["state"] = None
            __props__.__dict__["uid"] = None
            __props__.__dict__["update_time"] = None
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["location", "project"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(AppConnector, __self__).__init__(
            'google-native:beyondcorp/v1alpha:AppConnector',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'AppConnector':
        """
        Get an existing AppConnector resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = AppConnectorArgs.__new__(AppConnectorArgs)

        __props__.__dict__["app_connector_id"] = None
        __props__.__dict__["create_time"] = None
        __props__.__dict__["display_name"] = None
        __props__.__dict__["labels"] = None
        __props__.__dict__["location"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["principal_info"] = None
        __props__.__dict__["project"] = None
        __props__.__dict__["request_id"] = None
        __props__.__dict__["resource_info"] = None
        __props__.__dict__["state"] = None
        __props__.__dict__["uid"] = None
        __props__.__dict__["update_time"] = None
        __props__.__dict__["validate_only"] = None
        return AppConnector(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="appConnectorId")
    def app_connector_id(self) -> pulumi.Output[Optional[str]]:
        """
        Optional. User-settable AppConnector resource ID. * Must start with a letter. * Must contain between 4-63 characters from `/a-z-/`. * Must end with a number or a letter.
        """
        return pulumi.get(self, "app_connector_id")

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> pulumi.Output[str]:
        """
        Timestamp when the resource was created.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> pulumi.Output[str]:
        """
        Optional. An arbitrary user-provided name for the AppConnector. Cannot exceed 64 characters.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter
    def labels(self) -> pulumi.Output[Mapping[str, str]]:
        """
        Optional. Resource labels to represent user provided metadata.
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Unique resource name of the AppConnector. The name is ignored when creating a AppConnector.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="principalInfo")
    def principal_info(self) -> pulumi.Output['outputs.GoogleCloudBeyondcorpAppconnectorsV1alphaAppConnectorPrincipalInfoResponse']:
        """
        Principal information about the Identity of the AppConnector.
        """
        return pulumi.get(self, "principal_info")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        return pulumi.get(self, "project")

    @property
    @pulumi.getter(name="requestId")
    def request_id(self) -> pulumi.Output[Optional[str]]:
        """
        Optional. An optional request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. The server will guarantee that for at least 60 minutes since the first request. For example, consider a situation where you make an initial request and t he request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported (00000000-0000-0000-0000-000000000000).
        """
        return pulumi.get(self, "request_id")

    @property
    @pulumi.getter(name="resourceInfo")
    def resource_info(self) -> pulumi.Output['outputs.GoogleCloudBeyondcorpAppconnectorsV1alphaResourceInfoResponse']:
        """
        Optional. Resource info of the connector.
        """
        return pulumi.get(self, "resource_info")

    @property
    @pulumi.getter
    def state(self) -> pulumi.Output[str]:
        """
        The current state of the AppConnector.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter
    def uid(self) -> pulumi.Output[str]:
        """
        A unique identifier for the instance generated by the system.
        """
        return pulumi.get(self, "uid")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> pulumi.Output[str]:
        """
        Timestamp when the resource was last modified.
        """
        return pulumi.get(self, "update_time")

    @property
    @pulumi.getter(name="validateOnly")
    def validate_only(self) -> pulumi.Output[Optional[str]]:
        """
        Optional. If set, validates request by executing a dry-run which would not alter the resource in any way.
        """
        return pulumi.get(self, "validate_only")

