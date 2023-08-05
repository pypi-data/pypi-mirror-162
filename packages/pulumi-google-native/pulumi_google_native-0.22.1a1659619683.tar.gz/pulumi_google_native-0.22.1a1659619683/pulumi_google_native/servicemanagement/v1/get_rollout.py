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
    'GetRolloutResult',
    'AwaitableGetRolloutResult',
    'get_rollout',
    'get_rollout_output',
]

@pulumi.output_type
class GetRolloutResult:
    def __init__(__self__, create_time=None, created_by=None, delete_service_strategy=None, rollout_id=None, service_name=None, status=None, traffic_percent_strategy=None):
        if create_time and not isinstance(create_time, str):
            raise TypeError("Expected argument 'create_time' to be a str")
        pulumi.set(__self__, "create_time", create_time)
        if created_by and not isinstance(created_by, str):
            raise TypeError("Expected argument 'created_by' to be a str")
        pulumi.set(__self__, "created_by", created_by)
        if delete_service_strategy and not isinstance(delete_service_strategy, dict):
            raise TypeError("Expected argument 'delete_service_strategy' to be a dict")
        pulumi.set(__self__, "delete_service_strategy", delete_service_strategy)
        if rollout_id and not isinstance(rollout_id, str):
            raise TypeError("Expected argument 'rollout_id' to be a str")
        pulumi.set(__self__, "rollout_id", rollout_id)
        if service_name and not isinstance(service_name, str):
            raise TypeError("Expected argument 'service_name' to be a str")
        pulumi.set(__self__, "service_name", service_name)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)
        if traffic_percent_strategy and not isinstance(traffic_percent_strategy, dict):
            raise TypeError("Expected argument 'traffic_percent_strategy' to be a dict")
        pulumi.set(__self__, "traffic_percent_strategy", traffic_percent_strategy)

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> str:
        """
        Creation time of the rollout. Readonly.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter(name="createdBy")
    def created_by(self) -> str:
        """
        The user who created the Rollout. Readonly.
        """
        return pulumi.get(self, "created_by")

    @property
    @pulumi.getter(name="deleteServiceStrategy")
    def delete_service_strategy(self) -> 'outputs.DeleteServiceStrategyResponse':
        """
        The strategy associated with a rollout to delete a `ManagedService`. Readonly.
        """
        return pulumi.get(self, "delete_service_strategy")

    @property
    @pulumi.getter(name="rolloutId")
    def rollout_id(self) -> str:
        """
        Optional. Unique identifier of this Rollout. Must be no longer than 63 characters and only lower case letters, digits, '.', '_' and '-' are allowed. If not specified by client, the server will generate one. The generated id will have the form of , where "date" is the create date in ISO 8601 format. "revision number" is a monotonically increasing positive number that is reset every day for each service. An example of the generated rollout_id is '2016-02-16r1'
        """
        return pulumi.get(self, "rollout_id")

    @property
    @pulumi.getter(name="serviceName")
    def service_name(self) -> str:
        """
        The name of the service associated with this Rollout.
        """
        return pulumi.get(self, "service_name")

    @property
    @pulumi.getter
    def status(self) -> str:
        """
        The status of this rollout. Readonly. In case of a failed rollout, the system will automatically rollback to the current Rollout version. Readonly.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter(name="trafficPercentStrategy")
    def traffic_percent_strategy(self) -> 'outputs.TrafficPercentStrategyResponse':
        """
        Google Service Control selects service configurations based on traffic percentage.
        """
        return pulumi.get(self, "traffic_percent_strategy")


class AwaitableGetRolloutResult(GetRolloutResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetRolloutResult(
            create_time=self.create_time,
            created_by=self.created_by,
            delete_service_strategy=self.delete_service_strategy,
            rollout_id=self.rollout_id,
            service_name=self.service_name,
            status=self.status,
            traffic_percent_strategy=self.traffic_percent_strategy)


def get_rollout(rollout_id: Optional[str] = None,
                service_name: Optional[str] = None,
                opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetRolloutResult:
    """
    Gets a service configuration rollout.
    """
    __args__ = dict()
    __args__['rolloutId'] = rollout_id
    __args__['serviceName'] = service_name
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:servicemanagement/v1:getRollout', __args__, opts=opts, typ=GetRolloutResult).value

    return AwaitableGetRolloutResult(
        create_time=__ret__.create_time,
        created_by=__ret__.created_by,
        delete_service_strategy=__ret__.delete_service_strategy,
        rollout_id=__ret__.rollout_id,
        service_name=__ret__.service_name,
        status=__ret__.status,
        traffic_percent_strategy=__ret__.traffic_percent_strategy)


@_utilities.lift_output_func(get_rollout)
def get_rollout_output(rollout_id: Optional[pulumi.Input[str]] = None,
                       service_name: Optional[pulumi.Input[str]] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetRolloutResult]:
    """
    Gets a service configuration rollout.
    """
    ...
