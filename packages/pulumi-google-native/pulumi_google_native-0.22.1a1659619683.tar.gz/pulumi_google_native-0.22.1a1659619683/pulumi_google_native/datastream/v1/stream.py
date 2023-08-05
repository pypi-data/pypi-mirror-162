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

__all__ = ['StreamArgs', 'Stream']

@pulumi.input_type
class StreamArgs:
    def __init__(__self__, *,
                 destination_config: pulumi.Input['DestinationConfigArgs'],
                 display_name: pulumi.Input[str],
                 source_config: pulumi.Input['SourceConfigArgs'],
                 stream_id: pulumi.Input[str],
                 backfill_all: Optional[pulumi.Input['BackfillAllStrategyArgs']] = None,
                 backfill_none: Optional[pulumi.Input['BackfillNoneStrategyArgs']] = None,
                 customer_managed_encryption_key: Optional[pulumi.Input[str]] = None,
                 force: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 state: Optional[pulumi.Input['StreamState']] = None,
                 validate_only: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a Stream resource.
        :param pulumi.Input['DestinationConfigArgs'] destination_config: Destination connection profile configuration.
        :param pulumi.Input[str] display_name: Display name.
        :param pulumi.Input['SourceConfigArgs'] source_config: Source connection profile configuration.
        :param pulumi.Input[str] stream_id: Required. The stream identifier.
        :param pulumi.Input['BackfillAllStrategyArgs'] backfill_all: Automatically backfill objects included in the stream source configuration. Specific objects can be excluded.
        :param pulumi.Input['BackfillNoneStrategyArgs'] backfill_none: Do not automatically backfill any objects.
        :param pulumi.Input[str] customer_managed_encryption_key: Immutable. A reference to a KMS encryption key. If provided, it will be used to encrypt the data. If left blank, data will be encrypted using an internal Stream-specific encryption key provisioned through KMS.
        :param pulumi.Input[str] force: Optional. Create the stream without validating it.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: Labels.
        :param pulumi.Input[str] request_id: Optional. A request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. The server will guarantee that for at least 60 minutes since the first request. For example, consider a situation where you make an initial request and the request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported (00000000-0000-0000-0000-000000000000).
        :param pulumi.Input['StreamState'] state: The state of the stream.
        :param pulumi.Input[str] validate_only: Optional. Only validate the stream, but don't create any resources. The default is false.
        """
        pulumi.set(__self__, "destination_config", destination_config)
        pulumi.set(__self__, "display_name", display_name)
        pulumi.set(__self__, "source_config", source_config)
        pulumi.set(__self__, "stream_id", stream_id)
        if backfill_all is not None:
            pulumi.set(__self__, "backfill_all", backfill_all)
        if backfill_none is not None:
            pulumi.set(__self__, "backfill_none", backfill_none)
        if customer_managed_encryption_key is not None:
            pulumi.set(__self__, "customer_managed_encryption_key", customer_managed_encryption_key)
        if force is not None:
            pulumi.set(__self__, "force", force)
        if labels is not None:
            pulumi.set(__self__, "labels", labels)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if request_id is not None:
            pulumi.set(__self__, "request_id", request_id)
        if state is not None:
            pulumi.set(__self__, "state", state)
        if validate_only is not None:
            pulumi.set(__self__, "validate_only", validate_only)

    @property
    @pulumi.getter(name="destinationConfig")
    def destination_config(self) -> pulumi.Input['DestinationConfigArgs']:
        """
        Destination connection profile configuration.
        """
        return pulumi.get(self, "destination_config")

    @destination_config.setter
    def destination_config(self, value: pulumi.Input['DestinationConfigArgs']):
        pulumi.set(self, "destination_config", value)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> pulumi.Input[str]:
        """
        Display name.
        """
        return pulumi.get(self, "display_name")

    @display_name.setter
    def display_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "display_name", value)

    @property
    @pulumi.getter(name="sourceConfig")
    def source_config(self) -> pulumi.Input['SourceConfigArgs']:
        """
        Source connection profile configuration.
        """
        return pulumi.get(self, "source_config")

    @source_config.setter
    def source_config(self, value: pulumi.Input['SourceConfigArgs']):
        pulumi.set(self, "source_config", value)

    @property
    @pulumi.getter(name="streamId")
    def stream_id(self) -> pulumi.Input[str]:
        """
        Required. The stream identifier.
        """
        return pulumi.get(self, "stream_id")

    @stream_id.setter
    def stream_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "stream_id", value)

    @property
    @pulumi.getter(name="backfillAll")
    def backfill_all(self) -> Optional[pulumi.Input['BackfillAllStrategyArgs']]:
        """
        Automatically backfill objects included in the stream source configuration. Specific objects can be excluded.
        """
        return pulumi.get(self, "backfill_all")

    @backfill_all.setter
    def backfill_all(self, value: Optional[pulumi.Input['BackfillAllStrategyArgs']]):
        pulumi.set(self, "backfill_all", value)

    @property
    @pulumi.getter(name="backfillNone")
    def backfill_none(self) -> Optional[pulumi.Input['BackfillNoneStrategyArgs']]:
        """
        Do not automatically backfill any objects.
        """
        return pulumi.get(self, "backfill_none")

    @backfill_none.setter
    def backfill_none(self, value: Optional[pulumi.Input['BackfillNoneStrategyArgs']]):
        pulumi.set(self, "backfill_none", value)

    @property
    @pulumi.getter(name="customerManagedEncryptionKey")
    def customer_managed_encryption_key(self) -> Optional[pulumi.Input[str]]:
        """
        Immutable. A reference to a KMS encryption key. If provided, it will be used to encrypt the data. If left blank, data will be encrypted using an internal Stream-specific encryption key provisioned through KMS.
        """
        return pulumi.get(self, "customer_managed_encryption_key")

    @customer_managed_encryption_key.setter
    def customer_managed_encryption_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "customer_managed_encryption_key", value)

    @property
    @pulumi.getter
    def force(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. Create the stream without validating it.
        """
        return pulumi.get(self, "force")

    @force.setter
    def force(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "force", value)

    @property
    @pulumi.getter
    def labels(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Labels.
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
    def project(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)

    @property
    @pulumi.getter(name="requestId")
    def request_id(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. A request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. The server will guarantee that for at least 60 minutes since the first request. For example, consider a situation where you make an initial request and the request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported (00000000-0000-0000-0000-000000000000).
        """
        return pulumi.get(self, "request_id")

    @request_id.setter
    def request_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "request_id", value)

    @property
    @pulumi.getter
    def state(self) -> Optional[pulumi.Input['StreamState']]:
        """
        The state of the stream.
        """
        return pulumi.get(self, "state")

    @state.setter
    def state(self, value: Optional[pulumi.Input['StreamState']]):
        pulumi.set(self, "state", value)

    @property
    @pulumi.getter(name="validateOnly")
    def validate_only(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. Only validate the stream, but don't create any resources. The default is false.
        """
        return pulumi.get(self, "validate_only")

    @validate_only.setter
    def validate_only(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "validate_only", value)


class Stream(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 backfill_all: Optional[pulumi.Input[pulumi.InputType['BackfillAllStrategyArgs']]] = None,
                 backfill_none: Optional[pulumi.Input[pulumi.InputType['BackfillNoneStrategyArgs']]] = None,
                 customer_managed_encryption_key: Optional[pulumi.Input[str]] = None,
                 destination_config: Optional[pulumi.Input[pulumi.InputType['DestinationConfigArgs']]] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 force: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 source_config: Optional[pulumi.Input[pulumi.InputType['SourceConfigArgs']]] = None,
                 state: Optional[pulumi.Input['StreamState']] = None,
                 stream_id: Optional[pulumi.Input[str]] = None,
                 validate_only: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Use this method to create a stream.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['BackfillAllStrategyArgs']] backfill_all: Automatically backfill objects included in the stream source configuration. Specific objects can be excluded.
        :param pulumi.Input[pulumi.InputType['BackfillNoneStrategyArgs']] backfill_none: Do not automatically backfill any objects.
        :param pulumi.Input[str] customer_managed_encryption_key: Immutable. A reference to a KMS encryption key. If provided, it will be used to encrypt the data. If left blank, data will be encrypted using an internal Stream-specific encryption key provisioned through KMS.
        :param pulumi.Input[pulumi.InputType['DestinationConfigArgs']] destination_config: Destination connection profile configuration.
        :param pulumi.Input[str] display_name: Display name.
        :param pulumi.Input[str] force: Optional. Create the stream without validating it.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: Labels.
        :param pulumi.Input[str] request_id: Optional. A request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. The server will guarantee that for at least 60 minutes since the first request. For example, consider a situation where you make an initial request and the request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported (00000000-0000-0000-0000-000000000000).
        :param pulumi.Input[pulumi.InputType['SourceConfigArgs']] source_config: Source connection profile configuration.
        :param pulumi.Input['StreamState'] state: The state of the stream.
        :param pulumi.Input[str] stream_id: Required. The stream identifier.
        :param pulumi.Input[str] validate_only: Optional. Only validate the stream, but don't create any resources. The default is false.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: StreamArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Use this method to create a stream.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param StreamArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(StreamArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 backfill_all: Optional[pulumi.Input[pulumi.InputType['BackfillAllStrategyArgs']]] = None,
                 backfill_none: Optional[pulumi.Input[pulumi.InputType['BackfillNoneStrategyArgs']]] = None,
                 customer_managed_encryption_key: Optional[pulumi.Input[str]] = None,
                 destination_config: Optional[pulumi.Input[pulumi.InputType['DestinationConfigArgs']]] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 force: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 source_config: Optional[pulumi.Input[pulumi.InputType['SourceConfigArgs']]] = None,
                 state: Optional[pulumi.Input['StreamState']] = None,
                 stream_id: Optional[pulumi.Input[str]] = None,
                 validate_only: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = StreamArgs.__new__(StreamArgs)

            __props__.__dict__["backfill_all"] = backfill_all
            __props__.__dict__["backfill_none"] = backfill_none
            __props__.__dict__["customer_managed_encryption_key"] = customer_managed_encryption_key
            if destination_config is None and not opts.urn:
                raise TypeError("Missing required property 'destination_config'")
            __props__.__dict__["destination_config"] = destination_config
            if display_name is None and not opts.urn:
                raise TypeError("Missing required property 'display_name'")
            __props__.__dict__["display_name"] = display_name
            __props__.__dict__["force"] = force
            __props__.__dict__["labels"] = labels
            __props__.__dict__["location"] = location
            __props__.__dict__["project"] = project
            __props__.__dict__["request_id"] = request_id
            if source_config is None and not opts.urn:
                raise TypeError("Missing required property 'source_config'")
            __props__.__dict__["source_config"] = source_config
            __props__.__dict__["state"] = state
            if stream_id is None and not opts.urn:
                raise TypeError("Missing required property 'stream_id'")
            __props__.__dict__["stream_id"] = stream_id
            __props__.__dict__["validate_only"] = validate_only
            __props__.__dict__["create_time"] = None
            __props__.__dict__["errors"] = None
            __props__.__dict__["name"] = None
            __props__.__dict__["update_time"] = None
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["location", "project", "stream_id"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(Stream, __self__).__init__(
            'google-native:datastream/v1:Stream',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Stream':
        """
        Get an existing Stream resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = StreamArgs.__new__(StreamArgs)

        __props__.__dict__["backfill_all"] = None
        __props__.__dict__["backfill_none"] = None
        __props__.__dict__["create_time"] = None
        __props__.__dict__["customer_managed_encryption_key"] = None
        __props__.__dict__["destination_config"] = None
        __props__.__dict__["display_name"] = None
        __props__.__dict__["errors"] = None
        __props__.__dict__["force"] = None
        __props__.__dict__["labels"] = None
        __props__.__dict__["location"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["project"] = None
        __props__.__dict__["request_id"] = None
        __props__.__dict__["source_config"] = None
        __props__.__dict__["state"] = None
        __props__.__dict__["stream_id"] = None
        __props__.__dict__["update_time"] = None
        __props__.__dict__["validate_only"] = None
        return Stream(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="backfillAll")
    def backfill_all(self) -> pulumi.Output['outputs.BackfillAllStrategyResponse']:
        """
        Automatically backfill objects included in the stream source configuration. Specific objects can be excluded.
        """
        return pulumi.get(self, "backfill_all")

    @property
    @pulumi.getter(name="backfillNone")
    def backfill_none(self) -> pulumi.Output['outputs.BackfillNoneStrategyResponse']:
        """
        Do not automatically backfill any objects.
        """
        return pulumi.get(self, "backfill_none")

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> pulumi.Output[str]:
        """
        The creation time of the stream.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter(name="customerManagedEncryptionKey")
    def customer_managed_encryption_key(self) -> pulumi.Output[str]:
        """
        Immutable. A reference to a KMS encryption key. If provided, it will be used to encrypt the data. If left blank, data will be encrypted using an internal Stream-specific encryption key provisioned through KMS.
        """
        return pulumi.get(self, "customer_managed_encryption_key")

    @property
    @pulumi.getter(name="destinationConfig")
    def destination_config(self) -> pulumi.Output['outputs.DestinationConfigResponse']:
        """
        Destination connection profile configuration.
        """
        return pulumi.get(self, "destination_config")

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> pulumi.Output[str]:
        """
        Display name.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter
    def errors(self) -> pulumi.Output[Sequence['outputs.ErrorResponse']]:
        """
        Errors on the Stream.
        """
        return pulumi.get(self, "errors")

    @property
    @pulumi.getter
    def force(self) -> pulumi.Output[Optional[str]]:
        """
        Optional. Create the stream without validating it.
        """
        return pulumi.get(self, "force")

    @property
    @pulumi.getter
    def labels(self) -> pulumi.Output[Mapping[str, str]]:
        """
        Labels.
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
        The stream's name.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        return pulumi.get(self, "project")

    @property
    @pulumi.getter(name="requestId")
    def request_id(self) -> pulumi.Output[Optional[str]]:
        """
        Optional. A request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. The server will guarantee that for at least 60 minutes since the first request. For example, consider a situation where you make an initial request and the request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported (00000000-0000-0000-0000-000000000000).
        """
        return pulumi.get(self, "request_id")

    @property
    @pulumi.getter(name="sourceConfig")
    def source_config(self) -> pulumi.Output['outputs.SourceConfigResponse']:
        """
        Source connection profile configuration.
        """
        return pulumi.get(self, "source_config")

    @property
    @pulumi.getter
    def state(self) -> pulumi.Output[str]:
        """
        The state of the stream.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter(name="streamId")
    def stream_id(self) -> pulumi.Output[str]:
        """
        Required. The stream identifier.
        """
        return pulumi.get(self, "stream_id")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> pulumi.Output[str]:
        """
        The last update time of the stream.
        """
        return pulumi.get(self, "update_time")

    @property
    @pulumi.getter(name="validateOnly")
    def validate_only(self) -> pulumi.Output[Optional[str]]:
        """
        Optional. Only validate the stream, but don't create any resources. The default is false.
        """
        return pulumi.get(self, "validate_only")

