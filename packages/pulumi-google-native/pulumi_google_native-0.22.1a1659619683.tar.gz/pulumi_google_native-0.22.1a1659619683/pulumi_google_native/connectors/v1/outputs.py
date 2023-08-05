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
    'AuditConfigResponse',
    'AuditLogConfigResponse',
    'AuthConfigResponse',
    'BindingResponse',
    'ConfigVariableResponse',
    'ConnectionStatusResponse',
    'ExprResponse',
    'JwtClaimsResponse',
    'LockConfigResponse',
    'Oauth2ClientCredentialsResponse',
    'Oauth2JwtBearerResponse',
    'SecretResponse',
    'SshPublicKeyResponse',
    'UserPasswordResponse',
]

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
class AuthConfigResponse(dict):
    """
    AuthConfig defines details of a authentication type.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "additionalVariables":
            suggest = "additional_variables"
        elif key == "authType":
            suggest = "auth_type"
        elif key == "oauth2ClientCredentials":
            suggest = "oauth2_client_credentials"
        elif key == "oauth2JwtBearer":
            suggest = "oauth2_jwt_bearer"
        elif key == "sshPublicKey":
            suggest = "ssh_public_key"
        elif key == "userPassword":
            suggest = "user_password"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in AuthConfigResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        AuthConfigResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        AuthConfigResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 additional_variables: Sequence['outputs.ConfigVariableResponse'],
                 auth_type: str,
                 oauth2_client_credentials: 'outputs.Oauth2ClientCredentialsResponse',
                 oauth2_jwt_bearer: 'outputs.Oauth2JwtBearerResponse',
                 ssh_public_key: 'outputs.SshPublicKeyResponse',
                 user_password: 'outputs.UserPasswordResponse'):
        """
        AuthConfig defines details of a authentication type.
        :param Sequence['ConfigVariableResponse'] additional_variables: List containing additional auth configs.
        :param str auth_type: The type of authentication configured.
        :param 'Oauth2ClientCredentialsResponse' oauth2_client_credentials: Oauth2ClientCredentials.
        :param 'Oauth2JwtBearerResponse' oauth2_jwt_bearer: Oauth2JwtBearer.
        :param 'SshPublicKeyResponse' ssh_public_key: SSH Public Key.
        :param 'UserPasswordResponse' user_password: UserPassword.
        """
        pulumi.set(__self__, "additional_variables", additional_variables)
        pulumi.set(__self__, "auth_type", auth_type)
        pulumi.set(__self__, "oauth2_client_credentials", oauth2_client_credentials)
        pulumi.set(__self__, "oauth2_jwt_bearer", oauth2_jwt_bearer)
        pulumi.set(__self__, "ssh_public_key", ssh_public_key)
        pulumi.set(__self__, "user_password", user_password)

    @property
    @pulumi.getter(name="additionalVariables")
    def additional_variables(self) -> Sequence['outputs.ConfigVariableResponse']:
        """
        List containing additional auth configs.
        """
        return pulumi.get(self, "additional_variables")

    @property
    @pulumi.getter(name="authType")
    def auth_type(self) -> str:
        """
        The type of authentication configured.
        """
        return pulumi.get(self, "auth_type")

    @property
    @pulumi.getter(name="oauth2ClientCredentials")
    def oauth2_client_credentials(self) -> 'outputs.Oauth2ClientCredentialsResponse':
        """
        Oauth2ClientCredentials.
        """
        return pulumi.get(self, "oauth2_client_credentials")

    @property
    @pulumi.getter(name="oauth2JwtBearer")
    def oauth2_jwt_bearer(self) -> 'outputs.Oauth2JwtBearerResponse':
        """
        Oauth2JwtBearer.
        """
        return pulumi.get(self, "oauth2_jwt_bearer")

    @property
    @pulumi.getter(name="sshPublicKey")
    def ssh_public_key(self) -> 'outputs.SshPublicKeyResponse':
        """
        SSH Public Key.
        """
        return pulumi.get(self, "ssh_public_key")

    @property
    @pulumi.getter(name="userPassword")
    def user_password(self) -> 'outputs.UserPasswordResponse':
        """
        UserPassword.
        """
        return pulumi.get(self, "user_password")


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
class ConfigVariableResponse(dict):
    """
    ConfigVariable represents a configuration variable present in a Connection. or AuthConfig.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "boolValue":
            suggest = "bool_value"
        elif key == "intValue":
            suggest = "int_value"
        elif key == "secretValue":
            suggest = "secret_value"
        elif key == "stringValue":
            suggest = "string_value"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in ConfigVariableResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        ConfigVariableResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        ConfigVariableResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 bool_value: bool,
                 int_value: str,
                 key: str,
                 secret_value: 'outputs.SecretResponse',
                 string_value: str):
        """
        ConfigVariable represents a configuration variable present in a Connection. or AuthConfig.
        :param bool bool_value: Value is a bool.
        :param str int_value: Value is an integer
        :param str key: Key of the config variable.
        :param 'SecretResponse' secret_value: Value is a secret.
        :param str string_value: Value is a string.
        """
        pulumi.set(__self__, "bool_value", bool_value)
        pulumi.set(__self__, "int_value", int_value)
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "secret_value", secret_value)
        pulumi.set(__self__, "string_value", string_value)

    @property
    @pulumi.getter(name="boolValue")
    def bool_value(self) -> bool:
        """
        Value is a bool.
        """
        return pulumi.get(self, "bool_value")

    @property
    @pulumi.getter(name="intValue")
    def int_value(self) -> str:
        """
        Value is an integer
        """
        return pulumi.get(self, "int_value")

    @property
    @pulumi.getter
    def key(self) -> str:
        """
        Key of the config variable.
        """
        return pulumi.get(self, "key")

    @property
    @pulumi.getter(name="secretValue")
    def secret_value(self) -> 'outputs.SecretResponse':
        """
        Value is a secret.
        """
        return pulumi.get(self, "secret_value")

    @property
    @pulumi.getter(name="stringValue")
    def string_value(self) -> str:
        """
        Value is a string.
        """
        return pulumi.get(self, "string_value")


