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
    def __init__(__self__, accelerator_type=None, api_version=None, cidr_block=None, create_time=None, description=None, health=None, health_description=None, ip_address=None, labels=None, name=None, network=None, network_endpoints=None, port=None, scheduling_config=None, service_account=None, state=None, symptoms=None, tensorflow_version=None, use_service_networking=None):
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
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if health and not isinstance(health, str):
            raise TypeError("Expected argument 'health' to be a str")
        pulumi.set(__self__, "health", health)
        if health_description and not isinstance(health_description, str):
            raise TypeError("Expected argument 'health_description' to be a str")
        pulumi.set(__self__, "health_description", health_description)
        if ip_address and not isinstance(ip_address, str):
            raise TypeError("Expected argument 'ip_address' to be a str")
        if ip_address is not None:
            warnings.warn("""Output only. DEPRECATED! Use network_endpoints instead. The network address for the TPU Node as visible to Compute Engine instances.""", DeprecationWarning)
            pulumi.log.warn("""ip_address is deprecated: Output only. DEPRECATED! Use network_endpoints instead. The network address for the TPU Node as visible to Compute Engine instances.""")

        pulumi.set(__self__, "ip_address", ip_address)
        if labels and not isinstance(labels, dict):
            raise TypeError("Expected argument 'labels' to be a dict")
        pulumi.set(__self__, "labels", labels)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if network and not isinstance(network, str):
            raise TypeError("Expected argument 'network' to be a str")
        pulumi.set(__self__, "network", network)
        if network_endpoints and not isinstance(network_endpoints, list):
            raise TypeError("Expected argument 'network_endpoints' to be a list")
        pulumi.set(__self__, "network_endpoints", network_endpoints)
        if port and not isinstance(port, str):
            raise TypeError("Expected argument 'port' to be a str")
        if port is not None:
            warnings.warn("""Output only. DEPRECATED! Use network_endpoints instead. The network port for the TPU Node as visible to Compute Engine instances.""", DeprecationWarning)
            pulumi.log.warn("""port is deprecated: Output only. DEPRECATED! Use network_endpoints instead. The network port for the TPU Node as visible to Compute Engine instances.""")

        pulumi.set(__self__, "port", port)
        if scheduling_config and not isinstance(scheduling_config, dict):
            raise TypeError("Expected argument 'scheduling_config' to be a dict")
        pulumi.set(__self__, "scheduling_config", scheduling_config)
        if service_account and not isinstance(service_account, str):
            raise TypeError("Expected argument 'service_account' to be a str")
        pulumi.set(__self__, "service_account", service_account)
        if state and not isinstance(state, str):
            raise TypeError("Expected argument 'state' to be a str")
        pulumi.set(__self__, "state", state)
        if symptoms and not isinstance(symptoms, list):
            raise TypeError("Expected argument 'symptoms' to be a list")
        pulumi.set(__self__, "symptoms", symptoms)
        if tensorflow_version and not isinstance(tensorflow_version, str):
            raise TypeError("Expected argument 'tensorflow_version' to be a str")
        pulumi.set(__self__, "tensorflow_version", tensorflow_version)
        if use_service_networking and not isinstance(use_service_networking, bool):
            raise TypeError("Expected argument 'use_service_networking' to be a bool")
        pulumi.set(__self__, "use_service_networking", use_service_networking)

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
    @pulumi.getter(name="ipAddress")
    def ip_address(self) -> str:
        """
        DEPRECATED! Use network_endpoints instead. The network address for the TPU Node as visible to Compute Engine instances.
        """
        return pulumi.get(self, "ip_address")

    @property
    @pulumi.getter
    def labels(self) -> Mapping[str, str]:
        """
        Resource labels to represent user-provided metadata.
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Immutable. The name of the TPU
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def network(self) -> str:
        """
        The name of a network they wish to peer the TPU node to. It must be a preexisting Compute Engine network inside of the project on which this API has been activated. If none is provided, "default" will be used.
        """
        return pulumi.get(self, "network")

    @property
    @pulumi.getter(name="networkEndpoints")
    def network_endpoints(self) -> Sequence['outputs.NetworkEndpointResponse']:
        """
        The network endpoints where TPU workers can be accessed and sent work. It is recommended that Tensorflow clients of the node reach out to the 0th entry in this map first.
        """
        return pulumi.get(self, "network_endpoints")

    @property
    @pulumi.getter
    def port(self) -> str:
        """
        DEPRECATED! Use network_endpoints instead. The network port for the TPU Node as visible to Compute Engine instances.
        """
        return pulumi.get(self, "port")

    @property
    @pulumi.getter(name="schedulingConfig")
    def scheduling_config(self) -> 'outputs.SchedulingConfigResponse':
        """
        The scheduling options for this node.
        """
        return pulumi.get(self, "scheduling_config")

    @property
    @pulumi.getter(name="serviceAccount")
    def service_account(self) -> str:
        """
        The service account used to run the tensor flow services within the node. To share resources, including Google Cloud Storage data, with the Tensorflow job running in the Node, this account must have permissions to that data.
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
    @pulumi.getter(name="tensorflowVersion")
    def tensorflow_version(self) -> str:
        """
        The version of Tensorflow running in the Node.
        """
        return pulumi.get(self, "tensorflow_version")

    @property
    @pulumi.getter(name="useServiceNetworking")
    def use_service_networking(self) -> bool:
        """
        Whether the VPC peering for the node is set up through Service Networking API. The VPC Peering should be set up before provisioning the node. If this field is set, cidr_block field should not be specified. If the network, that you want to peer the TPU Node to, is Shared VPC networks, the node must be created with this this field enabled.
        """
        return pulumi.get(self, "use_service_networking")


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
            description=self.description,
            health=self.health,
            health_description=self.health_description,
            ip_address=self.ip_address,
            labels=self.labels,
            name=self.name,
            network=self.network,
            network_endpoints=self.network_endpoints,
            port=self.port,
            scheduling_config=self.scheduling_config,
            service_account=self.service_account,
            state=self.state,
            symptoms=self.symptoms,
            tensorflow_version=self.tensorflow_version,
            use_service_networking=self.use_service_networking)


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
    __ret__ = pulumi.runtime.invoke('google-native:tpu/v1alpha1:getNode', __args__, opts=opts, typ=GetNodeResult).value

    return AwaitableGetNodeResult(
        accelerator_type=__ret__.accelerator_type,
        api_version=__ret__.api_version,
        cidr_block=__ret__.cidr_block,
        create_time=__ret__.create_time,
        description=__ret__.description,
        health=__ret__.health,
        health_description=__ret__.health_description,
        ip_address=__ret__.ip_address,
        labels=__ret__.labels,
        name=__ret__.name,
        network=__ret__.network,
        network_endpoints=__ret__.network_endpoints,
        port=__ret__.port,
        scheduling_config=__ret__.scheduling_config,
        service_account=__ret__.service_account,
        state=__ret__.state,
        symptoms=__ret__.symptoms,
        tensorflow_version=__ret__.tensorflow_version,
        use_service_networking=__ret__.use_service_networking)


@_utilities.lift_output_func(get_node)
def get_node_output(location: Optional[pulumi.Input[str]] = None,
                    node_id: Optional[pulumi.Input[str]] = None,
                    project: Optional[pulumi.Input[Optional[str]]] = None,
                    opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetNodeResult]:
    """
    Gets the details of a node.
    """
    ...
