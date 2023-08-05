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
    'GetRegistrationResult',
    'AwaitableGetRegistrationResult',
    'get_registration',
    'get_registration_output',
]

@pulumi.output_type
class GetRegistrationResult:
    def __init__(__self__, contact_settings=None, create_time=None, dns_settings=None, domain_name=None, expire_time=None, issues=None, labels=None, management_settings=None, name=None, pending_contact_settings=None, register_failure_reason=None, state=None, supported_privacy=None, transfer_failure_reason=None):
        if contact_settings and not isinstance(contact_settings, dict):
            raise TypeError("Expected argument 'contact_settings' to be a dict")
        pulumi.set(__self__, "contact_settings", contact_settings)
        if create_time and not isinstance(create_time, str):
            raise TypeError("Expected argument 'create_time' to be a str")
        pulumi.set(__self__, "create_time", create_time)
        if dns_settings and not isinstance(dns_settings, dict):
            raise TypeError("Expected argument 'dns_settings' to be a dict")
        pulumi.set(__self__, "dns_settings", dns_settings)
        if domain_name and not isinstance(domain_name, str):
            raise TypeError("Expected argument 'domain_name' to be a str")
        pulumi.set(__self__, "domain_name", domain_name)
        if expire_time and not isinstance(expire_time, str):
            raise TypeError("Expected argument 'expire_time' to be a str")
        pulumi.set(__self__, "expire_time", expire_time)
        if issues and not isinstance(issues, list):
            raise TypeError("Expected argument 'issues' to be a list")
        pulumi.set(__self__, "issues", issues)
        if labels and not isinstance(labels, dict):
            raise TypeError("Expected argument 'labels' to be a dict")
        pulumi.set(__self__, "labels", labels)
        if management_settings and not isinstance(management_settings, dict):
            raise TypeError("Expected argument 'management_settings' to be a dict")
        pulumi.set(__self__, "management_settings", management_settings)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if pending_contact_settings and not isinstance(pending_contact_settings, dict):
            raise TypeError("Expected argument 'pending_contact_settings' to be a dict")
        pulumi.set(__self__, "pending_contact_settings", pending_contact_settings)
        if register_failure_reason and not isinstance(register_failure_reason, str):
            raise TypeError("Expected argument 'register_failure_reason' to be a str")
        pulumi.set(__self__, "register_failure_reason", register_failure_reason)
        if state and not isinstance(state, str):
            raise TypeError("Expected argument 'state' to be a str")
        pulumi.set(__self__, "state", state)
        if supported_privacy and not isinstance(supported_privacy, list):
            raise TypeError("Expected argument 'supported_privacy' to be a list")
        pulumi.set(__self__, "supported_privacy", supported_privacy)
        if transfer_failure_reason and not isinstance(transfer_failure_reason, str):
            raise TypeError("Expected argument 'transfer_failure_reason' to be a str")
        pulumi.set(__self__, "transfer_failure_reason", transfer_failure_reason)

    @property
    @pulumi.getter(name="contactSettings")
    def contact_settings(self) -> 'outputs.ContactSettingsResponse':
        """
        Settings for contact information linked to the `Registration`. You cannot update these with the `UpdateRegistration` method. To update these settings, use the `ConfigureContactSettings` method.
        """
        return pulumi.get(self, "contact_settings")

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> str:
        """
        The creation timestamp of the `Registration` resource.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter(name="dnsSettings")
    def dns_settings(self) -> 'outputs.DnsSettingsResponse':
        """
        Settings controlling the DNS configuration of the `Registration`. You cannot update these with the `UpdateRegistration` method. To update these settings, use the `ConfigureDnsSettings` method.
        """
        return pulumi.get(self, "dns_settings")

    @property
    @pulumi.getter(name="domainName")
    def domain_name(self) -> str:
        """
        Immutable. The domain name. Unicode domain names must be expressed in Punycode format.
        """
        return pulumi.get(self, "domain_name")

    @property
    @pulumi.getter(name="expireTime")
    def expire_time(self) -> str:
        """
        The expiration timestamp of the `Registration`.
        """
        return pulumi.get(self, "expire_time")

    @property
    @pulumi.getter
    def issues(self) -> Sequence[str]:
        """
        The set of issues with the `Registration` that require attention.
        """
        return pulumi.get(self, "issues")

    @property
    @pulumi.getter
    def labels(self) -> Mapping[str, str]:
        """
        Set of labels associated with the `Registration`.
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter(name="managementSettings")
    def management_settings(self) -> 'outputs.ManagementSettingsResponse':
        """
        Settings for management of the `Registration`, including renewal, billing, and transfer. You cannot update these with the `UpdateRegistration` method. To update these settings, use the `ConfigureManagementSettings` method.
        """
        return pulumi.get(self, "management_settings")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the `Registration` resource, in the format `projects/*/locations/*/registrations/`.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="pendingContactSettings")
    def pending_contact_settings(self) -> 'outputs.ContactSettingsResponse':
        """
        Pending contact settings for the `Registration`. Updates to the `contact_settings` field that change its `registrant_contact` or `privacy` fields require email confirmation by the `registrant_contact` before taking effect. This field is set only if there are pending updates to the `contact_settings` that have not been confirmed. To confirm the changes, the `registrant_contact` must follow the instructions in the email they receive.
        """
        return pulumi.get(self, "pending_contact_settings")

    @property
    @pulumi.getter(name="registerFailureReason")
    def register_failure_reason(self) -> str:
        """
        The reason the domain registration failed. Only set for domains in REGISTRATION_FAILED state.
        """
        return pulumi.get(self, "register_failure_reason")

    @property
    @pulumi.getter
    def state(self) -> str:
        """
        The state of the `Registration`
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter(name="supportedPrivacy")
    def supported_privacy(self) -> Sequence[str]:
        """
        Set of options for the `contact_settings.privacy` field that this `Registration` supports.
        """
        return pulumi.get(self, "supported_privacy")

    @property
    @pulumi.getter(name="transferFailureReason")
    def transfer_failure_reason(self) -> str:
        """
        The reason the domain transfer failed. Only set for domains in TRANSFER_FAILED state.
        """
        return pulumi.get(self, "transfer_failure_reason")


class AwaitableGetRegistrationResult(GetRegistrationResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetRegistrationResult(
            contact_settings=self.contact_settings,
            create_time=self.create_time,
            dns_settings=self.dns_settings,
            domain_name=self.domain_name,
            expire_time=self.expire_time,
            issues=self.issues,
            labels=self.labels,
            management_settings=self.management_settings,
            name=self.name,
            pending_contact_settings=self.pending_contact_settings,
            register_failure_reason=self.register_failure_reason,
            state=self.state,
            supported_privacy=self.supported_privacy,
            transfer_failure_reason=self.transfer_failure_reason)


def get_registration(location: Optional[str] = None,
                     project: Optional[str] = None,
                     registration_id: Optional[str] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetRegistrationResult:
    """
    Gets the details of a `Registration` resource.
    """
    __args__ = dict()
    __args__['location'] = location
    __args__['project'] = project
    __args__['registrationId'] = registration_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:domains/v1beta1:getRegistration', __args__, opts=opts, typ=GetRegistrationResult).value

    return AwaitableGetRegistrationResult(
        contact_settings=__ret__.contact_settings,
        create_time=__ret__.create_time,
        dns_settings=__ret__.dns_settings,
        domain_name=__ret__.domain_name,
        expire_time=__ret__.expire_time,
        issues=__ret__.issues,
        labels=__ret__.labels,
        management_settings=__ret__.management_settings,
        name=__ret__.name,
        pending_contact_settings=__ret__.pending_contact_settings,
        register_failure_reason=__ret__.register_failure_reason,
        state=__ret__.state,
        supported_privacy=__ret__.supported_privacy,
        transfer_failure_reason=__ret__.transfer_failure_reason)


@_utilities.lift_output_func(get_registration)
def get_registration_output(location: Optional[pulumi.Input[str]] = None,
                            project: Optional[pulumi.Input[Optional[str]]] = None,
                            registration_id: Optional[pulumi.Input[str]] = None,
                            opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetRegistrationResult]:
    """
    Gets the details of a `Registration` resource.
    """
    ...
