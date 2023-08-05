# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities

__all__ = ['ServiceArgs', 'Service']

@pulumi.input_type
class ServiceArgs:
    def __init__(__self__, *,
                 producer_project_id: Optional[pulumi.Input[str]] = None,
                 service_name: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a Service resource.
        :param pulumi.Input[str] producer_project_id: ID of the project that produces and owns this service.
        :param pulumi.Input[str] service_name: The name of the service. See the [overview](https://cloud.google.com/service-infrastructure/docs/overview) for naming requirements.
        """
        if producer_project_id is not None:
            pulumi.set(__self__, "producer_project_id", producer_project_id)
        if service_name is not None:
            pulumi.set(__self__, "service_name", service_name)

    @property
    @pulumi.getter(name="producerProjectId")
    def producer_project_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the project that produces and owns this service.
        """
        return pulumi.get(self, "producer_project_id")

    @producer_project_id.setter
    def producer_project_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "producer_project_id", value)

    @property
    @pulumi.getter(name="serviceName")
    def service_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the service. See the [overview](https://cloud.google.com/service-infrastructure/docs/overview) for naming requirements.
        """
        return pulumi.get(self, "service_name")

    @service_name.setter
    def service_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "service_name", value)


class Service(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 producer_project_id: Optional[pulumi.Input[str]] = None,
                 service_name: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Creates a new managed service. A managed service is immutable, and is subject to mandatory 30-day data retention. You cannot move a service or recreate it within 30 days after deletion. One producer project can own no more than 500 services. For security and reliability purposes, a production service should be hosted in a dedicated producer project. Operation
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] producer_project_id: ID of the project that produces and owns this service.
        :param pulumi.Input[str] service_name: The name of the service. See the [overview](https://cloud.google.com/service-infrastructure/docs/overview) for naming requirements.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[ServiceArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a new managed service. A managed service is immutable, and is subject to mandatory 30-day data retention. You cannot move a service or recreate it within 30 days after deletion. One producer project can own no more than 500 services. For security and reliability purposes, a production service should be hosted in a dedicated producer project. Operation
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param ServiceArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ServiceArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 producer_project_id: Optional[pulumi.Input[str]] = None,
                 service_name: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ServiceArgs.__new__(ServiceArgs)

            __props__.__dict__["producer_project_id"] = producer_project_id
            __props__.__dict__["service_name"] = service_name
        super(Service, __self__).__init__(
            'google-native:servicemanagement/v1:Service',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Service':
        """
        Get an existing Service resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = ServiceArgs.__new__(ServiceArgs)

        __props__.__dict__["producer_project_id"] = None
        __props__.__dict__["service_name"] = None
        return Service(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="producerProjectId")
    def producer_project_id(self) -> pulumi.Output[str]:
        """
        ID of the project that produces and owns this service.
        """
        return pulumi.get(self, "producer_project_id")

    @property
    @pulumi.getter(name="serviceName")
    def service_name(self) -> pulumi.Output[str]:
        """
        The name of the service. See the [overview](https://cloud.google.com/service-infrastructure/docs/overview) for naming requirements.
        """
        return pulumi.get(self, "service_name")

