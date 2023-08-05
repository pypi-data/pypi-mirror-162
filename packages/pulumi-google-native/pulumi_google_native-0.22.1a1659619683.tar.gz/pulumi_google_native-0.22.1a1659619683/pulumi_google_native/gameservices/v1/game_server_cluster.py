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

__all__ = ['GameServerClusterArgs', 'GameServerCluster']

@pulumi.input_type
class GameServerClusterArgs:
    def __init__(__self__, *,
                 game_server_cluster_id: pulumi.Input[str],
                 realm_id: pulumi.Input[str],
                 connection_info: Optional[pulumi.Input['GameServerClusterConnectionInfoArgs']] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 etag: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a GameServerCluster resource.
        :param pulumi.Input[str] game_server_cluster_id: Required. The ID of the game server cluster resource to create.
        :param pulumi.Input['GameServerClusterConnectionInfoArgs'] connection_info: The game server cluster connection information. This information is used to manage game server clusters.
        :param pulumi.Input[str] description: Human readable description of the cluster.
        :param pulumi.Input[str] etag: Used to perform consistent read-modify-write updates. If not set, a blind "overwrite" update happens.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: The labels associated with this game server cluster. Each label is a key-value pair.
        :param pulumi.Input[str] name: The resource name of the game server cluster, in the following form: `projects/{project}/locations/{locationId}/realms/{realmId}/gameServerClusters/{gameServerClusterId}`. For example, `projects/my-project/locations/global/realms/zanzibar/gameServerClusters/my-gke-cluster`.
        """
        pulumi.set(__self__, "game_server_cluster_id", game_server_cluster_id)
        pulumi.set(__self__, "realm_id", realm_id)
        if connection_info is not None:
            pulumi.set(__self__, "connection_info", connection_info)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if etag is not None:
            pulumi.set(__self__, "etag", etag)
        if labels is not None:
            pulumi.set(__self__, "labels", labels)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if project is not None:
            pulumi.set(__self__, "project", project)

    @property
    @pulumi.getter(name="gameServerClusterId")
    def game_server_cluster_id(self) -> pulumi.Input[str]:
        """
        Required. The ID of the game server cluster resource to create.
        """
        return pulumi.get(self, "game_server_cluster_id")

    @game_server_cluster_id.setter
    def game_server_cluster_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "game_server_cluster_id", value)

    @property
    @pulumi.getter(name="realmId")
    def realm_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "realm_id")

    @realm_id.setter
    def realm_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "realm_id", value)

    @property
    @pulumi.getter(name="connectionInfo")
    def connection_info(self) -> Optional[pulumi.Input['GameServerClusterConnectionInfoArgs']]:
        """
        The game server cluster connection information. This information is used to manage game server clusters.
        """
        return pulumi.get(self, "connection_info")

    @connection_info.setter
    def connection_info(self, value: Optional[pulumi.Input['GameServerClusterConnectionInfoArgs']]):
        pulumi.set(self, "connection_info", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Human readable description of the cluster.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def etag(self) -> Optional[pulumi.Input[str]]:
        """
        Used to perform consistent read-modify-write updates. If not set, a blind "overwrite" update happens.
        """
        return pulumi.get(self, "etag")

    @etag.setter
    def etag(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "etag", value)

    @property
    @pulumi.getter
    def labels(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        The labels associated with this game server cluster. Each label is a key-value pair.
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
        The resource name of the game server cluster, in the following form: `projects/{project}/locations/{locationId}/realms/{realmId}/gameServerClusters/{gameServerClusterId}`. For example, `projects/my-project/locations/global/realms/zanzibar/gameServerClusters/my-gke-cluster`.
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


class GameServerCluster(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 connection_info: Optional[pulumi.Input[pulumi.InputType['GameServerClusterConnectionInfoArgs']]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 etag: Optional[pulumi.Input[str]] = None,
                 game_server_cluster_id: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 realm_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Creates a new game server cluster in a given project and location.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['GameServerClusterConnectionInfoArgs']] connection_info: The game server cluster connection information. This information is used to manage game server clusters.
        :param pulumi.Input[str] description: Human readable description of the cluster.
        :param pulumi.Input[str] etag: Used to perform consistent read-modify-write updates. If not set, a blind "overwrite" update happens.
        :param pulumi.Input[str] game_server_cluster_id: Required. The ID of the game server cluster resource to create.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] labels: The labels associated with this game server cluster. Each label is a key-value pair.
        :param pulumi.Input[str] name: The resource name of the game server cluster, in the following form: `projects/{project}/locations/{locationId}/realms/{realmId}/gameServerClusters/{gameServerClusterId}`. For example, `projects/my-project/locations/global/realms/zanzibar/gameServerClusters/my-gke-cluster`.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: GameServerClusterArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a new game server cluster in a given project and location.

        :param str resource_name: The name of the resource.
        :param GameServerClusterArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(GameServerClusterArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 connection_info: Optional[pulumi.Input[pulumi.InputType['GameServerClusterConnectionInfoArgs']]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 etag: Optional[pulumi.Input[str]] = None,
                 game_server_cluster_id: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 realm_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = GameServerClusterArgs.__new__(GameServerClusterArgs)

            __props__.__dict__["connection_info"] = connection_info
            __props__.__dict__["description"] = description
            __props__.__dict__["etag"] = etag
            if game_server_cluster_id is None and not opts.urn:
                raise TypeError("Missing required property 'game_server_cluster_id'")
            __props__.__dict__["game_server_cluster_id"] = game_server_cluster_id
            __props__.__dict__["labels"] = labels
            __props__.__dict__["location"] = location
            __props__.__dict__["name"] = name
            __props__.__dict__["project"] = project
            if realm_id is None and not opts.urn:
                raise TypeError("Missing required property 'realm_id'")
            __props__.__dict__["realm_id"] = realm_id
            __props__.__dict__["cluster_state"] = None
            __props__.__dict__["create_time"] = None
            __props__.__dict__["update_time"] = None
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["game_server_cluster_id", "location", "project", "realm_id"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(GameServerCluster, __self__).__init__(
            'google-native:gameservices/v1:GameServerCluster',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'GameServerCluster':
        """
        Get an existing GameServerCluster resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = GameServerClusterArgs.__new__(GameServerClusterArgs)

        __props__.__dict__["cluster_state"] = None
        __props__.__dict__["connection_info"] = None
        __props__.__dict__["create_time"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["etag"] = None
        __props__.__dict__["game_server_cluster_id"] = None
        __props__.__dict__["labels"] = None
        __props__.__dict__["location"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["project"] = None
        __props__.__dict__["realm_id"] = None
        __props__.__dict__["update_time"] = None
        return GameServerCluster(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="clusterState")
    def cluster_state(self) -> pulumi.Output['outputs.KubernetesClusterStateResponse']:
        """
        The state of the Kubernetes cluster in preview. This will be available if view is set to FULL in the relevant list/get/preview request.
        """
        return pulumi.get(self, "cluster_state")

    @property
    @pulumi.getter(name="connectionInfo")
    def connection_info(self) -> pulumi.Output['outputs.GameServerClusterConnectionInfoResponse']:
        """
        The game server cluster connection information. This information is used to manage game server clusters.
        """
        return pulumi.get(self, "connection_info")

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
        Human readable description of the cluster.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def etag(self) -> pulumi.Output[str]:
        """
        Used to perform consistent read-modify-write updates. If not set, a blind "overwrite" update happens.
        """
        return pulumi.get(self, "etag")

    @property
    @pulumi.getter(name="gameServerClusterId")
    def game_server_cluster_id(self) -> pulumi.Output[str]:
        """
        Required. The ID of the game server cluster resource to create.
        """
        return pulumi.get(self, "game_server_cluster_id")

    @property
    @pulumi.getter
    def labels(self) -> pulumi.Output[Mapping[str, str]]:
        """
        The labels associated with this game server cluster. Each label is a key-value pair.
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
        The resource name of the game server cluster, in the following form: `projects/{project}/locations/{locationId}/realms/{realmId}/gameServerClusters/{gameServerClusterId}`. For example, `projects/my-project/locations/global/realms/zanzibar/gameServerClusters/my-gke-cluster`.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        return pulumi.get(self, "project")

    @property
    @pulumi.getter(name="realmId")
    def realm_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "realm_id")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> pulumi.Output[str]:
        """
        The last-modified time.
        """
        return pulumi.get(self, "update_time")

