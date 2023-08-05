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
    'GetUserResult',
    'AwaitableGetUserResult',
    'get_user',
    'get_user_output',
]

@pulumi.output_type
class GetUserResult:
    def __init__(__self__, dual_password_type=None, etag=None, host=None, instance=None, kind=None, name=None, password=None, password_policy=None, project=None, sqlserver_user_details=None, type=None):
        if dual_password_type and not isinstance(dual_password_type, str):
            raise TypeError("Expected argument 'dual_password_type' to be a str")
        pulumi.set(__self__, "dual_password_type", dual_password_type)
        if etag and not isinstance(etag, str):
            raise TypeError("Expected argument 'etag' to be a str")
        if etag is not None:
            warnings.warn("""This field is deprecated and will be removed from a future version of the API.""", DeprecationWarning)
            pulumi.log.warn("""etag is deprecated: This field is deprecated and will be removed from a future version of the API.""")

        pulumi.set(__self__, "etag", etag)
        if host and not isinstance(host, str):
            raise TypeError("Expected argument 'host' to be a str")
        pulumi.set(__self__, "host", host)
        if instance and not isinstance(instance, str):
            raise TypeError("Expected argument 'instance' to be a str")
        pulumi.set(__self__, "instance", instance)
        if kind and not isinstance(kind, str):
            raise TypeError("Expected argument 'kind' to be a str")
        pulumi.set(__self__, "kind", kind)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if password and not isinstance(password, str):
            raise TypeError("Expected argument 'password' to be a str")
        pulumi.set(__self__, "password", password)
        if password_policy and not isinstance(password_policy, dict):
            raise TypeError("Expected argument 'password_policy' to be a dict")
        pulumi.set(__self__, "password_policy", password_policy)
        if project and not isinstance(project, str):
            raise TypeError("Expected argument 'project' to be a str")
        pulumi.set(__self__, "project", project)
        if sqlserver_user_details and not isinstance(sqlserver_user_details, dict):
            raise TypeError("Expected argument 'sqlserver_user_details' to be a dict")
        pulumi.set(__self__, "sqlserver_user_details", sqlserver_user_details)
        if type and not isinstance(type, str):
            raise TypeError("Expected argument 'type' to be a str")
        pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="dualPasswordType")
    def dual_password_type(self) -> str:
        """
        Dual password status for the user.
        """
        return pulumi.get(self, "dual_password_type")

    @property
    @pulumi.getter
    def etag(self) -> str:
        """
        This field is deprecated and will be removed from a future version of the API.
        """
        return pulumi.get(self, "etag")

    @property
    @pulumi.getter
    def host(self) -> str:
        """
        Optional. The host from which the user can connect. For `insert` operations, host defaults to an empty string. For `update` operations, host is specified as part of the request URL. The host name cannot be updated after insertion. For a MySQL instance, it's required; for a PostgreSQL or SQL Server instance, it's optional.
        """
        return pulumi.get(self, "host")

    @property
    @pulumi.getter
    def instance(self) -> str:
        """
        The name of the Cloud SQL instance. This does not include the project ID. Can be omitted for `update` because it is already specified on the URL.
        """
        return pulumi.get(self, "instance")

    @property
    @pulumi.getter
    def kind(self) -> str:
        """
        This is always `sql#user`.
        """
        return pulumi.get(self, "kind")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the user in the Cloud SQL instance. Can be omitted for `update` because it is already specified in the URL.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def password(self) -> str:
        """
        The password for the user.
        """
        return pulumi.get(self, "password")

    @property
    @pulumi.getter(name="passwordPolicy")
    def password_policy(self) -> 'outputs.UserPasswordValidationPolicyResponse':
        """
        User level password validation policy.
        """
        return pulumi.get(self, "password_policy")

    @property
    @pulumi.getter
    def project(self) -> str:
        """
        The project ID of the project containing the Cloud SQL database. The Google apps domain is prefixed if applicable. Can be omitted for `update` because it is already specified on the URL.
        """
        return pulumi.get(self, "project")

    @property
    @pulumi.getter(name="sqlserverUserDetails")
    def sqlserver_user_details(self) -> 'outputs.SqlServerUserDetailsResponse':
        return pulumi.get(self, "sqlserver_user_details")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        The user type. It determines the method to authenticate the user during login. The default is the database's built-in user type.
        """
        return pulumi.get(self, "type")


class AwaitableGetUserResult(GetUserResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetUserResult(
            dual_password_type=self.dual_password_type,
            etag=self.etag,
            host=self.host,
            instance=self.instance,
            kind=self.kind,
            name=self.name,
            password=self.password,
            password_policy=self.password_policy,
            project=self.project,
            sqlserver_user_details=self.sqlserver_user_details,
            type=self.type)


def get_user(instance: Optional[str] = None,
             name: Optional[str] = None,
             project: Optional[str] = None,
             opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetUserResult:
    """
    Retrieves a resource containing information about a user.
    """
    __args__ = dict()
    __args__['instance'] = instance
    __args__['name'] = name
    __args__['project'] = project
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:sqladmin/v1:getUser', __args__, opts=opts, typ=GetUserResult).value

    return AwaitableGetUserResult(
        dual_password_type=__ret__.dual_password_type,
        etag=__ret__.etag,
        host=__ret__.host,
        instance=__ret__.instance,
        kind=__ret__.kind,
        name=__ret__.name,
        password=__ret__.password,
        password_policy=__ret__.password_policy,
        project=__ret__.project,
        sqlserver_user_details=__ret__.sqlserver_user_details,
        type=__ret__.type)


@_utilities.lift_output_func(get_user)
def get_user_output(instance: Optional[pulumi.Input[str]] = None,
                    name: Optional[pulumi.Input[str]] = None,
                    project: Optional[pulumi.Input[Optional[str]]] = None,
                    opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetUserResult]:
    """
    Retrieves a resource containing information about a user.
    """
    ...
