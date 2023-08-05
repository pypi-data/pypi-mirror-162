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
    'GetCustomerRepricingConfigResult',
    'AwaitableGetCustomerRepricingConfigResult',
    'get_customer_repricing_config',
    'get_customer_repricing_config_output',
]

@pulumi.output_type
class GetCustomerRepricingConfigResult:
    def __init__(__self__, name=None, repricing_config=None, update_time=None):
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if repricing_config and not isinstance(repricing_config, dict):
            raise TypeError("Expected argument 'repricing_config' to be a dict")
        pulumi.set(__self__, "repricing_config", repricing_config)
        if update_time and not isinstance(update_time, str):
            raise TypeError("Expected argument 'update_time' to be a str")
        pulumi.set(__self__, "update_time", update_time)

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Resource name of the CustomerRepricingConfig. Format: accounts/{account_id}/customers/{customer_id}/customerRepricingConfigs/{id}.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="repricingConfig")
    def repricing_config(self) -> 'outputs.GoogleCloudChannelV1RepricingConfigResponse':
        """
        The configuration for bill modifications made by a reseller before sending it to customers.
        """
        return pulumi.get(self, "repricing_config")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> str:
        """
        Timestamp of an update to the repricing rule. If `update_time` is after RepricingConfig.effective_invoice_month then it indicates this was set mid-month.
        """
        return pulumi.get(self, "update_time")


class AwaitableGetCustomerRepricingConfigResult(GetCustomerRepricingConfigResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetCustomerRepricingConfigResult(
            name=self.name,
            repricing_config=self.repricing_config,
            update_time=self.update_time)


def get_customer_repricing_config(account_id: Optional[str] = None,
                                  customer_id: Optional[str] = None,
                                  customer_repricing_config_id: Optional[str] = None,
                                  opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetCustomerRepricingConfigResult:
    """
    Gets information about how a Reseller modifies their bill before sending it to a Customer. Possible Error Codes: * PERMISSION_DENIED: If the account making the request and the account being queried are different. * NOT_FOUND: The CustomerRepricingConfig was not found. * INTERNAL: Any non-user error related to technical issues in the backend. In this case, contact Cloud Channel support. Return Value: If successful, the CustomerRepricingConfig resource, otherwise returns an error.
    """
    __args__ = dict()
    __args__['accountId'] = account_id
    __args__['customerId'] = customer_id
    __args__['customerRepricingConfigId'] = customer_repricing_config_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:cloudchannel/v1:getCustomerRepricingConfig', __args__, opts=opts, typ=GetCustomerRepricingConfigResult).value

    return AwaitableGetCustomerRepricingConfigResult(
        name=__ret__.name,
        repricing_config=__ret__.repricing_config,
        update_time=__ret__.update_time)


@_utilities.lift_output_func(get_customer_repricing_config)
def get_customer_repricing_config_output(account_id: Optional[pulumi.Input[str]] = None,
                                         customer_id: Optional[pulumi.Input[str]] = None,
                                         customer_repricing_config_id: Optional[pulumi.Input[str]] = None,
                                         opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetCustomerRepricingConfigResult]:
    """
    Gets information about how a Reseller modifies their bill before sending it to a Customer. Possible Error Codes: * PERMISSION_DENIED: If the account making the request and the account being queried are different. * NOT_FOUND: The CustomerRepricingConfig was not found. * INTERNAL: Any non-user error related to technical issues in the backend. In this case, contact Cloud Channel support. Return Value: If successful, the CustomerRepricingConfig resource, otherwise returns an error.
    """
    ...
