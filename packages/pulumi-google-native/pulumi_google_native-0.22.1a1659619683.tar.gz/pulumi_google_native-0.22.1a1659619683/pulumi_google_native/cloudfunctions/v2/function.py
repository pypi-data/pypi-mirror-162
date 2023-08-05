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

__all__ = ['FunctionArgs', 'Function']

@pulumi.input_type
class FunctionArgs:
    def __init__(__self__, *,
                 build_config: Optional[pulumi.Input['BuildConfigArgs']] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 environment: Optional[pulumi.Input['FunctionEnvironment']] = None,
                 event_trigger: Optional[pulumi.Input['EventTriggerArgs']] = None,
                 function_id: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 service_config: Optional[pulumi.Input['ServiceConfigArgs']] = None):
        """
        The set of arguments for constructing a Function resource.
        :param pulumi.Input['BuildConfigArgs'] build_config: Describes the Build step of the function that builds a container from the given source.
        :param pulumi.Input[str] description: User-provided description of a function.
        :param pulumi.Input['FunctionEnvironment'] environment: Describe whether the function is gen1 or gen2.
        :param pulumi.Input['EventTriggerArgs'] event_trigger: An Eventarc trigger managed by Google Cloud Functions that fires events in response to a condition in another service.
        :param pulumi.Input[str] function_id: The ID to use for the function, which will become the final component of the function's resource name. This value should be 4-63 characters, and valid characters are /a-z-/.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: Labels associated with this Cloud Function.
        :param pulumi.Input[str] name: A user-defined name of the function. Function names must be unique globally and match pattern `projects/*/locations/*/functions/*`
        :param pulumi.Input['ServiceConfigArgs'] service_config: Describes the Service being deployed. Currently deploys services to Cloud Run (fully managed).
        """
        if build_config is not None:
            pulumi.set(__self__, "build_config", build_config)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if environment is not None:
            pulumi.set(__self__, "environment", environment)
        if event_trigger is not None:
            pulumi.set(__self__, "event_trigger", event_trigger)
        if function_id is not None:
            pulumi.set(__self__, "function_id", function_id)
        if labels is not None:
            pulumi.set(__self__, "labels", labels)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if service_config is not None:
            pulumi.set(__self__, "service_config", service_config)

    @property
    @pulumi.getter(name="buildConfig")
    def build_config(self) -> Optional[pulumi.Input['BuildConfigArgs']]:
        """
        Describes the Build step of the function that builds a container from the given source.
        """
        return pulumi.get(self, "build_config")

    @build_config.setter
    def build_config(self, value: Optional[pulumi.Input['BuildConfigArgs']]):
        pulumi.set(self, "build_config", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        User-provided description of a function.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def environment(self) -> Optional[pulumi.Input['FunctionEnvironment']]:
        """
        Describe whether the function is gen1 or gen2.
        """
        return pulumi.get(self, "environment")

    @environment.setter
    def environment(self, value: Optional[pulumi.Input['FunctionEnvironment']]):
        pulumi.set(self, "environment", value)

    @property
    @pulumi.getter(name="eventTrigger")
    def event_trigger(self) -> Optional[pulumi.Input['EventTriggerArgs']]:
        """
        An Eventarc trigger managed by Google Cloud Functions that fires events in response to a condition in another service.
        """
        return pulumi.get(self, "event_trigger")

    @event_trigger.setter
    def event_trigger(self, value: Optional[pulumi.Input['EventTriggerArgs']]):
        pulumi.set(self, "event_trigger", value)

    @property
    @pulumi.getter(name="functionId")
    def function_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID to use for the function, which will become the final component of the function's resource name. This value should be 4-63 characters, and valid characters are /a-z-/.
        """
        return pulumi.get(self, "function_id")

    @function_id.setter
    def function_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "function_id", value)

    @property
    @pulumi.getter
    def labels(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Labels associated with this Cloud Function.
        """
        return pulumi.get(self, "labels")

    @labels.setter
    def labels(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "labels", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        A user-defined name of the function. Function names must be unique globally and match pattern `projects/*/locations/*/functions/*`
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)

    @property
    @pulumi.getter(name="serviceConfig")
    def service_config(self) -> Optional[pulumi.Input['ServiceConfigArgs']]:
        """
        Describes the Service being deployed. Currently deploys services to Cloud Run (fully managed).
        """
        return pulumi.get(self, "service_config")

    @service_config.setter
    def service_config(self, value: Optional[pulumi.Input['ServiceConfigArgs']]):
        pulumi.set(self, "service_config", value)


class Function(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 build_config: Optional[pulumi.Input[pulumi.InputType['BuildConfigArgs']]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 environment: Optional[pulumi.Input['FunctionEnvironment']] = None,
                 event_trigger: Optional[pulumi.Input[pulumi.InputType['EventTriggerArgs']]] = None,
                 function_id: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 service_config: Optional[pulumi.Input[pulumi.InputType['ServiceConfigArgs']]] = None,
                 __props__=None):
        """
        Creates a new function. If a function with the given name already exists in the specified project, the long running operation will return `ALREADY_EXISTS` error.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['BuildConfigArgs']] build_config: Describes the Build step of the function that builds a container from the given source.
        :param pulumi.Input[str] description: User-provided description of a function.
        :param pulumi.Input['FunctionEnvironment'] environment: Describe whether the function is gen1 or gen2.
        :param pulumi.Input[pulumi.InputType['EventTriggerArgs']] event_trigger: An Eventarc trigger managed by Google Cloud Functions that fires events in response to a condition in another service.
        :param pulumi.Input[str] function_id: The ID to use for the function, which will become the final component of the function's resource name. This value should be 4-63 characters, and valid characters are /a-z-/.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: Labels associated with this Cloud Function.
        :param pulumi.Input[str] name: A user-defined name of the function. Function names must be unique globally and match pattern `projects/*/locations/*/functions/*`
        :param pulumi.Input[pulumi.InputType['ServiceConfigArgs']] service_config: Describes the Service being deployed. Currently deploys services to Cloud Run (fully managed).
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[FunctionArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a new function. If a function with the given name already exists in the specified project, the long running operation will return `ALREADY_EXISTS` error.

        :param str resource_name: The name of the resource.
        :param FunctionArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(FunctionArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 build_config: Optional[pulumi.Input[pulumi.InputType['BuildConfigArgs']]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 environment: Optional[pulumi.Input['FunctionEnvironment']] = None,
                 event_trigger: Optional[pulumi.Input[pulumi.InputType['EventTriggerArgs']]] = None,
                 function_id: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 service_config: Optional[pulumi.Input[pulumi.InputType['ServiceConfigArgs']]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = FunctionArgs.__new__(FunctionArgs)

            __props__.__dict__["build_config"] = build_config
            __props__.__dict__["description"] = description
            __props__.__dict__["environment"] = environment
            __props__.__dict__["event_trigger"] = event_trigger
            __props__.__dict__["function_id"] = function_id
            __props__.__dict__["labels"] = labels
            __props__.__dict__["location"] = location
            __props__.__dict__["name"] = name
            __props__.__dict__["project"] = project
            __props__.__dict__["service_config"] = service_config
            __props__.__dict__["state"] = None
            __props__.__dict__["state_messages"] = None
            __props__.__dict__["update_time"] = None
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["location", "project"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(Function, __self__).__init__(
            'google-native:cloudfunctions/v2:Function',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Function':
        """
        Get an existing Function resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = FunctionArgs.__new__(FunctionArgs)

        __props__.__dict__["build_config"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["environment"] = None
        __props__.__dict__["event_trigger"] = None
        __props__.__dict__["function_id"] = None
        __props__.__dict__["labels"] = None
        __props__.__dict__["location"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["project"] = None
        __props__.__dict__["service_config"] = None
        __props__.__dict__["state"] = None
        __props__.__dict__["state_messages"] = None
        __props__.__dict__["update_time"] = None
        return Function(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="buildConfig")
    def build_config(self) -> pulumi.Output['outputs.BuildConfigResponse']:
        """
        Describes the Build step of the function that builds a container from the given source.
        """
        return pulumi.get(self, "build_config")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        User-provided description of a function.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def environment(self) -> pulumi.Output[str]:
        """
        Describe whether the function is gen1 or gen2.
        """
        return pulumi.get(self, "environment")

    @property
    @pulumi.getter(name="eventTrigger")
    def event_trigger(self) -> pulumi.Output['outputs.EventTriggerResponse']:
        """
        An Eventarc trigger managed by Google Cloud Functions that fires events in response to a condition in another service.
        """
        return pulumi.get(self, "event_trigger")

    @property
    @pulumi.getter(name="functionId")
    def function_id(self) -> pulumi.Output[Optional[str]]:
        """
        The ID to use for the function, which will become the final component of the function's resource name. This value should be 4-63 characters, and valid characters are /a-z-/.
        """
        return pulumi.get(self, "function_id")

    @property
    @pulumi.getter
    def labels(self) -> pulumi.Output[Mapping[str, str]]:
        """
        Labels associated with this Cloud Function.
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        A user-defined name of the function. Function names must be unique globally and match pattern `projects/*/locations/*/functions/*`
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        return pulumi.get(self, "project")

    @property
    @pulumi.getter(name="serviceConfig")
    def service_config(self) -> pulumi.Output['outputs.ServiceConfigResponse']:
        """
        Describes the Service being deployed. Currently deploys services to Cloud Run (fully managed).
        """
        return pulumi.get(self, "service_config")

    @property
    @pulumi.getter
    def state(self) -> pulumi.Output[str]:
        """
        State of the function.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter(name="stateMessages")
    def state_messages(self) -> pulumi.Output[Sequence['outputs.GoogleCloudFunctionsV2StateMessageResponse']]:
        """
        State Messages for this Cloud Function.
        """
        return pulumi.get(self, "state_messages")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> pulumi.Output[str]:
        """
        The last update timestamp of a Cloud Function.
        """
        return pulumi.get(self, "update_time")

