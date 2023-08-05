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

__all__ = ['RouterArgs', 'Router']

@pulumi.input_type
class RouterArgs:
    def __init__(__self__, *,
                 region: pulumi.Input[str],
                 bgp: Optional[pulumi.Input['RouterBgpArgs']] = None,
                 bgp_peers: Optional[pulumi.Input[Sequence[pulumi.Input['RouterBgpPeerArgs']]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 encrypted_interconnect_router: Optional[pulumi.Input[bool]] = None,
                 interfaces: Optional[pulumi.Input[Sequence[pulumi.Input['RouterInterfaceArgs']]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 nats: Optional[pulumi.Input[Sequence[pulumi.Input['RouterNatArgs']]]] = None,
                 network: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a Router resource.
        :param pulumi.Input['RouterBgpArgs'] bgp: BGP information specific to this router.
        :param pulumi.Input[Sequence[pulumi.Input['RouterBgpPeerArgs']]] bgp_peers: BGP information that must be configured into the routing stack to establish BGP peering. This information must specify the peer ASN and either the interface name, IP address, or peer IP address. Please refer to RFC4273.
        :param pulumi.Input[str] description: An optional description of this resource. Provide this property when you create the resource.
        :param pulumi.Input[bool] encrypted_interconnect_router: Indicates if a router is dedicated for use with encrypted VLAN attachments (interconnectAttachments). Not currently available publicly. 
        :param pulumi.Input[Sequence[pulumi.Input['RouterInterfaceArgs']]] interfaces: Router interfaces. Each interface requires either one linked resource, (for example, linkedVpnTunnel), or IP address and IP address range (for example, ipRange), or both.
        :param pulumi.Input[str] name: Name of the resource. Provided by the client when the resource is created. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?` which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash.
        :param pulumi.Input[Sequence[pulumi.Input['RouterNatArgs']]] nats: A list of NAT services created in this router.
        :param pulumi.Input[str] network: URI of the network to which this router belongs.
        :param pulumi.Input[str] request_id: An optional request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. For example, consider a situation where you make an initial request and the request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported ( 00000000-0000-0000-0000-000000000000).
        """
        pulumi.set(__self__, "region", region)
        if bgp is not None:
            pulumi.set(__self__, "bgp", bgp)
        if bgp_peers is not None:
            pulumi.set(__self__, "bgp_peers", bgp_peers)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if encrypted_interconnect_router is not None:
            pulumi.set(__self__, "encrypted_interconnect_router", encrypted_interconnect_router)
        if interfaces is not None:
            pulumi.set(__self__, "interfaces", interfaces)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if nats is not None:
            pulumi.set(__self__, "nats", nats)
        if network is not None:
            pulumi.set(__self__, "network", network)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if request_id is not None:
            pulumi.set(__self__, "request_id", request_id)

    @property
    @pulumi.getter
    def region(self) -> pulumi.Input[str]:
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: pulumi.Input[str]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter
    def bgp(self) -> Optional[pulumi.Input['RouterBgpArgs']]:
        """
        BGP information specific to this router.
        """
        return pulumi.get(self, "bgp")

    @bgp.setter
    def bgp(self, value: Optional[pulumi.Input['RouterBgpArgs']]):
        pulumi.set(self, "bgp", value)

    @property
    @pulumi.getter(name="bgpPeers")
    def bgp_peers(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['RouterBgpPeerArgs']]]]:
        """
        BGP information that must be configured into the routing stack to establish BGP peering. This information must specify the peer ASN and either the interface name, IP address, or peer IP address. Please refer to RFC4273.
        """
        return pulumi.get(self, "bgp_peers")

    @bgp_peers.setter
    def bgp_peers(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['RouterBgpPeerArgs']]]]):
        pulumi.set(self, "bgp_peers", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        An optional description of this resource. Provide this property when you create the resource.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="encryptedInterconnectRouter")
    def encrypted_interconnect_router(self) -> Optional[pulumi.Input[bool]]:
        """
        Indicates if a router is dedicated for use with encrypted VLAN attachments (interconnectAttachments). Not currently available publicly. 
        """
        return pulumi.get(self, "encrypted_interconnect_router")

    @encrypted_interconnect_router.setter
    def encrypted_interconnect_router(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "encrypted_interconnect_router", value)

    @property
    @pulumi.getter
    def interfaces(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['RouterInterfaceArgs']]]]:
        """
        Router interfaces. Each interface requires either one linked resource, (for example, linkedVpnTunnel), or IP address and IP address range (for example, ipRange), or both.
        """
        return pulumi.get(self, "interfaces")

    @interfaces.setter
    def interfaces(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['RouterInterfaceArgs']]]]):
        pulumi.set(self, "interfaces", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the resource. Provided by the client when the resource is created. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?` which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def nats(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['RouterNatArgs']]]]:
        """
        A list of NAT services created in this router.
        """
        return pulumi.get(self, "nats")

    @nats.setter
    def nats(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['RouterNatArgs']]]]):
        pulumi.set(self, "nats", value)

    @property
    @pulumi.getter
    def network(self) -> Optional[pulumi.Input[str]]:
        """
        URI of the network to which this router belongs.
        """
        return pulumi.get(self, "network")

    @network.setter
    def network(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "network", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)

    @property
    @pulumi.getter(name="requestId")
    def request_id(self) -> Optional[pulumi.Input[str]]:
        """
        An optional request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. For example, consider a situation where you make an initial request and the request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported ( 00000000-0000-0000-0000-000000000000).
        """
        return pulumi.get(self, "request_id")

    @request_id.setter
    def request_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "request_id", value)


