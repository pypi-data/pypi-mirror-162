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
    'GetNodeResult',
    'AwaitableGetNodeResult',
    'get_node',
    'get_node_output',
]

@pulumi.output_type
class GetNodeResult:
    def __init__(__self__, accelerator_type=None, api_version=None, cidr_block=None, create_time=None, data_disks=None, description=None, health=None, health_description=None, labels=None, metadata=None, name=None, network_config=None, network_endpoints=None, runtime_version=None, scheduling_config=None, service_account=None, state=None, symptoms=None, tags=None):
        if accelerator_type and not isinstance(accelerator_type, str):
            raise TypeError("Expected argument 'accelerator_type' to be a str")
        pulumi.set(__self__, "accelerator_type", accelerator_type)
        if api_version and not isinstance(api_version, str):
            raise TypeError("Expected argument 'api_version' to be a str")
        pulumi.set(__self__, "api_version", api_version)
        if cidr_block and not isinstance(cidr_block, str):
            raise TypeError("Expected argument 'cidr_block' to be a str")
        pulumi.set(__self__, "cidr_block", cidr_block)
        if create_time and not isinstance(create_time, str):
            raise TypeError("Expected argument 'create_time' to be a str")
        pulumi.set(__self__, "create_time", create_time)
        if data_disks and not isinstance(data_disks, list):
            raise TypeError("Expected argument 'data_disks' to be a list")
        pulumi.set(__self__, "data_disks", data_disks)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if health and not isinstance(health, str):
            raise TypeError("Expected argument 'health' to be a str")
        pulumi.set(__self__, "health", health)
        if health_description and not isinstance(health_description, str):
            raise TypeError("Expected argument 'health_description' to be a str")
        pulumi.set(__self__, "health_description", health_description)
        if labels and not isinstance(labels, dict):
            raise TypeError("Expected argument 'labels' to be a dict")
        pulumi.set(__self__, "labels", labels)
        if metadata and not isinstance(metadata, dict):
            raise TypeError("Expected argument 'metadata' to be a dict")
        pulumi.set(__self__, "metadata", metadata)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if network_config and not isinstance(network_config, dict):
            raise TypeError("Expected argument 'network_config' to be a dict")
        pulumi.set(__self__, "network_config", network_config)
        if network_endpoints and not isinstance(network_endpoints, list):
            raise TypeError("Expected argument 'network_endpoints' to be a list")
        pulumi.set(__self__, "network_endpoints", network_endpoints)
        if runtime_version and not isinstance(runtime_version, str):
            raise TypeError("Expected argument 'runtime_version' to be a str")
        pulumi.set(__self__, "runtime_version", runtime_version)
        if scheduling_config and not isinstance(scheduling_config, dict):
            raise TypeError("Expected argument 'scheduling_config' to be a dict")
        pulumi.set(__self__, "scheduling_config", scheduling_config)
        if service_account and not isinstance(service_account, dict):
            raise TypeError("Expected argument 'service_account' to be a dict")
        pulumi.set(__self__, "service_account", service_account)
        if state and not isinstance(state, str):
            raise TypeError("Expected argument 'state' to be a str")
        pulumi.set(__self__, "state", state)
        if symptoms and not isinstance(symptoms, list):
            raise TypeError("Expected argument 'symptoms' to be a list")
        pulumi.set(__self__, "symptoms", symptoms)
        if tags and not isinstance(tags, list):
            raise TypeError("Expected argument 'tags' to be a list")
        pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="acceleratorType")
    def accelerator_type(self) -> str:
        """
        The type of hardware accelerators associated with this node.
        """
        return pulumi.get(self, "accelerator_type")

    @property
    @pulumi.getter(name="apiVersion")
    def api_version(self) -> str:
        """
        The API version that created this Node.
        """
        return pulumi.get(self, "api_version")

    @property
    @pulumi.getter(name="cidrBlock")
    def cidr_block(self) -> str:
        """
        The CIDR block that the TPU node will use when selecting an IP address. This CIDR block must be a /29 block; the Compute Engine networks API forbids a smaller block, and using a larger block would be wasteful (a node can only consume one IP address). Errors will occur if the CIDR block has already been used for a currently existing TPU node, the CIDR block conflicts with any subnetworks in the user's provided network, or the provided network is peered with another network that is using that CIDR block.
        """
        return pulumi.get(self, "cidr_block")

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> str:
        """
        The time when the node was created.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter(name="dataDisks")
    def data_disks(self) -> Sequence['outputs.AttachedDiskResponse']:
        """
        The additional data disks for the Node.
        """
        return pulumi.get(self, "data_disks")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        The user-supplied description of the TPU. Maximum of 512 characters.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def health(self) -> str:
        """
        The health status of the TPU node.
        """
        return pulumi.get(self, "health")

    @property
    @pulumi.getter(name="healthDescription")
    def health_description(self) -> str:
        """
        If this field is populated, it contains a description of why the TPU Node is unhealthy.
        """
        return pulumi.get(self, "health_description")

    @property
    @pulumi.getter
    def labels(self) -> Mapping[str, str]:
        """
        Resource labels to represent user-provided metadata.
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def metadata(self) -> Mapping[str, str]:
        """
        Custom metadata to apply to the TPU Node. Can set startup-script and shutdown-script
        """
        return pulumi.get(self, "metadata")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Immutable. The name of the TPU.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="networkConfig")
    def network_config(self) -> 'outputs.NetworkConfigResponse':
        """
        Network configurations for the TPU node.
        """
        return pulumi.get(self, "network_config")

    @property
    @pulumi.getter(name="networkEndpoints")
    def network_endpoints(self) -> Sequence['outputs.NetworkEndpointResponse']:
        """
        The network endpoints where TPU workers can be accessed and sent work. It is recommended that runtime clients of the node reach out to the 0th entry in this map first.
        """
        return pulumi.get(self, "network_endpoints")

    @property
    @pulumi.getter(name="runtimeVersion")
    def runtime_version(self) -> str:
        """
        The runtime version running in the Node.
        """
        return pulumi.get(self, "runtime_version")

    @property
    @pulumi.getter(name="schedulingConfig")
    def scheduling_config(self) -> 'outputs.SchedulingConfigResponse':
        """
        The scheduling options for this node.
        """
        return pulumi.get(self, "scheduling_config")

    @property
    @pulumi.getter(name="serviceAccount")
    def service_account(self) -> 'outputs.ServiceAccountResponse':
        """
        The Google Cloud Platform Service Account to be used by the TPU node VMs. If None is specified, the default compute service account will be used.
        """
        return pulumi.get(self, "service_account")

    @property
    @pulumi.getter
    def state(self) -> str:
        """
        The current state for the TPU Node.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter
    def symptoms(self) -> Sequence['outputs.SymptomResponse']:
        """
        The Symptoms that have occurred to the TPU Node.
        """
        return pulumi.get(self, "symptoms")

    @property
    @pulumi.getter
    def tags(self) -> Sequence[str]:
        """
        Tags to apply to the TPU Node. Tags are used to identify valid sources or targets for network firewalls.
        """
        return pulumi.get(self, "tags")


class AwaitableGetNodeResult(GetNodeResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetNodeResult(
            accelerator_type=self.accelerator_type,
            api_version=self.api_version,
            cidr_block=self.cidr_block,
            create_time=self.create_time,
            data_disks=self.data_disks,
            description=self.description,
            health=self.health,
            health_description=self.health_description,
            labels=self.labels,
            metadata=self.metadata,
            name=self.name,
            network_config=self.network_config,
            network_endpoints=self.network_endpoints,
            runtime_version=self.runtime_version,
            scheduling_config=self.scheduling_config,
            service_account=self.service_account,
            state=self.state,
            symptoms=self.symptoms,
            tags=self.tags)


def get_node(location: Optional[str] = None,
             node_id: Optional[str] = None,
             project: Optional[str] = None,
             opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetNodeResult:
    """
    Gets the details of a node.
    """
    __args__ = dict()
    __args__['location'] = location
    __args__['nodeId'] = node_id
    __args__['project'] = project
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:tpu/v2alpha1:getNode', __args__, opts=opts, typ=GetNodeResult).value

    return AwaitableGetNodeResult(
        accelerator_type=__ret__.accelerator_type,
        api_version=__ret__.api_version,
        cidr_block=__ret__.cidr_block,
        create_time=__ret__.create_time,
        data_disks=__ret__.data_disks,
        description=__ret__.description,
        health=__ret__.health,
        health_description=__ret__.health_description,
        labels=__ret__.labels,
        metadata=__ret__.metadata,
        name=__ret__.name,
        network_config=__ret__.network_config,
        network_endpoints=__ret__.network_endpoints,
        runtime_version=__ret__.runtime_version,
        scheduling_config=__ret__.scheduling_config,
        service_account=__ret__.service_account,
        state=__ret__.state,
        symptoms=__ret__.symptoms,
        tags=__ret__.tags)


@_utilities.lift_output_func(get_node)
def get_node_output(location: Optional[pulumi.Input[str]] = None,
                    node_id: Optional[pulumi.Input[str]] = None,
                    project: Optional[pulumi.Input[Optional[str]]] = None,
                    opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetNodeResult]:
    """
    Gets the details of a node.
    """
    ...
