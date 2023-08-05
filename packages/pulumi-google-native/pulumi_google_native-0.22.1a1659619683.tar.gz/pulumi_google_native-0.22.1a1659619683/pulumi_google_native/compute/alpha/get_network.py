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
    'GetNetworkResult',
    'AwaitableGetNetworkResult',
    'get_network',
    'get_network_output',
]

@pulumi.output_type
class GetNetworkResult:
    def __init__(__self__, auto_create_subnetworks=None, creation_timestamp=None, description=None, enable_ula_internal_ipv6=None, firewall_policy=None, gateway_i_pv4=None, internal_ipv6_range=None, ipv4_range=None, kind=None, mtu=None, name=None, network_firewall_policy_enforcement_order=None, peerings=None, region=None, routing_config=None, self_link=None, self_link_with_id=None, subnetworks=None):
        if auto_create_subnetworks and not isinstance(auto_create_subnetworks, bool):
            raise TypeError("Expected argument 'auto_create_subnetworks' to be a bool")
        pulumi.set(__self__, "auto_create_subnetworks", auto_create_subnetworks)
        if creation_timestamp and not isinstance(creation_timestamp, str):
            raise TypeError("Expected argument 'creation_timestamp' to be a str")
        pulumi.set(__self__, "creation_timestamp", creation_timestamp)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if enable_ula_internal_ipv6 and not isinstance(enable_ula_internal_ipv6, bool):
            raise TypeError("Expected argument 'enable_ula_internal_ipv6' to be a bool")
        pulumi.set(__self__, "enable_ula_internal_ipv6", enable_ula_internal_ipv6)
        if firewall_policy and not isinstance(firewall_policy, str):
            raise TypeError("Expected argument 'firewall_policy' to be a str")
        pulumi.set(__self__, "firewall_policy", firewall_policy)
        if gateway_i_pv4 and not isinstance(gateway_i_pv4, str):
            raise TypeError("Expected argument 'gateway_i_pv4' to be a str")
        pulumi.set(__self__, "gateway_i_pv4", gateway_i_pv4)
        if internal_ipv6_range and not isinstance(internal_ipv6_range, str):
            raise TypeError("Expected argument 'internal_ipv6_range' to be a str")
        pulumi.set(__self__, "internal_ipv6_range", internal_ipv6_range)
        if ipv4_range and not isinstance(ipv4_range, str):
            raise TypeError("Expected argument 'ipv4_range' to be a str")
        if ipv4_range is not None:
            warnings.warn("""Deprecated in favor of subnet mode networks. The range of internal addresses that are legal on this network. This range is a CIDR specification, for example: 192.168.0.0/16. Provided by the client when the network is created.""", DeprecationWarning)
            pulumi.log.warn("""ipv4_range is deprecated: Deprecated in favor of subnet mode networks. The range of internal addresses that are legal on this network. This range is a CIDR specification, for example: 192.168.0.0/16. Provided by the client when the network is created.""")

        pulumi.set(__self__, "ipv4_range", ipv4_range)
        if kind and not isinstance(kind, str):
            raise TypeError("Expected argument 'kind' to be a str")
        pulumi.set(__self__, "kind", kind)
        if mtu and not isinstance(mtu, int):
            raise TypeError("Expected argument 'mtu' to be a int")
        pulumi.set(__self__, "mtu", mtu)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if network_firewall_policy_enforcement_order and not isinstance(network_firewall_policy_enforcement_order, str):
            raise TypeError("Expected argument 'network_firewall_policy_enforcement_order' to be a str")
        pulumi.set(__self__, "network_firewall_policy_enforcement_order", network_firewall_policy_enforcement_order)
        if peerings and not isinstance(peerings, list):
            raise TypeError("Expected argument 'peerings' to be a list")
        pulumi.set(__self__, "peerings", peerings)
        if region and not isinstance(region, str):
            raise TypeError("Expected argument 'region' to be a str")
        pulumi.set(__self__, "region", region)
        if routing_config and not isinstance(routing_config, dict):
            raise TypeError("Expected argument 'routing_config' to be a dict")
        pulumi.set(__self__, "routing_config", routing_config)
        if self_link and not isinstance(self_link, str):
            raise TypeError("Expected argument 'self_link' to be a str")
        pulumi.set(__self__, "self_link", self_link)
        if self_link_with_id and not isinstance(self_link_with_id, str):
            raise TypeError("Expected argument 'self_link_with_id' to be a str")
        pulumi.set(__self__, "self_link_with_id", self_link_with_id)
        if subnetworks and not isinstance(subnetworks, list):
            raise TypeError("Expected argument 'subnetworks' to be a list")
        pulumi.set(__self__, "subnetworks", subnetworks)

    @property
    @pulumi.getter(name="autoCreateSubnetworks")
    def auto_create_subnetworks(self) -> bool:
        """
        Must be set to create a VPC network. If not set, a legacy network is created. When set to true, the VPC network is created in auto mode. When set to false, the VPC network is created in custom mode. An auto mode VPC network starts with one subnet per region. Each subnet has a predetermined range as described in Auto mode VPC network IP ranges. For custom mode VPC networks, you can add subnets using the subnetworks insert method.
        """
        return pulumi.get(self, "auto_create_subnetworks")

    @property
    @pulumi.getter(name="creationTimestamp")
    def creation_timestamp(self) -> str:
        """
        Creation timestamp in RFC3339 text format.
        """
        return pulumi.get(self, "creation_timestamp")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        An optional description of this resource. Provide this field when you create the resource.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="enableUlaInternalIpv6")
    def enable_ula_internal_ipv6(self) -> bool:
        """
        Enable ULA internal ipv6 on this network. Enabling this feature will assign a /48 from google defined ULA prefix fd20::/20. .
        """
        return pulumi.get(self, "enable_ula_internal_ipv6")

    @property
    @pulumi.getter(name="firewallPolicy")
    def firewall_policy(self) -> str:
        """
        URL of the firewall policy the network is associated with.
        """
        return pulumi.get(self, "firewall_policy")

    @property
    @pulumi.getter(name="gatewayIPv4")
    def gateway_i_pv4(self) -> str:
        """
        The gateway address for default routing out of the network, selected by GCP.
        """
        return pulumi.get(self, "gateway_i_pv4")

    @property
    @pulumi.getter(name="internalIpv6Range")
    def internal_ipv6_range(self) -> str:
        """
        When enabling ula internal ipv6, caller optionally can specify the /48 range they want from the google defined ULA prefix fd20::/20. The input must be a valid /48 ULA IPv6 address and must be within the fd20::/20. Operation will fail if the speficied /48 is already in used by another resource. If the field is not speficied, then a /48 range will be randomly allocated from fd20::/20 and returned via this field. .
        """
        return pulumi.get(self, "internal_ipv6_range")

    @property
    @pulumi.getter(name="ipv4Range")
    def ipv4_range(self) -> str:
        """
        Deprecated in favor of subnet mode networks. The range of internal addresses that are legal on this network. This range is a CIDR specification, for example: 192.168.0.0/16. Provided by the client when the network is created.
        """
        return pulumi.get(self, "ipv4_range")

    @property
    @pulumi.getter
    def kind(self) -> str:
        """
        Type of the resource. Always compute#network for networks.
        """
        return pulumi.get(self, "kind")

    @property
    @pulumi.getter
    def mtu(self) -> int:
        """
        Maximum Transmission Unit in bytes. The minimum value for this field is 1460 and the maximum value is 1500 bytes. If unspecified, defaults to 1460.
        """
        return pulumi.get(self, "mtu")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the resource. Provided by the client when the resource is created. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?`. The first character must be a lowercase letter, and all following characters (except for the last character) must be a dash, lowercase letter, or digit. The last character must be a lowercase letter or digit.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="networkFirewallPolicyEnforcementOrder")
    def network_firewall_policy_enforcement_order(self) -> str:
        """
        The network firewall policy enforcement order. Can be either AFTER_CLASSIC_FIREWALL or BEFORE_CLASSIC_FIREWALL. Defaults to AFTER_CLASSIC_FIREWALL if the field is not specified.
        """
        return pulumi.get(self, "network_firewall_policy_enforcement_order")

    @property
    @pulumi.getter
    def peerings(self) -> Sequence['outputs.NetworkPeeringResponse']:
        """
        A list of network peerings for the resource.
        """
        return pulumi.get(self, "peerings")

    @property
    @pulumi.getter
    def region(self) -> str:
        """
        URL of the region where the regional network resides. This field is not applicable to global network. You must specify this field as part of the HTTP request URL. It is not settable as a field in the request body.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter(name="routingConfig")
    def routing_config(self) -> 'outputs.NetworkRoutingConfigResponse':
        """
        The network-level routing configuration for this network. Used by Cloud Router to determine what type of network-wide routing behavior to enforce.
        """
        return pulumi.get(self, "routing_config")

    @property
    @pulumi.getter(name="selfLink")
    def self_link(self) -> str:
        """
        Server-defined URL for the resource.
        """
        return pulumi.get(self, "self_link")

    @property
    @pulumi.getter(name="selfLinkWithId")
    def self_link_with_id(self) -> str:
        """
        Server-defined URL for this resource with the resource id.
        """
        return pulumi.get(self, "self_link_with_id")

    @property
    @pulumi.getter
    def subnetworks(self) -> Sequence[str]:
        """
        Server-defined fully-qualified URLs for all subnetworks in this VPC network.
        """
        return pulumi.get(self, "subnetworks")


class AwaitableGetNetworkResult(GetNetworkResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetNetworkResult(
            auto_create_subnetworks=self.auto_create_subnetworks,
            creation_timestamp=self.creation_timestamp,
            description=self.description,
            enable_ula_internal_ipv6=self.enable_ula_internal_ipv6,
            firewall_policy=self.firewall_policy,
            gateway_i_pv4=self.gateway_i_pv4,
            internal_ipv6_range=self.internal_ipv6_range,
            ipv4_range=self.ipv4_range,
            kind=self.kind,
            mtu=self.mtu,
            name=self.name,
            network_firewall_policy_enforcement_order=self.network_firewall_policy_enforcement_order,
            peerings=self.peerings,
            region=self.region,
            routing_config=self.routing_config,
            self_link=self.self_link,
            self_link_with_id=self.self_link_with_id,
            subnetworks=self.subnetworks)


def get_network(network: Optional[str] = None,
                project: Optional[str] = None,
                opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetNetworkResult:
    """
    Returns the specified network. Gets a list of available networks by making a list() request.
    """
    __args__ = dict()
    __args__['network'] = network
    __args__['project'] = project
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:compute/alpha:getNetwork', __args__, opts=opts, typ=GetNetworkResult).value

    return AwaitableGetNetworkResult(
        auto_create_subnetworks=__ret__.auto_create_subnetworks,
        creation_timestamp=__ret__.creation_timestamp,
        description=__ret__.description,
        enable_ula_internal_ipv6=__ret__.enable_ula_internal_ipv6,
        firewall_policy=__ret__.firewall_policy,
        gateway_i_pv4=__ret__.gateway_i_pv4,
        internal_ipv6_range=__ret__.internal_ipv6_range,
        ipv4_range=__ret__.ipv4_range,
        kind=__ret__.kind,
        mtu=__ret__.mtu,
        name=__ret__.name,
        network_firewall_policy_enforcement_order=__ret__.network_firewall_policy_enforcement_order,
        peerings=__ret__.peerings,
        region=__ret__.region,
        routing_config=__ret__.routing_config,
        self_link=__ret__.self_link,
        self_link_with_id=__ret__.self_link_with_id,
        subnetworks=__ret__.subnetworks)


@_utilities.lift_output_func(get_network)
def get_network_output(network: Optional[pulumi.Input[str]] = None,
                       project: Optional[pulumi.Input[Optional[str]]] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetNetworkResult]:
    """
    Returns the specified network. Gets a list of available networks by making a list() request.
    """
    ...