class Router(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bgp: Optional[pulumi.Input[pulumi.InputType['RouterBgpArgs']]] = None,
                 bgp_peers: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouterBgpPeerArgs']]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 encrypted_interconnect_router: Optional[pulumi.Input[bool]] = None,
                 interfaces: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouterInterfaceArgs']]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 nats: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouterNatArgs']]]]] = None,
                 network: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Creates a Router resource in the specified project and region using the data included in the request.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['RouterBgpArgs']] bgp: BGP information specific to this router.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouterBgpPeerArgs']]]] bgp_peers: BGP information that must be configured into the routing stack to establish BGP peering. This information must specify the peer ASN and either the interface name, IP address, or peer IP address. Please refer to RFC4273.
        :param pulumi.Input[str] description: An optional description of this resource. Provide this property when you create the resource.
        :param pulumi.Input[bool] encrypted_interconnect_router: Indicates if a router is dedicated for use with encrypted VLAN attachments (interconnectAttachments). Not currently available publicly. 
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouterInterfaceArgs']]]] interfaces: Router interfaces. Each interface requires either one linked resource, (for example, linkedVpnTunnel), or IP address and IP address range (for example, ipRange), or both.
        :param pulumi.Input[str] name: Name of the resource. Provided by the client when the resource is created. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?` which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouterNatArgs']]]] nats: A list of NAT services created in this router.
        :param pulumi.Input[str] network: URI of the network to which this router belongs.
        :param pulumi.Input[str] request_id: An optional request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. For example, consider a situation where you make an initial request and the request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported ( 00000000-0000-0000-0000-000000000000).
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: RouterArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a Router resource in the specified project and region using the data included in the request.

        :param str resource_name: The name of the resource.
        :param RouterArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(RouterArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bgp: Optional[pulumi.Input[pulumi.InputType['RouterBgpArgs']]] = None,
                 bgp_peers: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouterBgpPeerArgs']]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 encrypted_interconnect_router: Optional[pulumi.Input[bool]] = None,
                 interfaces: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouterInterfaceArgs']]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 nats: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouterNatArgs']]]]] = None,
                 network: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 request_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = RouterArgs.__new__(RouterArgs)

            __props__.__dict__["bgp"] = bgp
            __props__.__dict__["bgp_peers"] = bgp_peers
            __props__.__dict__["description"] = description
            __props__.__dict__["encrypted_interconnect_router"] = encrypted_interconnect_router
            __props__.__dict__["interfaces"] = interfaces
            __props__.__dict__["name"] = name
            __props__.__dict__["nats"] = nats
            __props__.__dict__["network"] = network
            __props__.__dict__["project"] = project
            if region is None and not opts.urn:
                raise TypeError("Missing required property 'region'")
            __props__.__dict__["region"] = region
            __props__.__dict__["request_id"] = request_id
            __props__.__dict__["creation_timestamp"] = None
            __props__.__dict__["kind"] = None
            __props__.__dict__["self_link"] = None
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["project", "region"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(Router, __self__).__init__(
            'google-native:compute/v1:Router',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Router':
        """
        Get an existing Router resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = RouterArgs.__new__(RouterArgs)

        __props__.__dict__["bgp"] = None
        __props__.__dict__["bgp_peers"] = None
        __props__.__dict__["creation_timestamp"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["encrypted_interconnect_router"] = None
        __props__.__dict__["interfaces"] = None
        __props__.__dict__["kind"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["nats"] = None
        __props__.__dict__["network"] = None
        __props__.__dict__["project"] = None
        __props__.__dict__["region"] = None
        __props__.__dict__["request_id"] = None
        __props__.__dict__["self_link"] = None
        return Router(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def bgp(self) -> pulumi.Output['outputs.RouterBgpResponse']:
        """
        BGP information specific to this router.
        """
        return pulumi.get(self, "bgp")

    @property
    @pulumi.getter(name="bgpPeers")
    def bgp_peers(self) -> pulumi.Output[Sequence['outputs.RouterBgpPeerResponse']]:
        """
        BGP information that must be configured into the routing stack to establish BGP peering. This information must specify the peer ASN and either the interface name, IP address, or peer IP address. Please refer to RFC4273.
        """
        return pulumi.get(self, "bgp_peers")

    @property
    @pulumi.getter(name="creationTimestamp")
    def creation_timestamp(self) -> pulumi.Output[str]:
        """
        Creation timestamp in RFC3339 text format.
        """
        return pulumi.get(self, "creation_timestamp")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        An optional description of this resource. Provide this property when you create the resource.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="encryptedInterconnectRouter")
    def encrypted_interconnect_router(self) -> pulumi.Output[bool]:
        """
        Indicates if a router is dedicated for use with encrypted VLAN attachments (interconnectAttachments). Not currently available publicly. 
        """
        return pulumi.get(self, "encrypted_interconnect_router")

    @property
    @pulumi.getter
    def interfaces(self) -> pulumi.Output[Sequence['outputs.RouterInterfaceResponse']]:
        """
        Router interfaces. Each interface requires either one linked resource, (for example, linkedVpnTunnel), or IP address and IP address range (for example, ipRange), or both.
        """
        return pulumi.get(self, "interfaces")

    @property
    @pulumi.getter
    def kind(self) -> pulumi.Output[str]:
        """
        Type of resource. Always compute#router for routers.
        """
        return pulumi.get(self, "kind")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Name of the resource. Provided by the client when the resource is created. The name must be 1-63 characters long, and comply with RFC1035. Specifically, the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?` which means the first character must be a lowercase letter, and all following characters must be a dash, lowercase letter, or digit, except the last character, which cannot be a dash.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def nats(self) -> pulumi.Output[Sequence['outputs.RouterNatResponse']]:
        """
        A list of NAT services created in this router.
        """
        return pulumi.get(self, "nats")

    @property
    @pulumi.getter
    def network(self) -> pulumi.Output[str]:
        """
        URI of the network to which this router belongs.
        """
        return pulumi.get(self, "network")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        return pulumi.get(self, "project")

    @property
    @pulumi.getter
    def region(self) -> pulumi.Output[str]:
        return pulumi.get(self, "region")

    @property
    @pulumi.getter(name="requestId")
    def request_id(self) -> pulumi.Output[Optional[str]]:
        """
        An optional request ID to identify requests. Specify a unique request ID so that if you must retry your request, the server will know to ignore the request if it has already been completed. For example, consider a situation where you make an initial request and the request times out. If you make the request again with the same request ID, the server can check if original operation with the same request ID was received, and if so, will ignore the second request. This prevents clients from accidentally creating duplicate commitments. The request ID must be a valid UUID with the exception that zero UUID is not supported ( 00000000-0000-0000-0000-000000000000).
        """
        return pulumi.get(self, "request_id")

    @property
    @pulumi.getter(name="selfLink")
    def self_link(self) -> pulumi.Output[str]:
        """
        Server-defined URL for the resource.
        """
        return pulumi.get(self, "self_link")

