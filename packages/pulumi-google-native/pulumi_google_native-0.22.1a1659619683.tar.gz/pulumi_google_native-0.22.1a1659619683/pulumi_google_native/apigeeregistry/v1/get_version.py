# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities

__all__ = [
    'GetVersionResult',
    'AwaitableGetVersionResult',
    'get_version',
    'get_version_output',
]

@pulumi.output_type
class GetVersionResult:
    def __init__(__self__, annotations=None, create_time=None, description=None, display_name=None, labels=None, name=None, state=None, update_time=None):
        if annotations and not isinstance(annotations, dict):
            raise TypeError("Expected argument 'annotations' to be a dict")
        pulumi.set(__self__, "annotations", annotations)
        if create_time and not isinstance(create_time, str):
            raise TypeError("Expected argument 'create_time' to be a str")
        pulumi.set(__self__, "create_time", create_time)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if display_name and not isinstance(display_name, str):
            raise TypeError("Expected argument 'display_name' to be a str")
        pulumi.set(__self__, "display_name", display_name)
        if labels and not isinstance(labels, dict):
            raise TypeError("Expected argument 'labels' to be a dict")
        pulumi.set(__self__, "labels", labels)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if state and not isinstance(state, str):
            raise TypeError("Expected argument 'state' to be a str")
        pulumi.set(__self__, "state", state)
        if update_time and not isinstance(update_time, str):
            raise TypeError("Expected argument 'update_time' to be a str")
        pulumi.set(__self__, "update_time", update_time)

    @property
    @pulumi.getter
    def annotations(self) -> Mapping[str, str]:
        """
        Annotations attach non-identifying metadata to resources. Annotation keys and values are less restricted than those of labels, but should be generally used for small values of broad interest. Larger, topic- specific metadata should be stored in Artifacts.
        """
        return pulumi.get(self, "annotations")

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> str:
        """
        Creation timestamp.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        A detailed description.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> str:
        """
        Human-meaningful name.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter
    def labels(self) -> Mapping[str, str]:
        """
        Labels attach identifying metadata to resources. Identifying metadata can be used to filter list operations. Label keys and values can be no longer than 64 characters (Unicode codepoints), can only contain lowercase letters, numeric characters, underscores and dashes. International characters are allowed. No more than 64 user labels can be associated with one resource (System labels are excluded). See https://goo.gl/xmQnxf for more information and examples of labels. System reserved label keys are prefixed with "apigeeregistry.googleapis.com/" and cannot be changed.
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Resource name.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def state(self) -> str:
        """
        A user-definable description of the lifecycle phase of this API version. Format: free-form, but we expect single words that describe API maturity, e.g. "CONCEPT", "DESIGN", "DEVELOPMENT", "STAGING", "PRODUCTION", "DEPRECATED", "RETIRED".
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> str:
        """
        Last update timestamp.
        """
        return pulumi.get(self, "update_time")


class AwaitableGetVersionResult(GetVersionResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetVersionResult(
            annotations=self.annotations,
            create_time=self.create_time,
            description=self.description,
            display_name=self.display_name,
            labels=self.labels,
            name=self.name,
            state=self.state,
            update_time=self.update_time)


def get_version(api_id: Optional[str] = None,
                location: Optional[str] = None,
                project: Optional[str] = None,
                version_id: Optional[str] = None,
                opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetVersionResult:
    """
    GetApiVersion returns a specified version.
    """
    __args__ = dict()
    __args__['apiId'] = api_id
    __args__['location'] = location
    __args__['project'] = project
    __args__['versionId'] = version_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:apigeeregistry/v1:getVersion', __args__, opts=opts, typ=GetVersionResult).value

    return AwaitableGetVersionResult(
        annotations=__ret__.annotations,
        create_time=__ret__.create_time,
        description=__ret__.description,
        display_name=__ret__.display_name,
        labels=__ret__.labels,
        name=__ret__.name,
        state=__ret__.state,
        update_time=__ret__.update_time)


@_utilities.lift_output_func(get_version)
def get_version_output(api_id: Optional[pulumi.Input[str]] = None,
                       location: Optional[pulumi.Input[str]] = None,
                       project: Optional[pulumi.Input[Optional[str]]] = None,
                       version_id: Optional[pulumi.Input[str]] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetVersionResult]:
    """
    GetApiVersion returns a specified version.
    """
    ...
