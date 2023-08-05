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
    'GetNodePoolResult',
    'AwaitableGetNodePoolResult',
    'get_node_pool',
    'get_node_pool_output',
]

@pulumi.output_type
class GetNodePoolResult:
    def __init__(__self__, autoscaling=None, conditions=None, config=None, initial_node_count=None, instance_group_urls=None, locations=None, management=None, max_pods_constraint=None, name=None, network_config=None, pod_ipv4_cidr_size=None, self_link=None, status=None, status_message=None, update_info=None, upgrade_settings=None, version=None):
        if autoscaling and not isinstance(autoscaling, dict):
            raise TypeError("Expected argument 'autoscaling' to be a dict")
        pulumi.set(__self__, "autoscaling", autoscaling)
        if conditions and not isinstance(conditions, list):
            raise TypeError("Expected argument 'conditions' to be a list")
        pulumi.set(__self__, "conditions", conditions)
        if config and not isinstance(config, dict):
            raise TypeError("Expected argument 'config' to be a dict")
        pulumi.set(__self__, "config", config)
        if initial_node_count and not isinstance(initial_node_count, int):
            raise TypeError("Expected argument 'initial_node_count' to be a int")
        pulumi.set(__self__, "initial_node_count", initial_node_count)
        if instance_group_urls and not isinstance(instance_group_urls, list):
            raise TypeError("Expected argument 'instance_group_urls' to be a list")
        pulumi.set(__self__, "instance_group_urls", instance_group_urls)
        if locations and not isinstance(locations, list):
            raise TypeError("Expected argument 'locations' to be a list")
        pulumi.set(__self__, "locations", locations)
        if management and not isinstance(management, dict):
            raise TypeError("Expected argument 'management' to be a dict")
        pulumi.set(__self__, "management", management)
        if max_pods_constraint and not isinstance(max_pods_constraint, dict):
            raise TypeError("Expected argument 'max_pods_constraint' to be a dict")
        pulumi.set(__self__, "max_pods_constraint", max_pods_constraint)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if network_config and not isinstance(network_config, dict):
            raise TypeError("Expected argument 'network_config' to be a dict")
        pulumi.set(__self__, "network_config", network_config)
        if pod_ipv4_cidr_size and not isinstance(pod_ipv4_cidr_size, int):
            raise TypeError("Expected argument 'pod_ipv4_cidr_size' to be a int")
        pulumi.set(__self__, "pod_ipv4_cidr_size", pod_ipv4_cidr_size)
        if self_link and not isinstance(self_link, str):
            raise TypeError("Expected argument 'self_link' to be a str")
        pulumi.set(__self__, "self_link", self_link)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)
        if status_message and not isinstance(status_message, str):
            raise TypeError("Expected argument 'status_message' to be a str")
        if status_message is not None:
            warnings.warn("""[Output only] Deprecated. Use conditions instead. Additional information about the current status of this node pool instance, if available.""", DeprecationWarning)
            pulumi.log.warn("""status_message is deprecated: [Output only] Deprecated. Use conditions instead. Additional information about the current status of this node pool instance, if available.""")

        pulumi.set(__self__, "status_message", status_message)
        if update_info and not isinstance(update_info, dict):
            raise TypeError("Expected argument 'update_info' to be a dict")
        pulumi.set(__self__, "update_info", update_info)
        if upgrade_settings and not isinstance(upgrade_settings, dict):
            raise TypeError("Expected argument 'upgrade_settings' to be a dict")
        pulumi.set(__self__, "upgrade_settings", upgrade_settings)
        if version and not isinstance(version, str):
            raise TypeError("Expected argument 'version' to be a str")
        pulumi.set(__self__, "version", version)

    @property
    @pulumi.getter
    def autoscaling(self) -> 'outputs.NodePoolAutoscalingResponse':
        """
        Autoscaler configuration for this NodePool. Autoscaler is enabled only if a valid configuration is present.
        """
        return pulumi.get(self, "autoscaling")

    @property
    @pulumi.getter
    def conditions(self) -> Sequence['outputs.StatusConditionResponse']:
        """
        Which conditions caused the current node pool state.
        """
        return pulumi.get(self, "conditions")

    @property
    @pulumi.getter
    def config(self) -> 'outputs.NodeConfigResponse':
        """
        The node configuration of the pool.
        """
        return pulumi.get(self, "config")

    @property
    @pulumi.getter(name="initialNodeCount")
    def initial_node_count(self) -> int:
        """
        The initial node count for the pool. You must ensure that your Compute Engine [resource quota](https://cloud.google.com/compute/quotas) is sufficient for this number of instances. You must also have available firewall and routes quota.
        """
        return pulumi.get(self, "initial_node_count")

    @property
    @pulumi.getter(name="instanceGroupUrls")
    def instance_group_urls(self) -> Sequence[str]:
        """
        [Output only] The resource URLs of the [managed instance groups](https://cloud.google.com/compute/docs/instance-groups/creating-groups-of-managed-instances) associated with this node pool. During the node pool blue-green upgrade operation, the URLs contain both blue and green resources.
        """
        return pulumi.get(self, "instance_group_urls")

    @property
    @pulumi.getter
    def locations(self) -> Sequence[str]:
        """
        The list of Google Compute Engine [zones](https://cloud.google.com/compute/docs/zones#available) in which the NodePool's nodes should be located. If this value is unspecified during node pool creation, the [Cluster.Locations](https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1/projects.locations.clusters#Cluster.FIELDS.locations) value will be used, instead. Warning: changing node pool locations will result in nodes being added and/or removed.
        """
        return pulumi.get(self, "locations")

    @property
    @pulumi.getter
    def management(self) -> 'outputs.NodeManagementResponse':
        """
        NodeManagement configuration for this NodePool.
        """
        return pulumi.get(self, "management")

    @property
    @pulumi.getter(name="maxPodsConstraint")
    def max_pods_constraint(self) -> 'outputs.MaxPodsConstraintResponse':
        """
        The constraint on the maximum number of pods that can be run simultaneously on a node in the node pool.
        """
        return pulumi.get(self, "max_pods_constraint")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the node pool.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="networkConfig")
    def network_config(self) -> 'outputs.NodeNetworkConfigResponse':
        """
        Networking configuration for this NodePool. If specified, it overrides the cluster-level defaults.
        """
        return pulumi.get(self, "network_config")

    @property
    @pulumi.getter(name="podIpv4CidrSize")
    def pod_ipv4_cidr_size(self) -> int:
        """
        [Output only] The pod CIDR block size per node in this node pool.
        """
        return pulumi.get(self, "pod_ipv4_cidr_size")

    @property
    @pulumi.getter(name="selfLink")
    def self_link(self) -> str:
        """
        [Output only] Server-defined URL for the resource.
        """
        return pulumi.get(self, "self_link")

    @property
    @pulumi.getter
    def status(self) -> str:
        """
        [Output only] The status of the nodes in this pool instance.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter(name="statusMessage")
    def status_message(self) -> str:
        """
        [Output only] Deprecated. Use conditions instead. Additional information about the current status of this node pool instance, if available.
        """
        return pulumi.get(self, "status_message")

    @property
    @pulumi.getter(name="updateInfo")
    def update_info(self) -> 'outputs.UpdateInfoResponse':
        """
        [Output only] Update info contains relevant information during a node pool update.
        """
        return pulumi.get(self, "update_info")

    @property
    @pulumi.getter(name="upgradeSettings")
    def upgrade_settings(self) -> 'outputs.UpgradeSettingsResponse':
        """
        Upgrade settings control disruption and speed of the upgrade.
        """
        return pulumi.get(self, "upgrade_settings")

    @property
    @pulumi.getter
    def version(self) -> str:
        """
        The version of the Kubernetes of this node.
        """
        return pulumi.get(self, "version")


class AwaitableGetNodePoolResult(GetNodePoolResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetNodePoolResult(
            autoscaling=self.autoscaling,
            conditions=self.conditions,
            config=self.config,
            initial_node_count=self.initial_node_count,
            instance_group_urls=self.instance_group_urls,
            locations=self.locations,
            management=self.management,
            max_pods_constraint=self.max_pods_constraint,
            name=self.name,
            network_config=self.network_config,
            pod_ipv4_cidr_size=self.pod_ipv4_cidr_size,
            self_link=self.self_link,
            status=self.status,
            status_message=self.status_message,
            update_info=self.update_info,
            upgrade_settings=self.upgrade_settings,
            version=self.version)


def get_node_pool(cluster_id: Optional[str] = None,
                  location: Optional[str] = None,
                  node_pool_id: Optional[str] = None,
                  project: Optional[str] = None,
                  project_id: Optional[str] = None,
                  zone: Optional[str] = None,
                  opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetNodePoolResult:
    """
    Retrieves the requested node pool.
    """
    __args__ = dict()
    __args__['clusterId'] = cluster_id
    __args__['location'] = location
    __args__['nodePoolId'] = node_pool_id
    __args__['project'] = project
    __args__['projectId'] = project_id
    __args__['zone'] = zone
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:container/v1:getNodePool', __args__, opts=opts, typ=GetNodePoolResult).value

    return AwaitableGetNodePoolResult(
        autoscaling=__ret__.autoscaling,
        conditions=__ret__.conditions,
        config=__ret__.config,
        initial_node_count=__ret__.initial_node_count,
        instance_group_urls=__ret__.instance_group_urls,
        locations=__ret__.locations,
        management=__ret__.management,
        max_pods_constraint=__ret__.max_pods_constraint,
        name=__ret__.name,
        network_config=__ret__.network_config,
        pod_ipv4_cidr_size=__ret__.pod_ipv4_cidr_size,
        self_link=__ret__.self_link,
        status=__ret__.status,
        status_message=__ret__.status_message,
        update_info=__ret__.update_info,
        upgrade_settings=__ret__.upgrade_settings,
        version=__ret__.version)


@_utilities.lift_output_func(get_node_pool)
def get_node_pool_output(cluster_id: Optional[pulumi.Input[str]] = None,
                         location: Optional[pulumi.Input[str]] = None,
                         node_pool_id: Optional[pulumi.Input[str]] = None,
                         project: Optional[pulumi.Input[Optional[str]]] = None,
                         project_id: Optional[pulumi.Input[Optional[str]]] = None,
                         zone: Optional[pulumi.Input[Optional[str]]] = None,
                         opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetNodePoolResult]:
    """
    Retrieves the requested node pool.
    """
    ...
