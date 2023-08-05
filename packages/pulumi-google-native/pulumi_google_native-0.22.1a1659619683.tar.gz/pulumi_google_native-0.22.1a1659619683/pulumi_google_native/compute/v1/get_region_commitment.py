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

__all__ = [
    'GetRegionCommitmentResult',
    'AwaitableGetRegionCommitmentResult',
    'get_region_commitment',
    'get_region_commitment_output',
]

@pulumi.output_type
class GetRegionCommitmentResult:
    def __init__(__self__, auto_renew=None, category=None, creation_timestamp=None, description=None, end_timestamp=None, kind=None, license_resource=None, name=None, plan=None, region=None, reservations=None, resources=None, self_link=None, start_timestamp=None, status=None, status_message=None, type=None):
        if auto_renew and not isinstance(auto_renew, bool):
            raise TypeError("Expected argument 'auto_renew' to be a bool")
        pulumi.set(__self__, "auto_renew", auto_renew)
        if category and not isinstance(category, str):
            raise TypeError("Expected argument 'category' to be a str")
        pulumi.set(__self__, "category", category)
        if creation_timestamp and not isinstance(creation_timestamp, str):
            raise TypeError("Expected argument 'creation_timestamp' to be a str")
        pulumi.set(__self__, "creation_timestamp", creation_timestamp)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if end_timestamp and not isinstance(end_timestamp, str):
            raise TypeError("Expected argument 'end_timestamp' to be a str")
        pulumi.set(__self__, "end_timestamp", end_timestamp)
        if kind and not isinstance(kind, str):
            raise TypeError("Expected argument 'kind' to be a str")
        pulumi.set(__self__, "kind", kind)
        if license_resource and not isinstance(license_resource, dict):
            raise TypeError("Expected argument 'license_resource' to be a dict")
        pulumi.set(__self__, "license_resource", license_resource)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if plan and not isinstance(plan, str):
            raise TypeError("Expected argument 'plan' to be a str")
        pulumi.set(__self__, "plan", plan)
        if region and not isinstance(region, str):
            raise TypeError("Expected argument 'region' to be a str")
        pulumi.set(__self__, "region", region)
        if reservations and not isinstance(reservations, list):
            raise TypeError("Expected argument 'reservations' to be a list")
        pulumi.set(__self__, "reservations", reservations)
        if resources and not isinstance(resources, list):
            raise TypeError("Expected argument 'resources' to be a list")
        pulumi.set(__self__, "resources", resources)
        if self_link and not isinstance(self_link, str):
            raise TypeError("Expected argument 'self_link' to be a str")
        pulumi.set(__self__, "self_link", self_link)
        if start_timestamp and not isinstance(start_timestamp, str):
            raise TypeError("Expected argument 'start_timestamp' to be a str")
        pulumi.set(__self__, "start_timestamp", start_timestamp)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)
        if status_message and not isinstance(status_message, str):
            raise TypeError("Expected argument 'status_message' to be a str")
        pulumi.set(__self__, "status_message", status_message)
        if type and not isinstance(type, str):
            raise TypeError("Expected argument 'type' to be a str")
        pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="autoRenew")
    def auto_renew(self) -> bool:
        """
        Specifies whether to enable automatic renewal for the commitment. The default value is false if not specified. The field can be updated until the day of the commitment expiration at 12:00am PST. If the field is set to true, the commitment will be automatically renewed for either one or three years according to the terms of the existing commitment.
        """
        return pulumi.get(self, "auto_renew")

    @property
    @pulumi.getter
    def category(self) -> str:
        """
        The category of the commitment. Category MACHINE specifies commitments composed of machine resources such as VCPU or MEMORY, listed in resources. Category LICENSE specifies commitments composed of software licenses, listed in licenseResources. Note that only MACHINE commitments should have a Type specified.
        """
        return pulumi.get(self, "category")

    @property
    @pulumi.getter(name="creationTimestamp")
    def creation_timestamp(self) -> str:
        """
        Creation timestamp in RFC3339 text format.
        """
        return pulumi.get(self, "creation_timestamp")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        An optional description of this resource. Provide this property when you create the resource.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="endTimestamp")
    def end_timestamp(self) -> str:
        """
        Commitment end time in RFC3339 text format.
        """
        return pulumi.get(self, "end_timestamp")

    @property
    @pulumi.getter
    def kind(self) -> str:
        """
        Type of the resource. Always compute#commitment for commitments.
        """
        return pulumi.get(self, "kind")

    @property
    @pulumi.getter(name="licenseResource")
    def license_resource(self) -> 'outputs.LicenseResourceCommitmentResponse':
        """
        The license specification required as part of a license commitment.
        """
        return pulumi.get(self, "license_resource")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the resource. Provided by the client when the resource is created. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?` which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def plan(self) -> str:
        """
        The plan for this commitment, which determines duration and discount rate. The currently supported plans are TWELVE_MONTH (1 year), and THIRTY_SIX_MONTH (3 years).
        """
        return pulumi.get(self, "plan")

    @property
    @pulumi.getter
    def region(self) -> str:
        """
        URL of the region where this commitment may be used.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter
    def reservations(self) -> Sequence['outputs.ReservationResponse']:
        """
        List of reservations in this commitment.
        """
        return pulumi.get(self, "reservations")

    @property
    @pulumi.getter
    def resources(self) -> Sequence['outputs.ResourceCommitmentResponse']:
        """
        A list of commitment amounts for particular resources. Note that VCPU and MEMORY resource commitments must occur together.
        """
        return pulumi.get(self, "resources")

    @property
    @pulumi.getter(name="selfLink")
    def self_link(self) -> str:
        """
        Server-defined URL for the resource.
        """
        return pulumi.get(self, "self_link")

    @property
    @pulumi.getter(name="startTimestamp")
    def start_timestamp(self) -> str:
        """
        Commitment start time in RFC3339 text format.
        """
        return pulumi.get(self, "start_timestamp")

    @property
    @pulumi.getter
    def status(self) -> str:
        """
        Status of the commitment with regards to eventual expiration (each commitment has an end date defined). One of the following values: NOT_YET_ACTIVE, ACTIVE, EXPIRED.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter(name="statusMessage")
    def status_message(self) -> str:
        """
        An optional, human-readable explanation of the status.
        """
        return pulumi.get(self, "status_message")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        The type of commitment, which affects the discount rate and the eligible resources. Type MEMORY_OPTIMIZED specifies a commitment that will only apply to memory optimized machines. Type ACCELERATOR_OPTIMIZED specifies a commitment that will only apply to accelerator optimized machines.
        """
        return pulumi.get(self, "type")


class AwaitableGetRegionCommitmentResult(GetRegionCommitmentResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetRegionCommitmentResult(
            auto_renew=self.auto_renew,
            category=self.category,
            creation_timestamp=self.creation_timestamp,
            description=self.description,
            end_timestamp=self.end_timestamp,
            kind=self.kind,
            license_resource=self.license_resource,
            name=self.name,
            plan=self.plan,
            region=self.region,
            reservations=self.reservations,
            resources=self.resources,
            self_link=self.self_link,
            start_timestamp=self.start_timestamp,
            status=self.status,
            status_message=self.status_message,
            type=self.type)


def get_region_commitment(commitment: Optional[str] = None,
                          project: Optional[str] = None,
                          region: Optional[str] = None,
                          opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetRegionCommitmentResult:
    """
    Returns the specified commitment resource. Gets a list of available commitments by making a list() request.
    """
    __args__ = dict()
    __args__['commitment'] = commitment
    __args__['project'] = project
    __args__['region'] = region
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:compute/v1:getRegionCommitment', __args__, opts=opts, typ=GetRegionCommitmentResult).value

    return AwaitableGetRegionCommitmentResult(
        auto_renew=__ret__.auto_renew,
        category=__ret__.category,
        creation_timestamp=__ret__.creation_timestamp,
        description=__ret__.description,
        end_timestamp=__ret__.end_timestamp,
        kind=__ret__.kind,
        license_resource=__ret__.license_resource,
        name=__ret__.name,
        plan=__ret__.plan,
        region=__ret__.region,
        reservations=__ret__.reservations,
        resources=__ret__.resources,
        self_link=__ret__.self_link,
        start_timestamp=__ret__.start_timestamp,
        status=__ret__.status,
        status_message=__ret__.status_message,
        type=__ret__.type)


@_utilities.lift_output_func(get_region_commitment)
def get_region_commitment_output(commitment: Optional[pulumi.Input[str]] = None,
                                 project: Optional[pulumi.Input[Optional[str]]] = None,
                                 region: Optional[pulumi.Input[str]] = None,
                                 opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetRegionCommitmentResult]:
    """
    Returns the specified commitment resource. Gets a list of available commitments by making a list() request.
    """
    ...
