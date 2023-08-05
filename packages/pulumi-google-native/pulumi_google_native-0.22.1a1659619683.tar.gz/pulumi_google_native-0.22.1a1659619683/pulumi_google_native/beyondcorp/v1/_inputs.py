# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities
from ._enums import *

__all__ = [
    'ConfigArgs',
    'DestinationRouteArgs',
    'EgressArgs',
    'GoogleCloudBeyondcorpAppconnectionsV1AppConnectionApplicationEndpointArgs',
    'GoogleCloudBeyondcorpAppconnectionsV1AppConnectionGatewayArgs',
    'GoogleCloudBeyondcorpAppconnectorsV1AppConnectorPrincipalInfoServiceAccountArgs',
    'GoogleCloudBeyondcorpAppconnectorsV1AppConnectorPrincipalInfoArgs',
    'GoogleCloudBeyondcorpAppconnectorsV1ResourceInfoArgs',
    'GoogleIamV1AuditConfigArgs',
    'GoogleIamV1AuditLogConfigArgs',
    'GoogleIamV1BindingArgs',
    'GoogleTypeExprArgs',
    'IngressArgs',
    'PeeredVpcArgs',
]

@pulumi.input_type
class ConfigArgs:
    def __init__(__self__, *,
                 destination_routes: pulumi.Input[Sequence[pulumi.Input['DestinationRouteArgs']]],
                 transport_protocol: pulumi.Input['ConfigTransportProtocol']):
        """
        The basic ingress config for ClientGateways.
        :param pulumi.Input[Sequence[pulumi.Input['DestinationRouteArgs']]] destination_routes: The settings used to configure basic ClientGateways.
        :param pulumi.Input['ConfigTransportProtocol'] transport_protocol: Immutable. The transport protocol used between the client and the server.
        """
        pulumi.set(__self__, "destination_routes", destination_routes)
        pulumi.set(__self__, "transport_protocol", transport_protocol)

    @property
    @pulumi.getter(name="destinationRoutes")
    def destination_routes(self) -> pulumi.Input[Sequence[pulumi.Input['DestinationRouteArgs']]]:
        """
        The settings used to configure basic ClientGateways.
        """
        return pulumi.get(self, "destination_routes")

    @destination_routes.setter
    def destination_routes(self, value: pulumi.Input[Sequence[pulumi.Input['DestinationRouteArgs']]]):
        pulumi.set(self, "destination_routes", value)

    @property
    @pulumi.getter(name="transportProtocol")
    def transport_protocol(self) -> pulumi.Input['ConfigTransportProtocol']:
        """
        Immutable. The transport protocol used between the client and the server.
        """
        return pulumi.get(self, "transport_protocol")

    @transport_protocol.setter
    def transport_protocol(self, value: pulumi.Input['ConfigTransportProtocol']):
        pulumi.set(self, "transport_protocol", value)


@pulumi.input_type
class DestinationRouteArgs:
    def __init__(__self__, *,
                 address: pulumi.Input[str],
                 netmask: pulumi.Input[str]):
        """
        The setting used to configure ClientGateways. It is adding routes to the client's routing table after the connection is established.
        :param pulumi.Input[str] address: The network address of the subnet for which the packet is routed to the ClientGateway.
        :param pulumi.Input[str] netmask: The network mask of the subnet for which the packet is routed to the ClientGateway.
        """
        pulumi.set(__self__, "address", address)
        pulumi.set(__self__, "netmask", netmask)

    @property
    @pulumi.getter
    def address(self) -> pulumi.Input[str]:
        """
        The network address of the subnet for which the packet is routed to the ClientGateway.
        """
        return pulumi.get(self, "address")

    @address.setter
    def address(self, value: pulumi.Input[str]):
        pulumi.set(self, "address", value)

    @property
    @pulumi.getter
    def netmask(self) -> pulumi.Input[str]:
        """
        The network mask of the subnet for which the packet is routed to the ClientGateway.
        """
        return pulumi.get(self, "netmask")

    @netmask.setter
    def netmask(self, value: pulumi.Input[str]):
        pulumi.set(self, "netmask", value)


