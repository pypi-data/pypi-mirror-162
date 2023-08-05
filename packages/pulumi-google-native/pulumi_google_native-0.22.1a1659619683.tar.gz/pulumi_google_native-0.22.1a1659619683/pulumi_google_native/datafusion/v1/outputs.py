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

__all__ = [
    'AcceleratorResponse',
    'AuditConfigResponse',
    'AuditLogConfigResponse',
    'BindingResponse',
    'CryptoKeyConfigResponse',
    'EventPublishConfigResponse',
    'ExprResponse',
    'NetworkConfigResponse',
    'VersionResponse',
]

@pulumi.output_type
class AcceleratorResponse(dict):
    """
    Identifies Data Fusion accelerators for an instance.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "acceleratorType":
            suggest = "accelerator_type"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in AcceleratorResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        AcceleratorResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        AcceleratorResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 accelerator_type: str,
                 state: str):
        """
        Identifies Data Fusion accelerators for an instance.
        :param str accelerator_type: The type of an accelator for a CDF instance.
        :param str state: The state of the accelerator
        """
        pulumi.set(__self__, "accelerator_type", accelerator_type)
        pulumi.set(__self__, "state", state)

    @property
    @pulumi.getter(name="acceleratorType")
    def accelerator_type(self) -> str:
        """
        The type of an accelator for a CDF instance.
        """
        return pulumi.get(self, "accelerator_type")

    @property
    @pulumi.getter
    def state(self) -> str:
        """
        The state of the accelerator
        """
        return pulumi.get(self, "state")


@pulumi.output_type
class AuditConfigResponse(dict):
    """
    Specifies the audit configuration for a service. The configuration determines which permission types are logged, and what identities, if any, are exempted from logging. An AuditConfig must have one or more AuditLogConfigs. If there are AuditConfigs for both `allServices` and a specific service, the union of the two AuditConfigs is used for that service: the log_types specified in each AuditConfig are enabled, and the exempted_members in each AuditLogConfig are exempted. Example Policy with multiple AuditConfigs: { "audit_configs": [ { "service": "allServices", "audit_log_configs": [ { "log_type": "DATA_READ", "exempted_members": [ "user:jose@example.com" ] }, { "log_type": "DATA_WRITE" }, { "log_type": "ADMIN_READ" } ] }, { "service": "sampleservice.googleapis.com", "audit_log_configs": [ { "log_type": "DATA_READ" }, { "log_type": "DATA_WRITE", "exempted_members": [ "user:aliya@example.com" ] } ] } ] } For sampleservice, this policy enables DATA_READ, DATA_WRITE and ADMIN_READ logging. It also exempts `jose@example.com` from DATA_READ logging, and `aliya@example.com` from DATA_WRITE logging.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "auditLogConfigs":
            suggest = "audit_log_configs"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in AuditConfigResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        AuditConfigResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        AuditConfigResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 audit_log_configs: Sequence['outputs.AuditLogConfigResponse'],
                 service: str):
        """
        Specifies the audit configuration for a service. The configuration determines which permission types are logged, and what identities, if any, are exempted from logging. An AuditConfig must have one or more AuditLogConfigs. If there are AuditConfigs for both `allServices` and a specific service, the union of the two AuditConfigs is used for that service: the log_types specified in each AuditConfig are enabled, and the exempted_members in each AuditLogConfig are exempted. Example Policy with multiple AuditConfigs: { "audit_configs": [ { "service": "allServices", "audit_log_configs": [ { "log_type": "DATA_READ", "exempted_members": [ "user:jose@example.com" ] }, { "log_type": "DATA_WRITE" }, { "log_type": "ADMIN_READ" } ] }, { "service": "sampleservice.googleapis.com", "audit_log_configs": [ { "log_type": "DATA_READ" }, { "log_type": "DATA_WRITE", "exempted_members": [ "user:aliya@example.com" ] } ] } ] } For sampleservice, this policy enables DATA_READ, DATA_WRITE and ADMIN_READ logging. It also exempts `jose@example.com` from DATA_READ logging, and `aliya@example.com` from DATA_WRITE logging.
        :param Sequence['AuditLogConfigResponse'] audit_log_configs: The configuration for logging of each type of permission.
        :param str service: Specifies a service that will be enabled for audit logging. For example, `storage.googleapis.com`, `cloudsql.googleapis.com`. `allServices` is a special value that covers all services.
        """
        pulumi.set(__self__, "audit_log_configs", audit_log_configs)
        pulumi.set(__self__, "service", service)

    @property
    @pulumi.getter(name="auditLogConfigs")
    def audit_log_configs(self) -> Sequence['outputs.AuditLogConfigResponse']:
        """
        The configuration for logging of each type of permission.
        """
        return pulumi.get(self, "audit_log_configs")

    @property
    @pulumi.getter
    def service(self) -> str:
        """
        Specifies a service that will be enabled for audit logging. For example, `storage.googleapis.com`, `cloudsql.googleapis.com`. `allServices` is a special value that covers all services.
        """
        return pulumi.get(self, "service")