@pulumi.output_type
class ConnectionStatusResponse(dict):
    """
    ConnectionStatus indicates the state of the connection.
    """
    def __init__(__self__, *,
                 description: str,
                 state: str,
                 status: str):
        """
        ConnectionStatus indicates the state of the connection.
        :param str description: Description.
        :param str state: State.
        :param str status: Status provides detailed information for the state.
        """
        pulumi.set(__self__, "description", description)
        pulumi.set(__self__, "state", state)
        pulumi.set(__self__, "status", status)

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        Description.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def state(self) -> str:
        """
        State.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter
    def status(self) -> str:
        """
        Status provides detailed information for the state.
        """
        return pulumi.get(self, "status")


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
class JwtClaimsResponse(dict):
    """
    JWT claims used for the jwt-bearer authorization grant.
    """
    def __init__(__self__, *,
                 audience: str,
                 issuer: str,
                 subject: str):
        """
        JWT claims used for the jwt-bearer authorization grant.
        :param str audience: Value for the "aud" claim.
        :param str issuer: Value for the "iss" claim.
        :param str subject: Value for the "sub" claim.
        """
        pulumi.set(__self__, "audience", audience)
        pulumi.set(__self__, "issuer", issuer)
        pulumi.set(__self__, "subject", subject)

    @property
    @pulumi.getter
    def audience(self) -> str:
        """
        Value for the "aud" claim.
        """
        return pulumi.get(self, "audience")

    @property
    @pulumi.getter
    def issuer(self) -> str:
        """
        Value for the "iss" claim.
        """
        return pulumi.get(self, "issuer")

    @property
    @pulumi.getter
    def subject(self) -> str:
        """
        Value for the "sub" claim.
        """
        return pulumi.get(self, "subject")


@pulumi.output_type
class LockConfigResponse(dict):
    """
    Determines whether or no a connection is locked. If locked, a reason must be specified.
    """
    def __init__(__self__, *,
                 locked: bool,
                 reason: str):
        """
        Determines whether or no a connection is locked. If locked, a reason must be specified.
        :param bool locked: Indicates whether or not the connection is locked.
        :param str reason: Describes why a connection is locked.
        """
        pulumi.set(__self__, "locked", locked)
        pulumi.set(__self__, "reason", reason)

    @property
    @pulumi.getter
    def locked(self) -> bool:
        """
        Indicates whether or not the connection is locked.
        """
        return pulumi.get(self, "locked")

    @property
    @pulumi.getter
    def reason(self) -> str:
        """
        Describes why a connection is locked.
        """
        return pulumi.get(self, "reason")


@pulumi.output_type
class Oauth2ClientCredentialsResponse(dict):
    """
    Parameters to support Oauth 2.0 Client Credentials Grant Authentication. See https://tools.ietf.org/html/rfc6749#section-1.3.4 for more details.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "clientId":
            suggest = "client_id"
        elif key == "clientSecret":
            suggest = "client_secret"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in Oauth2ClientCredentialsResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        Oauth2ClientCredentialsResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        Oauth2ClientCredentialsResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 client_id: str,
                 client_secret: 'outputs.SecretResponse'):
        """
        Parameters to support Oauth 2.0 Client Credentials Grant Authentication. See https://tools.ietf.org/html/rfc6749#section-1.3.4 for more details.
        :param str client_id: The client identifier.
        :param 'SecretResponse' client_secret: Secret version reference containing the client secret.
        """
        pulumi.set(__self__, "client_id", client_id)
        pulumi.set(__self__, "client_secret", client_secret)

    @property
    @pulumi.getter(name="clientId")
    def client_id(self) -> str:
        """
        The client identifier.
        """
        return pulumi.get(self, "client_id")

    @property
    @pulumi.getter(name="clientSecret")
    def client_secret(self) -> 'outputs.SecretResponse':
        """
        Secret version reference containing the client secret.
        """
        return pulumi.get(self, "client_secret")


