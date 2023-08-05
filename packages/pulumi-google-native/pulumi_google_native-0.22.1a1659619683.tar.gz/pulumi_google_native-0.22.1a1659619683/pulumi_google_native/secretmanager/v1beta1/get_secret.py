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
    'GetSecretResult',
    'AwaitableGetSecretResult',
    'get_secret',
    'get_secret_output',
]

@pulumi.output_type
class GetSecretResult:
    def __init__(__self__, create_time=None, labels=None, name=None, replication=None):
        if create_time and not isinstance(create_time, str):
            raise TypeError("Expected argument 'create_time' to be a str")
        pulumi.set(__self__, "create_time", create_time)
        if labels and not isinstance(labels, dict):
            raise TypeError("Expected argument 'labels' to be a dict")
        pulumi.set(__self__, "labels", labels)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if replication and not isinstance(replication, dict):
            raise TypeError("Expected argument 'replication' to be a dict")
        pulumi.set(__self__, "replication", replication)

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> str:
        """
        The time at which the Secret was created.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter
    def labels(self) -> Mapping[str, str]:
        """
        The labels assigned to this Secret. Label keys must be between 1 and 63 characters long, have a UTF-8 encoding of maximum 128 bytes, and must conform to the following PCRE regular expression: `\\p{Ll}\\p{Lo}{0,62}` Label values must be between 0 and 63 characters long, have a UTF-8 encoding of maximum 128 bytes, and must conform to the following PCRE regular expression: `[\\p{Ll}\\p{Lo}\\p{N}_-]{0,63}` No more than 64 labels can be assigned to a given resource.
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The resource name of the Secret in the format `projects/*/secrets/*`.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def replication(self) -> 'outputs.ReplicationResponse':
        """
        Immutable. The replication policy of the secret data attached to the Secret. The replication policy cannot be changed after the Secret has been created.
        """
        return pulumi.get(self, "replication")


class AwaitableGetSecretResult(GetSecretResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetSecretResult(
            create_time=self.create_time,
            labels=self.labels,
            name=self.name,
            replication=self.replication)


def get_secret(project: Optional[str] = None,
               secret_id: Optional[str] = None,
               opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetSecretResult:
    """
    Gets metadata for a given Secret.
    """
    __args__ = dict()
    __args__['project'] = project
    __args__['secretId'] = secret_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:secretmanager/v1beta1:getSecret', __args__, opts=opts, typ=GetSecretResult).value

    return AwaitableGetSecretResult(
        create_time=__ret__.create_time,
        labels=__ret__.labels,
        name=__ret__.name,
        replication=__ret__.replication)


@_utilities.lift_output_func(get_secret)
def get_secret_output(project: Optional[pulumi.Input[Optional[str]]] = None,
                      secret_id: Optional[pulumi.Input[str]] = None,
                      opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetSecretResult]:
    """
    Gets metadata for a given Secret.
    """
    ...
