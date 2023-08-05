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
    'GetTagResult',
    'AwaitableGetTagResult',
    'get_tag',
    'get_tag_output',
]

@pulumi.output_type
class GetTagResult:
    def __init__(__self__, name=None, version=None):
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if version and not isinstance(version, str):
            raise TypeError("Expected argument 'version' to be a str")
        pulumi.set(__self__, "version", version)

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the tag, for example: "projects/p1/locations/us-central1/repositories/repo1/packages/pkg1/tags/tag1". If the package part contains slashes, the slashes are escaped. The tag part can only have characters in [a-zA-Z0-9\\-._~:@], anything else must be URL encoded.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def version(self) -> str:
        """
        The name of the version the tag refers to, for example: "projects/p1/locations/us-central1/repositories/repo1/packages/pkg1/versions/sha256:5243811" If the package or version ID parts contain slashes, the slashes are escaped.
        """
        return pulumi.get(self, "version")


class AwaitableGetTagResult(GetTagResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetTagResult(
            name=self.name,
            version=self.version)


def get_tag(location: Optional[str] = None,
            package_id: Optional[str] = None,
            project: Optional[str] = None,
            repository_id: Optional[str] = None,
            tag_id: Optional[str] = None,
            opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetTagResult:
    """
    Gets a tag.
    """
    __args__ = dict()
    __args__['location'] = location
    __args__['packageId'] = package_id
    __args__['project'] = project
    __args__['repositoryId'] = repository_id
    __args__['tagId'] = tag_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:artifactregistry/v1beta1:getTag', __args__, opts=opts, typ=GetTagResult).value

    return AwaitableGetTagResult(
        name=__ret__.name,
        version=__ret__.version)


@_utilities.lift_output_func(get_tag)
def get_tag_output(location: Optional[pulumi.Input[str]] = None,
                   package_id: Optional[pulumi.Input[str]] = None,
                   project: Optional[pulumi.Input[Optional[str]]] = None,
                   repository_id: Optional[pulumi.Input[str]] = None,
                   tag_id: Optional[pulumi.Input[str]] = None,
                   opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetTagResult]:
    """
    Gets a tag.
    """
    ...
