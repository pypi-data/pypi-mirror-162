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
    'AcceleratorArgs',
    'AuditConfigArgs',
    'AuditLogConfigArgs',
    'BindingArgs',
    'CryptoKeyConfigArgs',
    'EventPublishConfigArgs',
    'ExprArgs',
    'NetworkConfigArgs',
    'VersionArgs',
]

@pulumi.input_type
class AcceleratorArgs:
    def __init__(__self__, *,
                 accelerator_type: Optional[pulumi.Input['AcceleratorAcceleratorType']] = None,
                 state: Optional[pulumi.Input['AcceleratorState']] = None):
        """
        Identifies Data Fusion accelerators for an instance.
        :param pulumi.Input['AcceleratorAcceleratorType'] accelerator_type: The type of an accelator for a CDF instance.
        :param pulumi.Input['AcceleratorState'] state: The state of the accelerator
        """
        if accelerator_type is not None:
            pulumi.set(__self__, "accelerator_type", accelerator_type)
        if state is not None:
            pulumi.set(__self__, "state", state)

    @property
    @pulumi.getter(name="acceleratorType")
    def accelerator_type(self) -> Optional[pulumi.Input['AcceleratorAcceleratorType']]:
        """
        The type of an accelator for a CDF instance.
        """
        return pulumi.get(self, "accelerator_type")

    @accelerator_type.setter
    def accelerator_type(self, value: Optional[pulumi.Input['AcceleratorAcceleratorType']]):
        pulumi.set(self, "accelerator_type", value)

    @property
    @pulumi.getter
    def state(self) -> Optional[pulumi.Input['AcceleratorState']]:
        """
        The state of the accelerator
        """
        return pulumi.get(self, "state")

    @state.setter
    def state(self, value: Optional[pulumi.Input['AcceleratorState']]):
        pulumi.set(self, "state", value)


