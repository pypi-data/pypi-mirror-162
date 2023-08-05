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

__all__ = ['SessionEntityTypeArgs', 'SessionEntityType']

@pulumi.input_type
class SessionEntityTypeArgs:
    def __init__(__self__, *,
                 entities: pulumi.Input[Sequence[pulumi.Input['GoogleCloudDialogflowV2EntityTypeEntityArgs']]],
                 entity_override_mode: pulumi.Input['SessionEntityTypeEntityOverrideMode'],
                 environment_id: pulumi.Input[str],
                 name: pulumi.Input[str],
                 session_id: pulumi.Input[str],
                 user_id: pulumi.Input[str],
                 location: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a SessionEntityType resource.
        :param pulumi.Input[Sequence[pulumi.Input['GoogleCloudDialogflowV2EntityTypeEntityArgs']]] entities: The collection of entities associated with this session entity type.
        :param pulumi.Input['SessionEntityTypeEntityOverrideMode'] entity_override_mode: Indicates whether the additional data should override or supplement the custom entity type definition.
        :param pulumi.Input[str] name: The unique identifier of this session entity type. Format: `projects//agent/sessions//entityTypes/`, or `projects//agent/environments//users//sessions//entityTypes/`. If `Environment ID` is not specified, we assume default 'draft' environment. If `User ID` is not specified, we assume default '-' user. `` must be the display name of an existing entity type in the same agent that will be overridden or supplemented.
        """
        pulumi.set(__self__, "entities", entities)
        pulumi.set(__self__, "entity_override_mode", entity_override_mode)
        pulumi.set(__self__, "environment_id", environment_id)
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "session_id", session_id)
        pulumi.set(__self__, "user_id", user_id)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if project is not None:
            pulumi.set(__self__, "project", project)

    @property
    @pulumi.getter
    def entities(self) -> pulumi.Input[Sequence[pulumi.Input['GoogleCloudDialogflowV2EntityTypeEntityArgs']]]:
        """
        The collection of entities associated with this session entity type.
        """
        return pulumi.get(self, "entities")

    @entities.setter
    def entities(self, value: pulumi.Input[Sequence[pulumi.Input['GoogleCloudDialogflowV2EntityTypeEntityArgs']]]):
        pulumi.set(self, "entities", value)

    @property
    @pulumi.getter(name="entityOverrideMode")
    def entity_override_mode(self) -> pulumi.Input['SessionEntityTypeEntityOverrideMode']:
        """
        Indicates whether the additional data should override or supplement the custom entity type definition.
        """
        return pulumi.get(self, "entity_override_mode")

    @entity_override_mode.setter
    def entity_override_mode(self, value: pulumi.Input['SessionEntityTypeEntityOverrideMode']):
        pulumi.set(self, "entity_override_mode", value)

    @property
    @pulumi.getter(name="environmentId")
    def environment_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "environment_id")

    @environment_id.setter
    def environment_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "environment_id", value)

    @property
    @pulumi.getter
    def name(self) -> pulumi.Input[str]:
        """
        The unique identifier of this session entity type. Format: `projects//agent/sessions//entityTypes/`, or `projects//agent/environments//users//sessions//entityTypes/`. If `Environment ID` is not specified, we assume default 'draft' environment. If `User ID` is not specified, we assume default '-' user. `` must be the display name of an existing entity type in the same agent that will be overridden or supplemented.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: pulumi.Input[str]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="sessionId")
    def session_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "session_id")

    @session_id.setter
    def session_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "session_id", value)

    @property
    @pulumi.getter(name="userId")
    def user_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "user_id")

    @user_id.setter
    def user_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "user_id", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)