@pulumi.output_type
class Oauth2JwtBearerResponse(dict):
    """
    Parameters to support JSON Web Token (JWT) Profile for Oauth 2.0 Authorization Grant based authentication. See https://tools.ietf.org/html/rfc7523 for more details.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "clientKey":
            suggest = "client_key"
        elif key == "jwtClaims":
            suggest = "jwt_claims"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in Oauth2JwtBearerResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        Oauth2JwtBearerResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        Oauth2JwtBearerResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 client_key: 'outputs.SecretResponse',
                 jwt_claims: 'outputs.JwtClaimsResponse'):
        """
        Parameters to support JSON Web Token (JWT) Profile for Oauth 2.0 Authorization Grant based authentication. See https://tools.ietf.org/html/rfc7523 for more details.
        :param 'SecretResponse' client_key: Secret version reference containing a PKCS#8 PEM-encoded private key associated with the Client Certificate. This private key will be used to sign JWTs used for the jwt-bearer authorization grant. Specified in the form as: `projects/*/secrets/*/versions/*`.
        :param 'JwtClaimsResponse' jwt_claims: JwtClaims providers fields to generate the token.
        """
        pulumi.set(__self__, "client_key", client_key)
        pulumi.set(__self__, "jwt_claims", jwt_claims)

    @property
    @pulumi.getter(name="clientKey")
    def client_key(self) -> 'outputs.SecretResponse':
        """
        Secret version reference containing a PKCS#8 PEM-encoded private key associated with the Client Certificate. This private key will be used to sign JWTs used for the jwt-bearer authorization grant. Specified in the form as: `projects/*/secrets/*/versions/*`.
        """
        return pulumi.get(self, "client_key")

    @property
    @pulumi.getter(name="jwtClaims")
    def jwt_claims(self) -> 'outputs.JwtClaimsResponse':
        """
        JwtClaims providers fields to generate the token.
        """
        return pulumi.get(self, "jwt_claims")


@pulumi.output_type
class SecretResponse(dict):
    """
    Secret provides a reference to entries in Secret Manager.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "secretVersion":
            suggest = "secret_version"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in SecretResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        SecretResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        SecretResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 secret_version: str):
        """
        Secret provides a reference to entries in Secret Manager.
        :param str secret_version: The resource name of the secret version in the format, format as: `projects/*/secrets/*/versions/*`.
        """
        pulumi.set(__self__, "secret_version", secret_version)

    @property
    @pulumi.getter(name="secretVersion")
    def secret_version(self) -> str:
        """
        The resource name of the secret version in the format, format as: `projects/*/secrets/*/versions/*`.
        """
        return pulumi.get(self, "secret_version")