@pulumi.input_type
class EgressArgs:
    def __init__(__self__, *,
                 peered_vpc: Optional[pulumi.Input['PeeredVpcArgs']] = None):
        """
        The details of the egress info. One of the following options should be set.
        :param pulumi.Input['PeeredVpcArgs'] peered_vpc: A VPC from the consumer project.
        """
        if peered_vpc is not None:
            pulumi.set(__self__, "peered_vpc", peered_vpc)

    @property
    @pulumi.getter(name="peeredVpc")
    def peered_vpc(self) -> Optional[pulumi.Input['PeeredVpcArgs']]:
        """
        A VPC from the consumer project.
        """
        return pulumi.get(self, "peered_vpc")

    @peered_vpc.setter
    def peered_vpc(self, value: Optional[pulumi.Input['PeeredVpcArgs']]):
        pulumi.set(self, "peered_vpc", value)


@pulumi.input_type
class GoogleCloudBeyondcorpAppconnectionsV1AppConnectionApplicationEndpointArgs:
    def __init__(__self__, *,
                 host: pulumi.Input[str],
                 port: pulumi.Input[int]):
        """
        ApplicationEndpoint represents a remote application endpoint.
        :param pulumi.Input[str] host: Hostname or IP address of the remote application endpoint.
        :param pulumi.Input[int] port: Port of the remote application endpoint.
        """
        pulumi.set(__self__, "host", host)
        pulumi.set(__self__, "port", port)

    @property
    @pulumi.getter
    def host(self) -> pulumi.Input[str]:
        """
        Hostname or IP address of the remote application endpoint.
        """
        return pulumi.get(self, "host")

    @host.setter
    def host(self, value: pulumi.Input[str]):
        pulumi.set(self, "host", value)

    @property
    @pulumi.getter
    def port(self) -> pulumi.Input[int]:
        """
        Port of the remote application endpoint.
        """
        return pulumi.get(self, "port")

    @port.setter
    def port(self, value: pulumi.Input[int]):
        pulumi.set(self, "port", value)