class SessionEntityType(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 entities: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['GoogleCloudDialogflowV2EntityTypeEntityArgs']]]]] = None,
                 entity_override_mode: Optional[pulumi.Input['SessionEntityTypeEntityOverrideMode']] = None,
                 environment_id: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 session_id: Optional[pulumi.Input[str]] = None,
                 user_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Creates a session entity type. If the specified session entity type already exists, overrides the session entity type. This method doesn't work with Google Assistant integration. Contact Dialogflow support if you need to use session entities with Google Assistant integration.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['GoogleCloudDialogflowV2EntityTypeEntityArgs']]]] entities: The collection of entities associated with this session entity type.
        :param pulumi.Input['SessionEntityTypeEntityOverrideMode'] entity_override_mode: Indicates whether the additional data should override or supplement the custom entity type definition.
        :param pulumi.Input[str] name: The unique identifier of this session entity type. Format: `projects//agent/sessions//entityTypes/`, or `projects//agent/environments//users//sessions//entityTypes/`. If `Environment ID` is not specified, we assume default 'draft' environment. If `User ID` is not specified, we assume default '-' user. `` must be the display name of an existing entity type in the same agent that will be overridden or supplemented.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: SessionEntityTypeArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a session entity type. If the specified session entity type already exists, overrides the session entity type. This method doesn't work with Google Assistant integration. Contact Dialogflow support if you need to use session entities with Google Assistant integration.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param SessionEntityTypeArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(SessionEntityTypeArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 entities: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['GoogleCloudDialogflowV2EntityTypeEntityArgs']]]]] = None,
                 entity_override_mode: Optional[pulumi.Input['SessionEntityTypeEntityOverrideMode']] = None,
                 environment_id: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 session_id: Optional[pulumi.Input[str]] = None,
                 user_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = SessionEntityTypeArgs.__new__(SessionEntityTypeArgs)

            if entities is None and not opts.urn:
                raise TypeError("Missing required property 'entities'")
            __props__.__dict__["entities"] = entities
            if entity_override_mode is None and not opts.urn:
                raise TypeError("Missing required property 'entity_override_mode'")
            __props__.__dict__["entity_override_mode"] = entity_override_mode
            if environment_id is None and not opts.urn:
                raise TypeError("Missing required property 'environment_id'")
            __props__.__dict__["environment_id"] = environment_id
            __props__.__dict__["location"] = location
            if name is None and not opts.urn:
                raise TypeError("Missing required property 'name'")
            __props__.__dict__["name"] = name
            __props__.__dict__["project"] = project
            if session_id is None and not opts.urn:
                raise TypeError("Missing required property 'session_id'")
            __props__.__dict__["session_id"] = session_id
            if user_id is None and not opts.urn:
                raise TypeError("Missing required property 'user_id'")
            __props__.__dict__["user_id"] = user_id
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["environment_id", "location", "project", "session_id", "user_id"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(SessionEntityType, __self__).__init__(
            'google-native:dialogflow/v2:SessionEntityType',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'SessionEntityType':
        """
        Get an existing SessionEntityType resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = SessionEntityTypeArgs.__new__(SessionEntityTypeArgs)

        __props__.__dict__["entities"] = None
        __props__.__dict__["entity_override_mode"] = None
        __props__.__dict__["environment_id"] = None
        __props__.__dict__["location"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["project"] = None
        __props__.__dict__["session_id"] = None
        __props__.__dict__["user_id"] = None
        return SessionEntityType(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def entities(self) -> pulumi.Output[Sequence['outputs.GoogleCloudDialogflowV2EntityTypeEntityResponse']]:
        """
        The collection of entities associated with this session entity type.
        """
        return pulumi.get(self, "entities")

    @property
    @pulumi.getter(name="entityOverrideMode")
    def entity_override_mode(self) -> pulumi.Output[str]:
        """
        Indicates whether the additional data should override or supplement the custom entity type definition.
        """
        return pulumi.get(self, "entity_override_mode")

    @property
    @pulumi.getter(name="environmentId")
    def environment_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "environment_id")

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The unique identifier of this session entity type. Format: `projects//agent/sessions//entityTypes/`, or `projects//agent/environments//users//sessions//entityTypes/`. If `Environment ID` is not specified, we assume default 'draft' environment. If `User ID` is not specified, we assume default '-' user. `` must be the display name of an existing entity type in the same agent that will be overridden or supplemented.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        return pulumi.get(self, "project")

    @property
    @pulumi.getter(name="sessionId")
    def session_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "session_id")

    @property
    @pulumi.getter(name="userId")
    def user_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "user_id")