@pulumi.output_type
class AuditLogConfigResponse(dict):
    """
    Provides the configuration for logging a type of permissions. Example: { "audit_log_configs": [ { "log_type": "DATA_READ", "exempted_members": [ "user:jose@example.com" ] }, { "log_type": "DATA_WRITE" } ] } This enables 'DATA_READ' and 'DATA_WRITE' logging, while exempting jose@example.com from DATA_READ logging.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "exemptedMembers":
            suggest = "exempted_members"
        elif key == "logType":
            suggest = "log_type"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in AuditLogConfigResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        AuditLogConfigResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        AuditLogConfigResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 exempted_members: Sequence[str],
                 log_type: str):
        """
        Provides the configuration for logging a type of permissions. Example: { "audit_log_configs": [ { "log_type": "DATA_READ", "exempted_members": [ "user:jose@example.com" ] }, { "log_type": "DATA_WRITE" } ] } This enables 'DATA_READ' and 'DATA_WRITE' logging, while exempting jose@example.com from DATA_READ logging.
        :param Sequence[str] exempted_members: Specifies the identities that do not cause logging for this type of permission. Follows the same format of Binding.members.
        :param str log_type: The log type that this config enables.
        """
        pulumi.set(__self__, "exempted_members", exempted_members)
        pulumi.set(__self__, "log_type", log_type)

    @property
    @pulumi.getter(name="exemptedMembers")
    def exempted_members(self) -> Sequence[str]:
        """
        Specifies the identities that do not cause logging for this type of permission. Follows the same format of Binding.members.
        """
        return pulumi.get(self, "exempted_members")

    @property
    @pulumi.getter(name="logType")
    def log_type(self) -> str:
        """
        The log type that this config enables.
        """
        return pulumi.get(self, "log_type")


@pulumi.output_type
class BindingResponse(dict):
    """
    Associates `members`, or principals, with a `role`.
    """
    def __init__(__self__, *,
                 condition: 'outputs.ExprResponse',
                 members: Sequence[str],
                 role: str):
        """
        Associates `members`, or principals, with a `role`.
        :param 'ExprResponse' condition: The condition that is associated with this binding. If the condition evaluates to `true`, then this binding applies to the current request. If the condition evaluates to `false`, then this binding does not apply to the current request. However, a different role binding might grant the same role to one or more of the principals in this binding. To learn which resources support conditions in their IAM policies, see the [IAM documentation](https://cloud.google.com/iam/help/conditions/resource-policies).
        :param Sequence[str] members: Specifies the principals requesting access for a Google Cloud resource. `members` can have the following values: * `allUsers`: A special identifier that represents anyone who is on the internet; with or without a Google account. * `allAuthenticatedUsers`: A special identifier that represents anyone who is authenticated with a Google account or a service account. * `user:{emailid}`: An email address that represents a specific Google account. For example, `alice@example.com` . * `serviceAccount:{emailid}`: An email address that represents a service account. For example, `my-other-app@appspot.gserviceaccount.com`. * `group:{emailid}`: An email address that represents a Google group. For example, `admins@example.com`. * `deleted:user:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a user that has been recently deleted. For example, `alice@example.com?uid=123456789012345678901`. If the user is recovered, this value reverts to `user:{emailid}` and the recovered user retains the role in the binding. * `deleted:serviceAccount:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a service account that has been recently deleted. For example, `my-other-app@appspot.gserviceaccount.com?uid=123456789012345678901`. If the service account is undeleted, this value reverts to `serviceAccount:{emailid}` and the undeleted service account retains the role in the binding. * `deleted:group:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a Google group that has been recently deleted. For example, `admins@example.com?uid=123456789012345678901`. If the group is recovered, this value reverts to `group:{emailid}` and the recovered group retains the role in the binding. * `domain:{domain}`: The G Suite domain (primary) that represents all the users of that domain. For example, `google.com` or `example.com`. 
        :param str role: Role that is assigned to the list of `members`, or principals. For example, `roles/viewer`, `roles/editor`, or `roles/owner`.
        """
        pulumi.set(__self__, "condition", condition)
        pulumi.set(__self__, "members", members)
        pulumi.set(__self__, "role", role)

    @property
    @pulumi.getter
    def condition(self) -> 'outputs.ExprResponse':
        """
        The condition that is associated with this binding. If the condition evaluates to `true`, then this binding applies to the current request. If the condition evaluates to `false`, then this binding does not apply to the current request. However, a different role binding might grant the same role to one or more of the principals in this binding. To learn which resources support conditions in their IAM policies, see the [IAM documentation](https://cloud.google.com/iam/help/conditions/resource-policies).
        """
        return pulumi.get(self, "condition")

    @property
    @pulumi.getter
    def members(self) -> Sequence[str]:
        """
        Specifies the principals requesting access for a Google Cloud resource. `members` can have the following values: * `allUsers`: A special identifier that represents anyone who is on the internet; with or without a Google account. * `allAuthenticatedUsers`: A special identifier that represents anyone who is authenticated with a Google account or a service account. * `user:{emailid}`: An email address that represents a specific Google account. For example, `alice@example.com` . * `serviceAccount:{emailid}`: An email address that represents a service account. For example, `my-other-app@appspot.gserviceaccount.com`. * `group:{emailid}`: An email address that represents a Google group. For example, `admins@example.com`. * `deleted:user:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a user that has been recently deleted. For example, `alice@example.com?uid=123456789012345678901`. If the user is recovered, this value reverts to `user:{emailid}` and the recovered user retains the role in the binding. * `deleted:serviceAccount:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a service account that has been recently deleted. For example, `my-other-app@appspot.gserviceaccount.com?uid=123456789012345678901`. If the service account is undeleted, this value reverts to `serviceAccount:{emailid}` and the undeleted service account retains the role in the binding. * `deleted:group:{emailid}?uid={uniqueid}`: An email address (plus unique identifier) representing a Google group that has been recently deleted. For example, `admins@example.com?uid=123456789012345678901`. If the group is recovered, this value reverts to `group:{emailid}` and the recovered group retains the role in the binding. * `domain:{domain}`: The G Suite domain (primary) that represents all the users of that domain. For example, `google.com` or `example.com`. 
        """
        return pulumi.get(self, "members")

    @property
    @pulumi.getter
    def role(self) -> str:
        """
        Role that is assigned to the list of `members`, or principals. For example, `roles/viewer`, `roles/editor`, or `roles/owner`.
        """
        return pulumi.get(self, "role")


@pulumi.output_type
class CryptoKeyConfigResponse(dict):
    """
    The crypto key configuration. This field is used by the Customer-managed encryption keys (CMEK) feature.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "keyReference":
            suggest = "key_reference"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in CryptoKeyConfigResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        CryptoKeyConfigResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        CryptoKeyConfigResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 key_reference: str):
        """
        The crypto key configuration. This field is used by the Customer-managed encryption keys (CMEK) feature.
        :param str key_reference: The name of the key which is used to encrypt/decrypt customer data. For key in Cloud KMS, the key should be in the format of `projects/*/locations/*/keyRings/*/cryptoKeys/*`.
        """
        pulumi.set(__self__, "key_reference", key_reference)

    @property
    @pulumi.getter(name="keyReference")
    def key_reference(self) -> str:
        """
        The name of the key which is used to encrypt/decrypt customer data. For key in Cloud KMS, the key should be in the format of `projects/*/locations/*/keyRings/*/cryptoKeys/*`.
        """
        return pulumi.get(self, "key_reference")


@pulumi.output_type
class EventPublishConfigResponse(dict):
    """
    Confirguration of PubSubEventWriter.
    """
    def __init__(__self__, *,
                 enabled: bool,
                 topic: str):
        """
        Confirguration of PubSubEventWriter.
        :param bool enabled: Option to enable Event Publishing.
        :param str topic: The resource name of the Pub/Sub topic. Format: projects/{project_id}/topics/{topic_id}
        """
        pulumi.set(__self__, "enabled", enabled)
        pulumi.set(__self__, "topic", topic)

    @property
    @pulumi.getter
    def enabled(self) -> bool:
        """
        Option to enable Event Publishing.
        """
        return pulumi.get(self, "enabled")

    @property
    @pulumi.getter
    def topic(self) -> str:
        """
        The resource name of the Pub/Sub topic. Format: projects/{project_id}/topics/{topic_id}
        """
        return pulumi.get(self, "topic")


@pulumi.output_type
class ExprResponse(dict):
    """
    Represents a textual expression in the Common Expression Language (CEL) syntax. CEL is a C-like expression language. The syntax and semantics of CEL are documented at https://github.com/google/cel-spec. Example (Comparison): title: "Summary size limit" description: "Determines if a summary is less than 100 chars" expression: "document.summary.size() < 100" Example (Equality): title: "Requestor is owner" description: "Determines if requestor is the document owner" expression: "document.owner == request.auth.claims.email" Example (Logic): title: "Public documents" description: "Determine whether the document should be publicly visible" expression: "document.type != 'private' && document.type != 'internal'" Example (Data Manipulation): title: "Notification string" description: "Create a notification string with a timestamp." expression: "'New message received at ' + string(document.create_time)" The exact variables and functions that may be referenced within an expression are determined by the service that evaluates it. See the service documentation for additional information.
    """
    def __init__(__self__, *,
                 description: str,
                 expression: str,
                 location: str,
                 title: str):
        """
        Represents a textual expression in the Common Expression Language (CEL) syntax. CEL is a C-like expression language. The syntax and semantics of CEL are documented at https://github.com/google/cel-spec. Example (Comparison): title: "Summary size limit" description: "Determines if a summary is less than 100 chars" expression: "document.summary.size() < 100" Example (Equality): title: "Requestor is owner" description: "Determines if requestor is the document owner" expression: "document.owner == request.auth.claims.email" Example (Logic): title: "Public documents" description: "Determine whether the document should be publicly visible" expression: "document.type != 'private' && document.type != 'internal'" Example (Data Manipulation): title: "Notification string" description: "Create a notification string with a timestamp." expression: "'New message received at ' + string(document.create_time)" The exact variables and functions that may be referenced within an expression are determined by the service that evaluates it. See the service documentation for additional information.
        :param str description: Optional. Description of the expression. This is a longer text which describes the expression, e.g. when hovered over it in a UI.
        :param str expression: Textual representation of an expression in Common Expression Language syntax.
        :param str location: Optional. String indicating the location of the expression for error reporting, e.g. a file name and a position in the file.
        :param str title: Optional. Title for the expression, i.e. a short string describing its purpose. This can be used e.g. in UIs which allow to enter the expression.
        """
        pulumi.set(__self__, "description", description)
        pulumi.set(__self__, "expression", expression)
        pulumi.set(__self__, "location", location)
        pulumi.set(__self__, "title", title)

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        Optional. Description of the expression. This is a longer text which describes the expression, e.g. when hovered over it in a UI.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def expression(self) -> str:
        """
        Textual representation of an expression in Common Expression Language syntax.
        """
        return pulumi.get(self, "expression")

    @property
    @pulumi.getter
    def location(self) -> str:
        """
        Optional. String indicating the location of the expression for error reporting, e.g. a file name and a position in the file.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def title(self) -> str:
        """
        Optional. Title for the expression, i.e. a short string describing its purpose. This can be used e.g. in UIs which allow to enter the expression.
        """
        return pulumi.get(self, "title")


@pulumi.output_type
class NetworkConfigResponse(dict):
    """
    Network configuration for a Data Fusion instance. These configurations are used for peering with the customer network. Configurations are optional when a public Data Fusion instance is to be created. However, providing these configurations allows several benefits, such as reduced network latency while accessing the customer resources from managed Data Fusion instance nodes, as well as access to the customer on-prem resources.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "ipAllocation":
            suggest = "ip_allocation"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in NetworkConfigResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        NetworkConfigResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        NetworkConfigResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 ip_allocation: str,
                 network: str):
        """
        Network configuration for a Data Fusion instance. These configurations are used for peering with the customer network. Configurations are optional when a public Data Fusion instance is to be created. However, providing these configurations allows several benefits, such as reduced network latency while accessing the customer resources from managed Data Fusion instance nodes, as well as access to the customer on-prem resources.
        :param str ip_allocation: The IP range in CIDR notation to use for the managed Data Fusion instance nodes. This range must not overlap with any other ranges used in the customer network.
        :param str network: Name of the network in the customer project with which the Tenant Project will be peered for executing pipelines. In case of shared VPC where the network resides in another host project the network should specified in the form of projects/{host-project-id}/global/networks/{network}
        """
        pulumi.set(__self__, "ip_allocation", ip_allocation)
        pulumi.set(__self__, "network", network)

    @property
    @pulumi.getter(name="ipAllocation")
    def ip_allocation(self) -> str:
        """
        The IP range in CIDR notation to use for the managed Data Fusion instance nodes. This range must not overlap with any other ranges used in the customer network.
        """
        return pulumi.get(self, "ip_allocation")

    @property
    @pulumi.getter
    def network(self) -> str:
        """
        Name of the network in the customer project with which the Tenant Project will be peered for executing pipelines. In case of shared VPC where the network resides in another host project the network should specified in the form of projects/{host-project-id}/global/networks/{network}
        """
        return pulumi.get(self, "network")


@pulumi.output_type
class VersionResponse(dict):
    """
    The Data Fusion version. This proto message stores information about certain Data Fusion version, which is used for Data Fusion version upgrade.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "availableFeatures":
            suggest = "available_features"
        elif key == "defaultVersion":
            suggest = "default_version"
        elif key == "versionNumber":
            suggest = "version_number"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in VersionResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        VersionResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        VersionResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 available_features: Sequence[str],
                 default_version: bool,
                 type: str,
                 version_number: str):
        """
        The Data Fusion version. This proto message stores information about certain Data Fusion version, which is used for Data Fusion version upgrade.
        :param Sequence[str] available_features: Represents a list of available feature names for a given version.
        :param bool default_version: Whether this is currently the default version for Cloud Data Fusion
        :param str type: Type represents the release availability of the version
        :param str version_number: The version number of the Data Fusion instance, such as '6.0.1.0'.
        """
        pulumi.set(__self__, "available_features", available_features)
        pulumi.set(__self__, "default_version", default_version)
        pulumi.set(__self__, "type", type)
        pulumi.set(__self__, "version_number", version_number)

    @property
    @pulumi.getter(name="availableFeatures")
    def available_features(self) -> Sequence[str]:
        """
        Represents a list of available feature names for a given version.
        """
        return pulumi.get(self, "available_features")

    @property
    @pulumi.getter(name="defaultVersion")
    def default_version(self) -> bool:
        """
        Whether this is currently the default version for Cloud Data Fusion
        """
        return pulumi.get(self, "default_version")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        Type represents the release availability of the version
        """
        return pulumi.get(self, "type")

    @property
    @pulumi.getter(name="versionNumber")
    def version_number(self) -> str:
        """
        The version number of the Data Fusion instance, such as '6.0.1.0'.
        """
        return pulumi.get(self, "version_number")