@pulumi.input_type
class GoogleCloudBeyondcorpAppconnectionsV1AppConnectionGatewayArgs:
    def __init__(__self__, *,
                 app_gateway: pulumi.Input[str],
                 type: pulumi.Input['GoogleCloudBeyondcorpAppconnectionsV1AppConnectionGatewayType']):
        """
        Gateway represents a user facing component that serves as an entrance to enable connectivity.
        :param pulumi.Input[str] app_gateway: AppGateway name in following format: `projects/{project_id}/locations/{location_id}/appgateways/{gateway_id}`
        :param pulumi.Input['GoogleCloudBeyondcorpAppconnectionsV1AppConnectionGatewayType'] type: The type of hosting used by the gateway.
        """
        pulumi.set(__self__, "app_gateway", app_gateway)
        pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="appGateway")
    def app_gateway(self) -> pulumi.Input[str]:
        """
        AppGateway name in following format: `projects/{project_id}/locations/{location_id}/appgateways/{gateway_id}`
        """
        return pulumi.get(self, "app_gateway")

    @app_gateway.setter
    def app_gateway(self, value: pulumi.Input[str]):
        pulumi.set(self, "app_gateway", value)

    @property
    @pulumi.getter
    def type(self) -> pulumi.Input['GoogleCloudBeyondcorpAppconnectionsV1AppConnectionGatewayType']:
        """
        The type of hosting used by the gateway.
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: pulumi.Input['GoogleCloudBeyondcorpAppconnectionsV1AppConnectionGatewayType']):
        pulumi.set(self, "type", value)


@pulumi.input_type
class GoogleCloudBeyondcorpAppconnectorsV1AppConnectorPrincipalInfoServiceAccountArgs:
    def __init__(__self__, *,
                 email: Optional[pulumi.Input[str]] = None):
        """
        ServiceAccount represents a GCP service account.
        :param pulumi.Input[str] email: Email address of the service account.
        """
        if email is not None:
            pulumi.set(__self__, "email", email)

    @property
    @pulumi.getter
    def email(self) -> Optional[pulumi.Input[str]]:
        """
        Email address of the service account.
        """
        return pulumi.get(self, "email")

    @email.setter
    def email(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "email", value)


@pulumi.input_type
class GoogleCloudBeyondcorpAppconnectorsV1AppConnectorPrincipalInfoArgs:
    def __init__(__self__, *,
                 service_account: Optional[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1AppConnectorPrincipalInfoServiceAccountArgs']] = None):
        """
        PrincipalInfo represents an Identity oneof.
        :param pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1AppConnectorPrincipalInfoServiceAccountArgs'] service_account: A GCP service account.
        """
        if service_account is not None:
            pulumi.set(__self__, "service_account", service_account)

    @property
    @pulumi.getter(name="serviceAccount")
    def service_account(self) -> Optional[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1AppConnectorPrincipalInfoServiceAccountArgs']]:
        """
        A GCP service account.
        """
        return pulumi.get(self, "service_account")

    @service_account.setter
    def service_account(self, value: Optional[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1AppConnectorPrincipalInfoServiceAccountArgs']]):
        pulumi.set(self, "service_account", value)


@pulumi.input_type
class GoogleCloudBeyondcorpAppconnectorsV1ResourceInfoArgs:
    def __init__(__self__, *,
                 id: pulumi.Input[str],
                 resource: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 status: Optional[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1ResourceInfoStatus']] = None,
                 sub: Optional[pulumi.Input[Sequence[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1ResourceInfoArgs']]]] = None,
                 time: Optional[pulumi.Input[str]] = None):
        """
        ResourceInfo represents the information/status of an app connector resource. Such as: - remote_agent - container - runtime - appgateway - appconnector - appconnection - tunnel - logagent
        :param pulumi.Input[str] id: Unique Id for the resource.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] resource: Specific details for the resource. This is for internal use only.
        :param pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1ResourceInfoStatus'] status: Overall health status. Overall status is derived based on the status of each sub level resources.
        :param pulumi.Input[Sequence[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1ResourceInfoArgs']]] sub: List of Info for the sub level resources.
        :param pulumi.Input[str] time: The timestamp to collect the info. It is suggested to be set by the topmost level resource only.
        """
        pulumi.set(__self__, "id", id)
        if resource is not None:
            pulumi.set(__self__, "resource", resource)
        if status is not None:
            pulumi.set(__self__, "status", status)
        if sub is not None:
            pulumi.set(__self__, "sub", sub)
        if time is not None:
            pulumi.set(__self__, "time", time)

    @property
    @pulumi.getter
    def id(self) -> pulumi.Input[str]:
        """
        Unique Id for the resource.
        """
        return pulumi.get(self, "id")

    @id.setter
    def id(self, value: pulumi.Input[str]):
        pulumi.set(self, "id", value)

    @property
    @pulumi.getter
    def resource(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Specific details for the resource. This is for internal use only.
        """
        return pulumi.get(self, "resource")

    @resource.setter
    def resource(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "resource", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1ResourceInfoStatus']]:
        """
        Overall health status. Overall status is derived based on the status of each sub level resources.
        """
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1ResourceInfoStatus']]):
        pulumi.set(self, "status", value)

    @property
    @pulumi.getter
    def sub(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1ResourceInfoArgs']]]]:
        """
        List of Info for the sub level resources.
        """
        return pulumi.get(self, "sub")

    @sub.setter
    def sub(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['GoogleCloudBeyondcorpAppconnectorsV1ResourceInfoArgs']]]]):
        pulumi.set(self, "sub", value)

    @property
    @pulumi.getter
    def time(self) -> Optional[pulumi.Input[str]]:
        """
        The timestamp to collect the info. It is suggested to be set by the topmost level resource only.
        """
        return pulumi.get(self, "time")

    @time.setter
    def time(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "time", value)


@pulumi.input_type
class GoogleIamV1AuditConfigArgs:
    def __init__(__self__, *,
                 audit_log_configs: Optional[pulumi.Input[Sequence[pulumi.Input['GoogleIamV1AuditLogConfigArgs']]]] = None,
                 service: Optional[pulumi.Input[str]] = None):
        """
        Specifies the audit configuration for a service. The configuration determines which permission types are logged, and what identities, if any, are exempted from logging. An AuditConfig must have one or more AuditLogConfigs. If there are AuditConfigs for both `allServices` and a specific service, the union of the two AuditConfigs is used for that service: the log_types specified in each AuditConfig are enabled, and the exempted_members in each AuditLogConfig are exempted. Example Policy with multiple AuditConfigs: { "audit_configs": [ { "service": "allServices", "audit_log_configs": [ { "log_type": "DATA_READ", "exempted_members": [ "user:jose@example.com" ] }, { "log_type": "DATA_WRITE" }, { "log_type": "ADMIN_READ" } ] }, { "service": "sampleservice.googleapis.com", "audit_log_configs": [ { "log_type": "DATA_READ" }, { "log_type": "DATA_WRITE", "exempted_members": [ "user:aliya@example.com" ] } ] } ] } For sampleservice, this policy enables DATA_READ, DATA_WRITE and ADMIN_READ logging. It also exempts `jose@example.com` from DATA_READ logging, and `aliya@example.com` from DATA_WRITE logging.
        :param pulumi.Input[Sequence[pulumi.Input['GoogleIamV1AuditLogConfigArgs']]] audit_log_configs: The configuration for logging of each type of permission.
        :param pulumi.Input[str] service: Specifies a service that will be enabled for audit logging. For example, `storage.googleapis.com`, `cloudsql.googleapis.com`. `allServices` is a special value that covers all services.
        """
        if audit_log_configs is not None:
            pulumi.set(__self__, "audit_log_configs", audit_log_configs)
        if service is not None:
            pulumi.set(__self__, "service", service)

    @property
    @pulumi.getter(name="auditLogConfigs")
    def audit_log_configs(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['GoogleIamV1AuditLogConfigArgs']]]]:
        """
        The configuration for logging of each type of permission.
        """
        return pulumi.get(self, "audit_log_configs")

    @audit_log_configs.setter
    def audit_log_configs(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['GoogleIamV1AuditLogConfigArgs']]]]):
        pulumi.set(self, "audit_log_configs", value)

    @property
    @pulumi.getter
    def service(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies a service that will be enabled for audit logging. For example, `storage.googleapis.com`, `cloudsql.googleapis.com`. `allServices` is a special value that covers all services.
        """
        return pulumi.get(self, "service")

    @service.setter
    def service(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "service", value)


@pulumi.input_type
class GoogleIamV1AuditLogConfigArgs:
    def __init__(__self__, *,
                 exempted_members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 log_type: Optional[pulumi.Input['GoogleIamV1AuditLogConfigLogType']] = None):
        """
        Provides the configuration for logging a type of permissions. Example: { "audit_log_configs": [ { "log_type": "DATA_READ", "exempted_members": [ "user:jose@example.com" ] }, { "log_type": "DATA_WRITE" } ] } This enables 'DATA_READ' and 'DATA_WRITE' logging, while exempting jose@example.com from DATA_READ logging.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] exempted_members: Specifies the identities that do not cause logging for this type of permission. Follows the same format of Binding.members.
        :param pulumi.Input['GoogleIamV1AuditLogConfigLogType'] log_type: The log type that this config enables.
        """
        if exempted_members is not None:
            pulumi.set(__self__, "exempted_members", exempted_members)
        if log_type is not None:
            pulumi.set(__self__, "log_type", log_type)

    @property
    @pulumi.getter(name="exemptedMembers")
    def exempted_members(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Specifies the identities that do not cause logging for this type of permission. Follows the same format of Binding.members.
        """
        return pulumi.get(self, "exempted_members")

    @exempted_members.setter
    def exempted_members(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "exempted_members", value)

    @property
    @pulumi.getter(name="logType")
    def log_type(self) -> Optional[pulumi.Input['GoogleIamV1AuditLogConfigLogType']]:
        """
        The log type that this config enables.
        """
        return pulumi.get(self, "log_type")

    @log_type.setter
    def log_type(self, value: Optional[pulumi.Input['GoogleIamV1AuditLogConfigLogType']]):
        pulumi.set(self, "log_type", value)


