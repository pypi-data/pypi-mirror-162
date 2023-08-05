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

__all__ = ['OrganizationReplayArgs', 'OrganizationReplay']

@pulumi.input_type
class OrganizationReplayArgs:
    def __init__(__self__, *,
                 config: pulumi.Input['GoogleCloudPolicysimulatorV1beta1ReplayConfigArgs'],
                 organization_id: pulumi.Input[str],
                 location: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a OrganizationReplay resource.
        :param pulumi.Input['GoogleCloudPolicysimulatorV1beta1ReplayConfigArgs'] config: The configuration used for the `Replay`.
        """
        pulumi.set(__self__, "config", config)
        pulumi.set(__self__, "organization_id", organization_id)
        if location is not None:
            pulumi.set(__self__, "location", location)

    @property
    @pulumi.getter
    def config(self) -> pulumi.Input['GoogleCloudPolicysimulatorV1beta1ReplayConfigArgs']:
        """
        The configuration used for the `Replay`.
        """
        return pulumi.get(self, "config")

    @config.setter
    def config(self, value: pulumi.Input['GoogleCloudPolicysimulatorV1beta1ReplayConfigArgs']):
        pulumi.set(self, "config", value)

    @property
    @pulumi.getter(name="organizationId")
    def organization_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "organization_id")

    @organization_id.setter
    def organization_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "organization_id", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)


class OrganizationReplay(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 config: Optional[pulumi.Input[pulumi.InputType['GoogleCloudPolicysimulatorV1beta1ReplayConfigArgs']]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 organization_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Creates and starts a Replay using the given ReplayConfig.
        Auto-naming is currently not supported for this resource.
        Note - this resource's API doesn't support deletion. When deleted, the resource will persist
        on Google Cloud even though it will be deleted from Pulumi state.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['GoogleCloudPolicysimulatorV1beta1ReplayConfigArgs']] config: The configuration used for the `Replay`.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: OrganizationReplayArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates and starts a Replay using the given ReplayConfig.
        Auto-naming is currently not supported for this resource.
        Note - this resource's API doesn't support deletion. When deleted, the resource will persist
        on Google Cloud even though it will be deleted from Pulumi state.

        :param str resource_name: The name of the resource.
        :param OrganizationReplayArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(OrganizationReplayArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 config: Optional[pulumi.Input[pulumi.InputType['GoogleCloudPolicysimulatorV1beta1ReplayConfigArgs']]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 organization_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = OrganizationReplayArgs.__new__(OrganizationReplayArgs)

            if config is None and not opts.urn:
                raise TypeError("Missing required property 'config'")
            __props__.__dict__["config"] = config
            __props__.__dict__["location"] = location
            if organization_id is None and not opts.urn:
                raise TypeError("Missing required property 'organization_id'")
            __props__.__dict__["organization_id"] = organization_id
            __props__.__dict__["name"] = None
            __props__.__dict__["results_summary"] = None
            __props__.__dict__["state"] = None
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["location", "organization_id"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(OrganizationReplay, __self__).__init__(
            'google-native:policysimulator/v1beta1:OrganizationReplay',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'OrganizationReplay':
        """
        Get an existing OrganizationReplay resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = OrganizationReplayArgs.__new__(OrganizationReplayArgs)

        __props__.__dict__["config"] = None
        __props__.__dict__["location"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["organization_id"] = None
        __props__.__dict__["results_summary"] = None
        __props__.__dict__["state"] = None
        return OrganizationReplay(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def config(self) -> pulumi.Output['outputs.GoogleCloudPolicysimulatorV1beta1ReplayConfigResponse']:
        """
        The configuration used for the `Replay`.
        """
        return pulumi.get(self, "config")

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The resource name of the `Replay`, which has the following format: `{projects|folders|organizations}/{resource-id}/locations/global/replays/{replay-id}`, where `{resource-id}` is the ID of the project, folder, or organization that owns the Replay. Example: `projects/my-example-project/locations/global/replays/506a5f7f-38ce-4d7d-8e03-479ce1833c36`
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="organizationId")
    def organization_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "organization_id")

    @property
    @pulumi.getter(name="resultsSummary")
    def results_summary(self) -> pulumi.Output['outputs.GoogleCloudPolicysimulatorV1beta1ReplayResultsSummaryResponse']:
        """
        Summary statistics about the replayed log entries.
        """
        return pulumi.get(self, "results_summary")

    @property
    @pulumi.getter
    def state(self) -> pulumi.Output[str]:
        """
        The current state of the `Replay`.
        """
        return pulumi.get(self, "state")

