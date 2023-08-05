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
    'GetCompositeTypeResult',
    'AwaitableGetCompositeTypeResult',
    'get_composite_type',
    'get_composite_type_output',
]

@pulumi.output_type
class GetCompositeTypeResult:
    def __init__(__self__, description=None, insert_time=None, labels=None, name=None, operation=None, self_link=None, status=None, template_contents=None):
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if insert_time and not isinstance(insert_time, str):
            raise TypeError("Expected argument 'insert_time' to be a str")
        pulumi.set(__self__, "insert_time", insert_time)
        if labels and not isinstance(labels, list):
            raise TypeError("Expected argument 'labels' to be a list")
        pulumi.set(__self__, "labels", labels)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if operation and not isinstance(operation, dict):
            raise TypeError("Expected argument 'operation' to be a dict")
        pulumi.set(__self__, "operation", operation)
        if self_link and not isinstance(self_link, str):
            raise TypeError("Expected argument 'self_link' to be a str")
        pulumi.set(__self__, "self_link", self_link)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)
        if template_contents and not isinstance(template_contents, dict):
            raise TypeError("Expected argument 'template_contents' to be a dict")
        pulumi.set(__self__, "template_contents", template_contents)

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        An optional textual description of the resource; provided by the client when the resource is created.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="insertTime")
    def insert_time(self) -> str:
        """
        Creation timestamp in RFC3339 text format.
        """
        return pulumi.get(self, "insert_time")

    @property
    @pulumi.getter
    def labels(self) -> Sequence['outputs.CompositeTypeLabelEntryResponse']:
        """
        Map of labels; provided by the client when the resource is created or updated. Specifically: Label keys must be between 1 and 63 characters long and must conform to the following regular expression: `[a-z]([-a-z0-9]*[a-z0-9])?` Label values must be between 0 and 63 characters long and must conform to the regular expression `([a-z]([-a-z0-9]*[a-z0-9])?)?`.
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the composite type, must follow the expression: `[a-z]([-a-z0-9_.]{0,61}[a-z0-9])?`.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def operation(self) -> 'outputs.OperationResponse':
        """
        The Operation that most recently ran, or is currently running, on this composite type.
        """
        return pulumi.get(self, "operation")

    @property
    @pulumi.getter(name="selfLink")
    def self_link(self) -> str:
        """
        Server defined URL for the resource.
        """
        return pulumi.get(self, "self_link")

    @property
    @pulumi.getter
    def status(self) -> str:
        return pulumi.get(self, "status")

    @property
    @pulumi.getter(name="templateContents")
    def template_contents(self) -> 'outputs.TemplateContentsResponse':
        """
        Files for the template type.
        """
        return pulumi.get(self, "template_contents")


class AwaitableGetCompositeTypeResult(GetCompositeTypeResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetCompositeTypeResult(
            description=self.description,
            insert_time=self.insert_time,
            labels=self.labels,
            name=self.name,
            operation=self.operation,
            self_link=self.self_link,
            status=self.status,
            template_contents=self.template_contents)


def get_composite_type(composite_type: Optional[str] = None,
                       project: Optional[str] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetCompositeTypeResult:
    """
    Gets information about a specific composite type.
    """
    __args__ = dict()
    __args__['compositeType'] = composite_type
    __args__['project'] = project
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:deploymentmanager/alpha:getCompositeType', __args__, opts=opts, typ=GetCompositeTypeResult).value

    return AwaitableGetCompositeTypeResult(
        description=__ret__.description,
        insert_time=__ret__.insert_time,
        labels=__ret__.labels,
        name=__ret__.name,
        operation=__ret__.operation,
        self_link=__ret__.self_link,
        status=__ret__.status,
        template_contents=__ret__.template_contents)


@_utilities.lift_output_func(get_composite_type)
def get_composite_type_output(composite_type: Optional[pulumi.Input[str]] = None,
                              project: Optional[pulumi.Input[Optional[str]]] = None,
                              opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetCompositeTypeResult]:
    """
    Gets information about a specific composite type.
    """
    ...
