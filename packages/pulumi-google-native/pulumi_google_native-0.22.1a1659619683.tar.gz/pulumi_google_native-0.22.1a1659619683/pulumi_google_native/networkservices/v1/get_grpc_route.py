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
    'GetGrpcRouteResult',
    'AwaitableGetGrpcRouteResult',
    'get_grpc_route',
    'get_grpc_route_output',
]

@pulumi.output_type
class GetGrpcRouteResult:
    def __init__(__self__, create_time=None, description=None, gateways=None, hostnames=None, labels=None, meshes=None, name=None, rules=None, self_link=None, update_time=None):
        if create_time and not isinstance(create_time, str):
            raise TypeError("Expected argument 'create_time' to be a str")
        pulumi.set(__self__, "create_time", create_time)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if gateways and not isinstance(gateways, list):
            raise TypeError("Expected argument 'gateways' to be a list")
        pulumi.set(__self__, "gateways", gateways)
        if hostnames and not isinstance(hostnames, list):
            raise TypeError("Expected argument 'hostnames' to be a list")
        pulumi.set(__self__, "hostnames", hostnames)
        if labels and not isinstance(labels, dict):
            raise TypeError("Expected argument 'labels' to be a dict")
        pulumi.set(__self__, "labels", labels)
        if meshes and not isinstance(meshes, list):
            raise TypeError("Expected argument 'meshes' to be a list")
        pulumi.set(__self__, "meshes", meshes)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if rules and not isinstance(rules, list):
            raise TypeError("Expected argument 'rules' to be a list")
        pulumi.set(__self__, "rules", rules)
        if self_link and not isinstance(self_link, str):
            raise TypeError("Expected argument 'self_link' to be a str")
        pulumi.set(__self__, "self_link", self_link)
        if update_time and not isinstance(update_time, str):
            raise TypeError("Expected argument 'update_time' to be a str")
        pulumi.set(__self__, "update_time", update_time)

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> str:
        """
        The timestamp when the resource was created.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        Optional. A free-text description of the resource. Max length 1024 characters.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def gateways(self) -> Sequence[str]:
        """
        Optional. Gateways defines a list of gateways this GrpcRoute is attached to, as one of the routing rules to route the requests served by the gateway. Each gateway reference should match the pattern: `projects/*/locations/global/gateways/`
        """
        return pulumi.get(self, "gateways")

    @property
    @pulumi.getter
    def hostnames(self) -> Sequence[str]:
        """
        Service hostnames with an optional port for which this route describes traffic. Format: [:] Hostname is the fully qualified domain name of a network host. This matches the RFC 1123 definition of a hostname with 2 notable exceptions: - IPs are not allowed. - A hostname may be prefixed with a wildcard label (*.). The wildcard label must appear by itself as the first label. Hostname can be "precise" which is a domain name without the terminating dot of a network host (e.g. "foo.example.com") or "wildcard", which is a domain name prefixed with a single wildcard label (e.g. *.example.com). Note that as per RFC1035 and RFC1123, a label must consist of lower case alphanumeric characters or '-', and must start and end with an alphanumeric character. No other punctuation is allowed. The routes associated with a Mesh or Gateway must have unique hostnames. If you attempt to attach multiple routes with conflicting hostnames, the configuration will be rejected. For example, while it is acceptable for routes for the hostnames "*.foo.bar.com" and "*.bar.com" to be associated with the same route, it is not possible to associate two routes both with "*.bar.com" or both with "bar.com". If a port is specified, then gRPC clients must use the channel URI with the port to match this rule (i.e. "xds:///service:123"), otherwise they must supply the URI without a port (i.e. "xds:///service").
        """
        return pulumi.get(self, "hostnames")

    @property
    @pulumi.getter
    def labels(self) -> Mapping[str, str]:
        """
        Optional. Set of label tags associated with the GrpcRoute resource.
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def meshes(self) -> Sequence[str]:
        """
        Optional. Meshes defines a list of meshes this GrpcRoute is attached to, as one of the routing rules to route the requests served by the mesh. Each mesh reference should match the pattern: `projects/*/locations/global/meshes/`
        """
        return pulumi.get(self, "meshes")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the GrpcRoute resource. It matches pattern `projects/*/locations/global/grpcRoutes/`
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def rules(self) -> Sequence['outputs.GrpcRouteRouteRuleResponse']:
        """
        A list of detailed rules defining how to route traffic. Within a single GrpcRoute, the GrpcRoute.RouteAction associated with the first matching GrpcRoute.RouteRule will be executed. At least one rule must be supplied.
        """
        return pulumi.get(self, "rules")

    @property
    @pulumi.getter(name="selfLink")
    def self_link(self) -> str:
        """
        Server-defined URL of this resource
        """
        return pulumi.get(self, "self_link")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> str:
        """
        The timestamp when the resource was updated.
        """
        return pulumi.get(self, "update_time")


class AwaitableGetGrpcRouteResult(GetGrpcRouteResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetGrpcRouteResult(
            create_time=self.create_time,
            description=self.description,
            gateways=self.gateways,
            hostnames=self.hostnames,
            labels=self.labels,
            meshes=self.meshes,
            name=self.name,
            rules=self.rules,
            self_link=self.self_link,
            update_time=self.update_time)


def get_grpc_route(grpc_route_id: Optional[str] = None,
                   location: Optional[str] = None,
                   project: Optional[str] = None,
                   opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetGrpcRouteResult:
    """
    Gets details of a single GrpcRoute.
    """
    __args__ = dict()
    __args__['grpcRouteId'] = grpc_route_id
    __args__['location'] = location
    __args__['project'] = project
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:networkservices/v1:getGrpcRoute', __args__, opts=opts, typ=GetGrpcRouteResult).value

    return AwaitableGetGrpcRouteResult(
        create_time=__ret__.create_time,
        description=__ret__.description,
        gateways=__ret__.gateways,
        hostnames=__ret__.hostnames,
        labels=__ret__.labels,
        meshes=__ret__.meshes,
        name=__ret__.name,
        rules=__ret__.rules,
        self_link=__ret__.self_link,
        update_time=__ret__.update_time)


@_utilities.lift_output_func(get_grpc_route)
def get_grpc_route_output(grpc_route_id: Optional[pulumi.Input[str]] = None,
                          location: Optional[pulumi.Input[str]] = None,
                          project: Optional[pulumi.Input[Optional[str]]] = None,
                          opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetGrpcRouteResult]:
    """
    Gets details of a single GrpcRoute.
    """
    ...
