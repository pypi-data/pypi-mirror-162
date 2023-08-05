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
    'GetChangeResult',
    'AwaitableGetChangeResult',
    'get_change',
    'get_change_output',
]

@pulumi.output_type
class GetChangeResult:
    def __init__(__self__, additions=None, deletions=None, is_serving=None, kind=None, start_time=None, status=None):
        if additions and not isinstance(additions, list):
            raise TypeError("Expected argument 'additions' to be a list")
        pulumi.set(__self__, "additions", additions)
        if deletions and not isinstance(deletions, list):
            raise TypeError("Expected argument 'deletions' to be a list")
        pulumi.set(__self__, "deletions", deletions)
        if is_serving and not isinstance(is_serving, bool):
            raise TypeError("Expected argument 'is_serving' to be a bool")
        pulumi.set(__self__, "is_serving", is_serving)
        if kind and not isinstance(kind, str):
            raise TypeError("Expected argument 'kind' to be a str")
        pulumi.set(__self__, "kind", kind)
        if start_time and not isinstance(start_time, str):
            raise TypeError("Expected argument 'start_time' to be a str")
        pulumi.set(__self__, "start_time", start_time)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)

    @property
    @pulumi.getter
    def additions(self) -> Sequence['outputs.ResourceRecordSetResponse']:
        """
        Which ResourceRecordSets to add?
        """
        return pulumi.get(self, "additions")

    @property
    @pulumi.getter
    def deletions(self) -> Sequence['outputs.ResourceRecordSetResponse']:
        """
        Which ResourceRecordSets to remove? Must match existing data exactly.
        """
        return pulumi.get(self, "deletions")

    @property
    @pulumi.getter(name="isServing")
    def is_serving(self) -> bool:
        """
        If the DNS queries for the zone will be served.
        """
        return pulumi.get(self, "is_serving")

    @property
    @pulumi.getter
    def kind(self) -> str:
        return pulumi.get(self, "kind")

    @property
    @pulumi.getter(name="startTime")
    def start_time(self) -> str:
        """
        The time that this operation was started by the server (output only). This is in RFC3339 text format.
        """
        return pulumi.get(self, "start_time")

    @property
    @pulumi.getter
    def status(self) -> str:
        """
        Status of the operation (output only). A status of "done" means that the request to update the authoritative servers has been sent, but the servers might not be updated yet.
        """
        return pulumi.get(self, "status")


class AwaitableGetChangeResult(GetChangeResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetChangeResult(
            additions=self.additions,
            deletions=self.deletions,
            is_serving=self.is_serving,
            kind=self.kind,
            start_time=self.start_time,
            status=self.status)


def get_change(change_id: Optional[str] = None,
               client_operation_id: Optional[str] = None,
               location: Optional[str] = None,
               managed_zone: Optional[str] = None,
               project: Optional[str] = None,
               opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetChangeResult:
    """
    Fetches the representation of an existing Change.
    """
    __args__ = dict()
    __args__['changeId'] = change_id
    __args__['clientOperationId'] = client_operation_id
    __args__['location'] = location
    __args__['managedZone'] = managed_zone
    __args__['project'] = project
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:dns/v2:getChange', __args__, opts=opts, typ=GetChangeResult).value

    return AwaitableGetChangeResult(
        additions=__ret__.additions,
        deletions=__ret__.deletions,
        is_serving=__ret__.is_serving,
        kind=__ret__.kind,
        start_time=__ret__.start_time,
        status=__ret__.status)


@_utilities.lift_output_func(get_change)
def get_change_output(change_id: Optional[pulumi.Input[str]] = None,
                      client_operation_id: Optional[pulumi.Input[Optional[str]]] = None,
                      location: Optional[pulumi.Input[str]] = None,
                      managed_zone: Optional[pulumi.Input[str]] = None,
                      project: Optional[pulumi.Input[Optional[str]]] = None,
                      opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetChangeResult]:
    """
    Fetches the representation of an existing Change.
    """
    ...
