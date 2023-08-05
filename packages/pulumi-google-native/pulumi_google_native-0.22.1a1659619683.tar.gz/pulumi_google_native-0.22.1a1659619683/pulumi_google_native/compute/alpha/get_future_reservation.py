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
    'GetFutureReservationResult',
    'AwaitableGetFutureReservationResult',
    'get_future_reservation',
    'get_future_reservation_output',
]

@pulumi.output_type
class GetFutureReservationResult:
    def __init__(__self__, creation_timestamp=None, description=None, kind=None, name=None, name_prefix=None, self_link=None, self_link_with_id=None, share_settings=None, specific_sku_properties=None, status=None, time_window=None, zone=None):
        if creation_timestamp and not isinstance(creation_timestamp, str):
            raise TypeError("Expected argument 'creation_timestamp' to be a str")
        pulumi.set(__self__, "creation_timestamp", creation_timestamp)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if kind and not isinstance(kind, str):
            raise TypeError("Expected argument 'kind' to be a str")
        pulumi.set(__self__, "kind", kind)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if name_prefix and not isinstance(name_prefix, str):
            raise TypeError("Expected argument 'name_prefix' to be a str")
        pulumi.set(__self__, "name_prefix", name_prefix)
        if self_link and not isinstance(self_link, str):
            raise TypeError("Expected argument 'self_link' to be a str")
        pulumi.set(__self__, "self_link", self_link)
        if self_link_with_id and not isinstance(self_link_with_id, str):
            raise TypeError("Expected argument 'self_link_with_id' to be a str")
        pulumi.set(__self__, "self_link_with_id", self_link_with_id)
        if share_settings and not isinstance(share_settings, dict):
            raise TypeError("Expected argument 'share_settings' to be a dict")
        pulumi.set(__self__, "share_settings", share_settings)
        if specific_sku_properties and not isinstance(specific_sku_properties, dict):
            raise TypeError("Expected argument 'specific_sku_properties' to be a dict")
        pulumi.set(__self__, "specific_sku_properties", specific_sku_properties)
        if status and not isinstance(status, dict):
            raise TypeError("Expected argument 'status' to be a dict")
        pulumi.set(__self__, "status", status)
        if time_window and not isinstance(time_window, dict):
            raise TypeError("Expected argument 'time_window' to be a dict")
        pulumi.set(__self__, "time_window", time_window)
        if zone and not isinstance(zone, str):
            raise TypeError("Expected argument 'zone' to be a str")
        pulumi.set(__self__, "zone", zone)

    @property
    @pulumi.getter(name="creationTimestamp")
    def creation_timestamp(self) -> str:
        """
        The creation timestamp for this future reservation in RFC3339 text format.
        """
        return pulumi.get(self, "creation_timestamp")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        An optional description of this resource. Provide this property when you create the future reservation.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def kind(self) -> str:
        """
        Type of the resource. Always compute#futureReservation for future reservations.
        """
        return pulumi.get(self, "kind")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the resource, provided by the client when initially creating the resource. The resource name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?` which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="namePrefix")
    def name_prefix(self) -> str:
        """
        Name prefix for the reservations to be created at the time of delivery. The name prefix must comply with RFC1035. Maximum allowed length for name prefix is 20. Automatically created reservations name format will be -date-####.
        """
        return pulumi.get(self, "name_prefix")

    @property
    @pulumi.getter(name="selfLink")
    def self_link(self) -> str:
        """
        Server-defined fully-qualified URL for this resource.
        """
        return pulumi.get(self, "self_link")

    @property
    @pulumi.getter(name="selfLinkWithId")
    def self_link_with_id(self) -> str:
        """
        Server-defined URL for this resource with the resource id.
        """
        return pulumi.get(self, "self_link_with_id")

    @property
    @pulumi.getter(name="shareSettings")
    def share_settings(self) -> 'outputs.ShareSettingsResponse':
        """
        List of Projects/Folders to share with.
        """
        return pulumi.get(self, "share_settings")

    @property
    @pulumi.getter(name="specificSkuProperties")
    def specific_sku_properties(self) -> 'outputs.FutureReservationSpecificSKUPropertiesResponse':
        """
        Future Reservation configuration to indicate instance properties and total count.
        """
        return pulumi.get(self, "specific_sku_properties")

    @property
    @pulumi.getter
    def status(self) -> 'outputs.FutureReservationStatusResponse':
        """
        [Output only] Status of the Future Reservation
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter(name="timeWindow")
    def time_window(self) -> 'outputs.FutureReservationTimeWindowResponse':
        """
        Time window for this Future Reservation.
        """
        return pulumi.get(self, "time_window")

    @property
    @pulumi.getter
    def zone(self) -> str:
        """
        URL of the Zone where this future reservation resides.
        """
        return pulumi.get(self, "zone")


class AwaitableGetFutureReservationResult(GetFutureReservationResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetFutureReservationResult(
            creation_timestamp=self.creation_timestamp,
            description=self.description,
            kind=self.kind,
            name=self.name,
            name_prefix=self.name_prefix,
            self_link=self.self_link,
            self_link_with_id=self.self_link_with_id,
            share_settings=self.share_settings,
            specific_sku_properties=self.specific_sku_properties,
            status=self.status,
            time_window=self.time_window,
            zone=self.zone)


def get_future_reservation(future_reservation: Optional[str] = None,
                           project: Optional[str] = None,
                           zone: Optional[str] = None,
                           opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetFutureReservationResult:
    """
    Retrieves information about the specified future reservation.
    """
    __args__ = dict()
    __args__['futureReservation'] = future_reservation
    __args__['project'] = project
    __args__['zone'] = zone
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:compute/alpha:getFutureReservation', __args__, opts=opts, typ=GetFutureReservationResult).value

    return AwaitableGetFutureReservationResult(
        creation_timestamp=__ret__.creation_timestamp,
        description=__ret__.description,
        kind=__ret__.kind,
        name=__ret__.name,
        name_prefix=__ret__.name_prefix,
        self_link=__ret__.self_link,
        self_link_with_id=__ret__.self_link_with_id,
        share_settings=__ret__.share_settings,
        specific_sku_properties=__ret__.specific_sku_properties,
        status=__ret__.status,
        time_window=__ret__.time_window,
        zone=__ret__.zone)


@_utilities.lift_output_func(get_future_reservation)
def get_future_reservation_output(future_reservation: Optional[pulumi.Input[str]] = None,
                                  project: Optional[pulumi.Input[Optional[str]]] = None,
                                  zone: Optional[pulumi.Input[str]] = None,
                                  opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetFutureReservationResult]:
    """
    Retrieves information about the specified future reservation.
    """
    ...