@pulumi.input_type
class GoogleIamV1BindingArgs:
    def __init__(__self__, *,
                 condition: Optional[pulumi.Input['GoogleTypeExprArgs']] = None,
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 role: Optional[pulumi.Input[str]] = None):
        """
        Associates `members`, or principals, with a `role`.
        :param pulumi.Input['GoogleTypeExprArgs'] condition: The condition that is associated with this binding. If the condition evaluates to `true`, then this binding applies to the current request. If the condition evaluates to `false`, then this binding does not apply to the current request. However, a different role binding might grant the same role to one or more of the principals in this binding. To learn which resources support conditions in their IAM policies, see the [IAM documentation](https://cloud.google.com/iam/help/conditions/resource-policies).
        :param pulumi.Input[Sequence[pulumi.Input[str]]] members: Specifies the principals requesting access for a Google Cloud resource. `members` can have the following values: * `allUsers`: A special identifier that represents anyone who is on the internet; with or without a Google account. * `allAuthenticatedUsers`: A special identifier that represents anyone who is authenticated with a Google account or a service account. * `user:{emailid}`: An email address that represents a specific Google account. For example, `alice@example.com` . * `serviceAccount:{emailid}`: An email address that represents a service account. For example, `my-other-app@appspot.gserviceaccount.com`. * `group:{emailid}`: An email address that represents a Google group. For example, `admins@example.com`. * `deleted:user:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a user that has been recently deleted. For example, `alice@example.com?uid=123456789012345678901`. If the user is recovered, this value reverts to `user:{emailid}` and the recovered user retains the role in the binding. * `deleted:serviceAccount:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a service account that has been recently deleted. For example, `my-other-app@appspot.gserviceaccount.com?uid=123456789012345678901`. If the service account is undeleted, this value reverts to `serviceAccount:{emailid}` and the undeleted service account retains the role in the binding. * `deleted:group:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a Google group that has been recently deleted. For example, `admins@example.com?uid=123456789012345678901`. If the group is recovered, this value reverts to `group:{emailid}` and the recovered group retains the role in the binding. * `domain:{domain}`: The G Suite domain (primary) that represents all the users of that domain. For example, `google.com` or `example.com`. 
        :param pulumi.Input[str] role: Role that is assigned to the list of `members`, or principals. For example, `roles/viewer`, `roles/editor`, or `roles/owner`.
        """
        if condition is not None:
            pulumi.set(__self__, "condition", condition)
        if members is not None:
            pulumi.set(__self__, "members", members)
        if role is not None:
            pulumi.set(__self__, "role", role)

    @property
    @pulumi.getter
    def condition(self) -> Optional[pulumi.Input['GoogleTypeExprArgs']]:
        """
        The condition that is associated with this binding. If the condition evaluates to `true`, then this binding applies to the current request. If the condition evaluates to `false`, then this binding does not apply to the current request. However, a different role binding might grant the same role to one or more of the principals in this binding. To learn which resources support conditions in their IAM policies, see the [IAM documentation](https://cloud.google.com/iam/help/conditions/resource-policies).
        """
        return pulumi.get(self, "condition")

    @condition.setter
    def condition(self, value: Optional[pulumi.Input['GoogleTypeExprArgs']]):
        pulumi.set(self, "condition", value)

    @property
    @pulumi.getter
    def members(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Specifies the principals requesting access for a Google Cloud resource. `members` can have the following values: * `allUsers`: A special identifier that represents anyone who is on the internet; with or without a Google account. * `allAuthenticatedUsers`: A special identifier that represents anyone who is authenticated with a Google account or a service account. * `user:{emailid}`: An email address that represents a specific Google account. For example, `alice@example.com` . * `serviceAccount:{emailid}`: An email address that represents a service account. For example, `my-other-app@appspot.gserviceaccount.com`. * `group:{emailid}`: An email address that represents a Google group. For example, `admins@example.com`. * `deleted:user:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a user that has been recently deleted. For example, `alice@example.com?uid=123456789012345678901`. If the user is recovered, this value reverts to `user:{emailid}` and the recovered user retains the role in the binding. * `deleted:serviceAccount:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a service account that has been recently deleted. For example, `my-other-app@appspot.gserviceaccount.com?uid=123456789012345678901`. If the service account is undeleted, this value reverts to `serviceAccount:{emailid}` and the undeleted service account retains the role in the binding. * `deleted:group:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a Google group that has been recently deleted. For example, `admins@example.com?uid=123456789012345678901`. If the group is recovered, this value reverts to `group:{emailid}` and the recovered group retains the role in the binding. * `domain:{domain}`: The G Suite domain (primary) that represents all the users of that domain. For example, `google.com` or `example.com`. 
        """
        return pulumi.get(self, "members")

    @members.setter
    def members(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "members", value)

    @property
    @pulumi.getter
    def role(self) -> Optional[pulumi.Input[str]]:
        """
        Role that is assigned to the list of `members`, or principals. For example, `roles/viewer`, `roles/editor`, or `roles/owner`.
        """
        return pulumi.get(self, "role")

    @role.setter
    def role(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "role", value)


@pulumi.input_type
class GoogleTypeExprArgs:
    def __init__(__self__, *,
                 description: Optional[pulumi.Input[str]] = None,
                 expression: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 title: Optional[pulumi.Input[str]] = None):
        """
        Represents a textual expression in the Common Expression Language (CEL) syntax. CEL is a C-like expression language. The syntax and semantics of CEL are documented at https://github.com/google/cel-spec. Example (Comparison): title: "Summary size limit" description: "Determines if a summary is less than 100 chars" expression: "document.summary.size() < 100" Example (Equality): title: "Requestor is owner" description: "Determines if requestor is the document owner" expression: "document.owner == request.auth.claims.email" Example (Logic): title: "Public documents" description: "Determine whether the document should be publicly visible" expression: "document.type != 'private' && document.type != 'internal'" Example (Data Manipulation): title: "Notification string" description: "Create a notification string with a timestamp." expression: "'New message received at ' + string(document.create_time)" The exact variables and functions that may be referenced within an expression are determined by the service that evaluates it. See the service documentation for additional information.
        :param pulumi.Input[str] description: Optional. Description of the expression. This is a longer text which describes the expression, e.g. when hovered over it in a UI.
        :param pulumi.Input[str] expression: Textual representation of an expression in Common Expression Language syntax.
        :param pulumi.Input[str] location: Optional. String indicating the location of the expression for error reporting, e.g. a file name and a position in the file.
        :param pulumi.Input[str] title: Optional. Title for the expression, i.e. a short string describing its purpose. This can be used e.g. in UIs which allow to enter the expression.
        """
        if description is not None:
            pulumi.set(__self__, "description", description)
        if expression is not None:
            pulumi.set(__self__, "expression", expression)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if title is not None:
            pulumi.set(__self__, "title", title)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. Description of the expression. This is a longer text which describes the expression, e.g. when hovered over it in a UI.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def expression(self) -> Optional[pulumi.Input[str]]:
        """
        Textual representation of an expression in Common Expression Language syntax.
        """
        return pulumi.get(self, "expression")

    @expression.setter
    def expression(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "expression", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. String indicating the location of the expression for error reporting, e.g. a file name and a position in the file.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def title(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. Title for the expression, i.e. a short string describing its purpose. This can be used e.g. in UIs which allow to enter the expression.
        """
        return pulumi.get(self, "title")

    @title.setter
    def title(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "title", value)


@pulumi.input_type
class IngressArgs:
    def __init__(__self__, *,
                 config: Optional[pulumi.Input['ConfigArgs']] = None):
        """
        Settings of how to connect to the ClientGateway. One of the following options should be set.
        :param pulumi.Input['ConfigArgs'] config: The basic ingress config for ClientGateways.
        """
        if config is not None:
            pulumi.set(__self__, "config", config)

    @property
    @pulumi.getter
    def config(self) -> Optional[pulumi.Input['ConfigArgs']]:
        """
        The basic ingress config for ClientGateways.
        """
        return pulumi.get(self, "config")

    @config.setter
    def config(self, value: Optional[pulumi.Input['ConfigArgs']]):
        pulumi.set(self, "config", value)


@pulumi.input_type
class PeeredVpcArgs:
    def __init__(__self__, *,
                 network_vpc: pulumi.Input[str]):
        """
        The peered VPC owned by the consumer project.
        :param pulumi.Input[str] network_vpc: The name of the peered VPC owned by the consumer project.
        """
        pulumi.set(__self__, "network_vpc", network_vpc)

    @property
    @pulumi.getter(name="networkVpc")
    def network_vpc(self) -> pulumi.Input[str]:
        """
        The name of the peered VPC owned by the consumer project.
        """
        return pulumi.get(self, "network_vpc")

    @network_vpc.setter
    def network_vpc(self, value: pulumi.Input[str]):
        pulumi.set(self, "network_vpc", value)