@pulumi.input_type
class AuditConfigArgs:
    def __init__(__self__, *,
                 audit_log_configs: Optional[pulumi.Input[Sequence[pulumi.Input['AuditLogConfigArgs']]]] = None,
                 service: Optional[pulumi.Input[str]] = None):
        """
        Specifies the audit configuration for a service. The configuration determines which permission types are logged, and what identities, if any, are exempted from logging. An AuditConfig must have one or more AuditLogConfigs. If there are AuditConfigs for both `allServices` and a specific service, the union of the two AuditConfigs is used for that service: the log_types specified in each AuditConfig are enabled, and the exempted_members in each AuditLogConfig are exempted. Example Policy with multiple AuditConfigs: { "audit_configs": [ { "service": "allServices", "audit_log_configs": [ { "log_type": "DATA_READ", "exempted_members": [ "user:jose@example.com" ] }, { "log_type": "DATA_WRITE" }, { "log_type": "ADMIN_READ" } ] }, { "service": "sampleservice.googleapis.com", "audit_log_configs": [ { "log_type": "DATA_READ" }, { "log_type": "DATA_WRITE", "exempted_members": [ "user:aliya@example.com" ] } ] } ] } For sampleservice, this policy enables DATA_READ, DATA_WRITE and ADMIN_READ logging. It also exempts `jose@example.com` from DATA_READ logging, and `aliya@example.com` from DATA_WRITE logging.
        :param pulumi.Input[Sequence[pulumi.Input['AuditLogConfigArgs']]] audit_log_configs: The configuration for logging of each type of permission.
        :param pulumi.Input[str] service: Specifies a service that will be enabled for audit logging. For example, `storage.googleapis.com`, `cloudsql.googleapis.com`. `allServices` is a special value that covers all services.
        """
        if audit_log_configs is not None:
            pulumi.set(__self__, "audit_log_configs", audit_log_configs)
        if service is not None:
            pulumi.set(__self__, "service", service)

    @property
    @pulumi.getter(name="auditLogConfigs")
    def audit_log_configs(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['AuditLogConfigArgs']]]]:
        """
        The configuration for logging of each type of permission.
        """
        return pulumi.get(self, "audit_log_configs")

    @audit_log_configs.setter
    def audit_log_configs(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['AuditLogConfigArgs']]]]):
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
class AuditLogConfigArgs:
    def __init__(__self__, *,
                 exempted_members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 log_type: Optional[pulumi.Input['AuditLogConfigLogType']] = None):
        """
        Provides the configuration for logging a type of permissions. Example: { "audit_log_configs": [ { "log_type": "DATA_READ", "exempted_members": [ "user:jose@example.com" ] }, { "log_type": "DATA_WRITE" } ] } This enables 'DATA_READ' and 'DATA_WRITE' logging, while exempting jose@example.com from DATA_READ logging.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] exempted_members: Specifies the identities that do not cause logging for this type of permission. Follows the same format of Binding.members.
        :param pulumi.Input['AuditLogConfigLogType'] log_type: The log type that this config enables.
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
    def log_type(self) -> Optional[pulumi.Input['AuditLogConfigLogType']]:
        """
        The log type that this config enables.
        """
        return pulumi.get(self, "log_type")

    @log_type.setter
    def log_type(self, value: Optional[pulumi.Input['AuditLogConfigLogType']]):
        pulumi.set(self, "log_type", value)


@pulumi.input_type
class BindingArgs:
    def __init__(__self__, *,
                 condition: Optional[pulumi.Input['ExprArgs']] = None,
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 role: Optional[pulumi.Input[str]] = None):
        """
        Associates `members`, or principals, with a `role`.
        :param pulumi.Input['ExprArgs'] condition: The condition that is associated with this binding. If the condition evaluates to `true`, then this binding applies to the current request. If the condition evaluates to `false`, then this binding does not apply to the current request. However, a different role binding might grant the same role to one or more of the principals in this binding. To learn which resources support conditions in their IAM policies, see the [IAM documentation](https://cloud.google.com/iam/help/conditions/resource-policies).
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
    def condition(self) -> Optional[pulumi.Input['ExprArgs']]:
        """
        The condition that is associated with this binding. If the condition evaluates to `true`, then this binding applies to the current request. If the condition evaluates to `false`, then this binding does not apply to the current request. However, a different role binding might grant the same role to one or more of the principals in this binding. To learn which resources support conditions in their IAM policies, see the [IAM documentation](https://cloud.google.com/iam/help/conditions/resource-policies).
        """
        return pulumi.get(self, "condition")

    @condition.setter
    def condition(self, value: Optional[pulumi.Input['ExprArgs']]):
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
class CryptoKeyConfigArgs:
    def __init__(__self__, *,
                 key_reference: Optional[pulumi.Input[str]] = None):
        """
        The crypto key configuration. This field is used by the Customer-managed encryption keys (CMEK) feature.
        :param pulumi.Input[str] key_reference: The name of the key which is used to encrypt/decrypt customer data. For key in Cloud KMS, the key should be in the format of `projects/*/locations/*/keyRings/*/cryptoKeys/*`.
        """
        if key_reference is not None:
            pulumi.set(__self__, "key_reference", key_reference)

    @property
    @pulumi.getter(name="keyReference")
    def key_reference(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the key which is used to encrypt/decrypt customer data. For key in Cloud KMS, the key should be in the format of `projects/*/locations/*/keyRings/*/cryptoKeys/*`.
        """
        return pulumi.get(self, "key_reference")

    @key_reference.setter
    def key_reference(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "key_reference", value)


@pulumi.input_type
class EventPublishConfigArgs:
    def __init__(__self__, *,
                 enabled: pulumi.Input[bool],
                 topic: pulumi.Input[str]):
        """
        Confirguration of PubSubEventWriter.
        :param pulumi.Input[bool] enabled: Option to enable Event Publishing.
        :param pulumi.Input[str] topic: The resource name of the Pub/Sub topic. Format: projects/{project_id}/topics/{topic_id}
        """
        pulumi.set(__self__, "enabled", enabled)
        pulumi.set(__self__, "topic", topic)

    @property
    @pulumi.getter
    def enabled(self) -> pulumi.Input[bool]:
        """
        Option to enable Event Publishing.
        """
        return pulumi.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: pulumi.Input[bool]):
        pulumi.set(self, "enabled", value)

    @property
    @pulumi.getter
    def topic(self) -> pulumi.Input[str]:
        """
        The resource name of the Pub/Sub topic. Format: projects/{project_id}/topics/{topic_id}
        """
        return pulumi.get(self, "topic")

    @topic.setter
    def topic(self, value: pulumi.Input[str]):
        pulumi.set(self, "topic", value)


@pulumi.input_type
class ExprArgs:
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
class NetworkConfigArgs:
    def __init__(__self__, *,
                 ip_allocation: Optional[pulumi.Input[str]] = None,
                 network: Optional[pulumi.Input[str]] = None):
        """
        Network configuration for a Data Fusion instance. These configurations are used for peering with the customer network. Configurations are optional when a public Data Fusion instance is to be created. However, providing these configurations allows several benefits, such as reduced network latency while accessing the customer resources from managed Data Fusion instance nodes, as well as access to the customer on-prem resources.
        :param pulumi.Input[str] ip_allocation: The IP range in CIDR notation to use for the managed Data Fusion instance nodes. This range must not overlap with any other ranges used in the customer network.
        :param pulumi.Input[str] network: Name of the network in the customer project with which the Tenant Project will be peered for executing pipelines. In case of shared VPC where the network resides in another host project the network should specified in the form of projects/{host-project-id}/global/networks/{network}
        """
        if ip_allocation is not None:
            pulumi.set(__self__, "ip_allocation", ip_allocation)
        if network is not None:
            pulumi.set(__self__, "network", network)

    @property
    @pulumi.getter(name="ipAllocation")
    def ip_allocation(self) -> Optional[pulumi.Input[str]]:
        """
        The IP range in CIDR notation to use for the managed Data Fusion instance nodes. This range must not overlap with any other ranges used in the customer network.
        """
        return pulumi.get(self, "ip_allocation")

    @ip_allocation.setter
    def ip_allocation(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "ip_allocation", value)

    @property
    @pulumi.getter
    def network(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the network in the customer project with which the Tenant Project will be peered for executing pipelines. In case of shared VPC where the network resides in another host project the network should specified in the form of projects/{host-project-id}/global/networks/{network}
        """
        return pulumi.get(self, "network")

    @network.setter
    def network(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "network", value)


@pulumi.input_type
class VersionArgs:
    def __init__(__self__, *,
                 available_features: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 default_version: Optional[pulumi.Input[bool]] = None,
                 type: Optional[pulumi.Input['VersionType']] = None,
                 version_number: Optional[pulumi.Input[str]] = None):
        """
        The Data Fusion version. This proto message stores information about certain Data Fusion version, which is used for Data Fusion version upgrade.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] available_features: Represents a list of available feature names for a given version.
        :param pulumi.Input[bool] default_version: Whether this is currently the default version for Cloud Data Fusion
        :param pulumi.Input['VersionType'] type: Type represents the release availability of the version
        :param pulumi.Input[str] version_number: The version number of the Data Fusion instance, such as '6.0.1.0'.
        """
        if available_features is not None:
            pulumi.set(__self__, "available_features", available_features)
        if default_version is not None:
            pulumi.set(__self__, "default_version", default_version)
        if type is not None:
            pulumi.set(__self__, "type", type)
        if version_number is not None:
            pulumi.set(__self__, "version_number", version_number)

    @property
    @pulumi.getter(name="availableFeatures")
    def available_features(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Represents a list of available feature names for a given version.
        """
        return pulumi.get(self, "available_features")

    @available_features.setter
    def available_features(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "available_features", value)

    @property
    @pulumi.getter(name="defaultVersion")
    def default_version(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether this is currently the default version for Cloud Data Fusion
        """
        return pulumi.get(self, "default_version")

    @default_version.setter
    def default_version(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "default_version", value)

    @property
    @pulumi.getter
    def type(self) -> Optional[pulumi.Input['VersionType']]:
        """
        Type represents the release availability of the version
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: Optional[pulumi.Input['VersionType']]):
        pulumi.set(self, "type", value)

    @property
    @pulumi.getter(name="versionNumber")
    def version_number(self) -> Optional[pulumi.Input[str]]:
        """
        The version number of the Data Fusion instance, such as '6.0.1.0'.
        """
        return pulumi.get(self, "version_number")

    @version_number.setter
    def version_number(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "version_number", value)