@pulumi.output_type
class SshPublicKeyResponse(dict):
    """
    Parameters to support Ssh public key Authentication.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "certType":
            suggest = "cert_type"
        elif key == "sshClientCert":
            suggest = "ssh_client_cert"
        elif key == "sshClientCertPass":
            suggest = "ssh_client_cert_pass"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in SshPublicKeyResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        SshPublicKeyResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        SshPublicKeyResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 cert_type: str,
                 password: 'outputs.SecretResponse',
                 ssh_client_cert: 'outputs.SecretResponse',
                 ssh_client_cert_pass: 'outputs.SecretResponse',
                 username: str):
        """
        Parameters to support Ssh public key Authentication.
        :param str cert_type: Format of SSH Client cert.
        :param 'SecretResponse' password: This is an optional field used in case client has enabled multi-factor authentication
        :param 'SecretResponse' ssh_client_cert: SSH Client Cert. It should contain both public and private key.
        :param 'SecretResponse' ssh_client_cert_pass: Password (passphrase) for ssh client certificate if it has one.
        :param str username: The user account used to authenticate.
        """
        pulumi.set(__self__, "cert_type", cert_type)
        pulumi.set(__self__, "password", password)
        pulumi.set(__self__, "ssh_client_cert", ssh_client_cert)
        pulumi.set(__self__, "ssh_client_cert_pass", ssh_client_cert_pass)
        pulumi.set(__self__, "username", username)

    @property
    @pulumi.getter(name="certType")
    def cert_type(self) -> str:
        """
        Format of SSH Client cert.
        """
        return pulumi.get(self, "cert_type")

    @property
    @pulumi.getter
    def password(self) -> 'outputs.SecretResponse':
        """
        This is an optional field used in case client has enabled multi-factor authentication
        """
        return pulumi.get(self, "password")

    @property
    @pulumi.getter(name="sshClientCert")
    def ssh_client_cert(self) -> 'outputs.SecretResponse':
        """
        SSH Client Cert. It should contain both public and private key.
        """
        return pulumi.get(self, "ssh_client_cert")

    @property
    @pulumi.getter(name="sshClientCertPass")
    def ssh_client_cert_pass(self) -> 'outputs.SecretResponse':
        """
        Password (passphrase) for ssh client certificate if it has one.
        """
        return pulumi.get(self, "ssh_client_cert_pass")

    @property
    @pulumi.getter
    def username(self) -> str:
        """
        The user account used to authenticate.
        """
        return pulumi.get(self, "username")


@pulumi.output_type
class UserPasswordResponse(dict):
    """
    Parameters to support Username and Password Authentication.
    """
    def __init__(__self__, *,
                 password: 'outputs.SecretResponse',
                 username: str):
        """
        Parameters to support Username and Password Authentication.
        :param 'SecretResponse' password: Secret version reference containing the password.
        :param str username: Username.
        """
        pulumi.set(__self__, "password", password)
        pulumi.set(__self__, "username", username)

    @property
    @pulumi.getter
    def password(self) -> 'outputs.SecretResponse':
        """
        Secret version reference containing the password.
        """
        return pulumi.get(self, "password")

    @property
    @pulumi.getter
    def username(self) -> str:
        """
        Username.
        """
        return pulumi.get(self, "username")


