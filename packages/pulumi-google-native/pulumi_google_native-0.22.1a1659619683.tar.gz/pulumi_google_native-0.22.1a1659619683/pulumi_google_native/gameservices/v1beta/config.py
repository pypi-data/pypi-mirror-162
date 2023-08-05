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
from ._inputs import *

__all__ = ['ConfigArgs', 'Config']

@pulumi.input_type
class ConfigArgs:
    def __init__(__self__, *,
                 config_id: pulumi.Input[str],
                 game_server_deployment_id: pulumi.Input[str],
                 description: Optional[pulumi.Input[str]] = None,
                 fleet_configs: Optional[pulumi.Input[Sequence[pulumi.Input['FleetConfigArgs']]]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 scaling_configs: Optional[pulumi.Input[Sequence[pulumi.Input['ScalingConfigArgs']]]] = None):
        """
        The set of arguments for constructing a Config resource.
        :param pulumi.Input[str] config_id: Required. The ID of the game server config resource to create.
        :param pulumi.Input[str] description: The description of the game server config.
        :param pulumi.Input[Sequence[pulumi.Input['FleetConfigArgs']]] fleet_configs: FleetConfig contains a list of Agones fleet specs. Only one FleetConfig is allowed.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: The labels associated with this game server config. Each label is a key-value pair.
        :param pulumi.Input[str] name: The resource name of the game server config, in the following form: `projects/{project}/locations/{locationId}/gameServerDeployments/{deploymentId}/configs/{configId}`. For example, `projects/my-project/locations/global/gameServerDeployments/my-game/configs/my-config`.
        :param pulumi.Input[Sequence[pulumi.Input['ScalingConfigArgs']]] scaling_configs: The autoscaling settings.
        """
        pulumi.set(__self__, "config_id", config_id)
        pulumi.set(__self__, "game_server_deployment_id", game_server_deployment_id)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if fleet_configs is not None:
            pulumi.set(__self__, "fleet_configs", fleet_configs)
        if labels is not None:
            pulumi.set(__self__, "labels", labels)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if scaling_configs is not None:
            pulumi.set(__self__, "scaling_configs", scaling_configs)

    @property
    @pulumi.getter(name="configId")
    def config_id(self) -> pulumi.Input[str]:
        """
        Required. The ID of the game server config resource to create.
        """
        return pulumi.get(self, "config_id")

    @config_id.setter
    def config_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "config_id", value)

    @property
    @pulumi.getter(name="gameServerDeploymentId")
    def game_server_deployment_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "game_server_deployment_id")

    @game_server_deployment_id.setter
    def game_server_deployment_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "game_server_deployment_id", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the game server config.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="fleetConfigs")
    def fleet_configs(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['FleetConfigArgs']]]]:
        """
        FleetConfig contains a list of Agones fleet specs. Only one FleetConfig is allowed.
        """
        return pulumi.get(self, "fleet_configs")

    @fleet_configs.setter
    def fleet_configs(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['FleetConfigArgs']]]]):
        pulumi.set(self, "fleet_configs", value)

    @property
    @pulumi.getter
    def labels(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        The labels associated with this game server config. Each label is a key-value pair.
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
        The resource name of the game server config, in the following form: `projects/{project}/locations/{locationId}/gameServerDeployments/{deploymentId}/configs/{configId}`. For example, `projects/my-project/locations/global/gameServerDeployments/my-game/configs/my-config`.
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
    @pulumi.getter(name="scalingConfigs")
    def scaling_configs(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ScalingConfigArgs']]]]:
        """
        The autoscaling settings.
        """
        return pulumi.get(self, "scaling_configs")

    @scaling_configs.setter
    def scaling_configs(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ScalingConfigArgs']]]]):
        pulumi.set(self, "scaling_configs", value)


class Config(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 config_id: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 fleet_configs: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FleetConfigArgs']]]]] = None,
                 game_server_deployment_id: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 scaling_configs: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ScalingConfigArgs']]]]] = None,
                 __props__=None):
        """
        Creates a new game server config in a given project, location, and game server deployment. Game server configs are immutable, and are not applied until referenced in the game server deployment rollout resource.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] config_id: Required. The ID of the game server config resource to create.
        :param pulumi.Input[str] description: The description of the game server config.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FleetConfigArgs']]]] fleet_configs: FleetConfig contains a list of Agones fleet specs. Only one FleetConfig is allowed.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: The labels associated with this game server config. Each label is a key-value pair.
        :param pulumi.Input[str] name: The resource name of the game server config, in the following form: `projects/{project}/locations/{locationId}/gameServerDeployments/{deploymentId}/configs/{configId}`. For example, `projects/my-project/locations/global/gameServerDeployments/my-game/configs/my-config`.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ScalingConfigArgs']]]] scaling_configs: The autoscaling settings.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ConfigArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a new game server config in a given project, location, and game server deployment. Game server configs are immutable, and are not applied until referenced in the game server deployment rollout resource.

        :param str resource_name: The name of the resource.
        :param ConfigArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ConfigArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 config_id: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 fleet_configs: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['FleetConfigArgs']]]]] = None,
                 game_server_deployment_id: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 scaling_configs: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ScalingConfigArgs']]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ConfigArgs.__new__(ConfigArgs)

            if config_id is None and not opts.urn:
                raise TypeError("Missing required property 'config_id'")
            __props__.__dict__["config_id"] = config_id
            __props__.__dict__["description"] = description
            __props__.__dict__["fleet_configs"] = fleet_configs
            if game_server_deployment_id is None and not opts.urn:
                raise TypeError("Missing required property 'game_server_deployment_id'")
            __props__.__dict__["game_server_deployment_id"] = game_server_deployment_id
            __props__.__dict__["labels"] = labels
            __props__.__dict__["location"] = location
            __props__.__dict__["name"] = name
            __props__.__dict__["project"] = project
            __props__.__dict__["scaling_configs"] = scaling_configs
            __props__.__dict__["create_time"] = None
            __props__.__dict__["update_time"] = None
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["config_id", "game_server_deployment_id", "location", "project"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(Config, __self__).__init__(
            'google-native:gameservices/v1beta:Config',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Config':
        """
        Get an existing Config resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = ConfigArgs.__new__(ConfigArgs)

        __props__.__dict__["config_id"] = None
        __props__.__dict__["create_time"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["fleet_configs"] = None
        __props__.__dict__["game_server_deployment_id"] = None
        __props__.__dict__["labels"] = None
        __props__.__dict__["location"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["project"] = None
        __props__.__dict__["scaling_configs"] = None
        __props__.__dict__["update_time"] = None
        return Config(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="configId")
    def config_id(self) -> pulumi.Output[str]:
        """
        Required. The ID of the game server config resource to create.
        """
        return pulumi.get(self, "config_id")

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> pulumi.Output[str]:
        """
        The creation time.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        The description of the game server config.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="fleetConfigs")
    def fleet_configs(self) -> pulumi.Output[Sequence['outputs.FleetConfigResponse']]:
        """
        FleetConfig contains a list of Agones fleet specs. Only one FleetConfig is allowed.
        """
        return pulumi.get(self, "fleet_configs")

    @property
    @pulumi.getter(name="gameServerDeploymentId")
    def game_server_deployment_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "game_server_deployment_id")

    @property
    @pulumi.getter
    def labels(self) -> pulumi.Output[Mapping[str, str]]:
        """
        The labels associated with this game server config. Each label is a key-value pair.
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
        The resource name of the game server config, in the following form: `projects/{project}/locations/{locationId}/gameServerDeployments/{deploymentId}/configs/{configId}`. For example, `projects/my-project/locations/global/gameServerDeployments/my-game/configs/my-config`.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        return pulumi.get(self, "project")

    @property
    @pulumi.getter(name="scalingConfigs")
    def scaling_configs(self) -> pulumi.Output[Sequence['outputs.ScalingConfigResponse']]:
        """
        The autoscaling settings.
        """
        return pulumi.get(self, "scaling_configs")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> pulumi.Output[str]:
        """
        The last-modified time.
        """
        return pulumi.get(self, "update_time")

