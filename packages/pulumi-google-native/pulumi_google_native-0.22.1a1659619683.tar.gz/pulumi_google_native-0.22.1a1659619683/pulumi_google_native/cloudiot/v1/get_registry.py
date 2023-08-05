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
    'GetRegistryResult',
    'AwaitableGetRegistryResult',
    'get_registry',
    'get_registry_output',
]

@pulumi.output_type
class GetRegistryResult:
    def __init__(__self__, credentials=None, event_notification_configs=None, http_config=None, log_level=None, mqtt_config=None, name=None, state_notification_config=None):
        if credentials and not isinstance(credentials, list):
            raise TypeError("Expected argument 'credentials' to be a list")
        pulumi.set(__self__, "credentials", credentials)
        if event_notification_configs and not isinstance(event_notification_configs, list):
            raise TypeError("Expected argument 'event_notification_configs' to be a list")
        pulumi.set(__self__, "event_notification_configs", event_notification_configs)
        if http_config and not isinstance(http_config, dict):
            raise TypeError("Expected argument 'http_config' to be a dict")
        pulumi.set(__self__, "http_config", http_config)
        if log_level and not isinstance(log_level, str):
            raise TypeError("Expected argument 'log_level' to be a str")
        pulumi.set(__self__, "log_level", log_level)
        if mqtt_config and not isinstance(mqtt_config, dict):
            raise TypeError("Expected argument 'mqtt_config' to be a dict")
        pulumi.set(__self__, "mqtt_config", mqtt_config)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if state_notification_config and not isinstance(state_notification_config, dict):
            raise TypeError("Expected argument 'state_notification_config' to be a dict")
        pulumi.set(__self__, "state_notification_config", state_notification_config)

    @property
    @pulumi.getter
    def credentials(self) -> Sequence['outputs.RegistryCredentialResponse']:
        """
        The credentials used to verify the device credentials. No more than 10 credentials can be bound to a single registry at a time. The verification process occurs at the time of device creation or update. If this field is empty, no verification is performed. Otherwise, the credentials of a newly created device or added credentials of an updated device should be signed with one of these registry credentials. Note, however, that existing devices will never be affected by modifications to this list of credentials: after a device has been successfully created in a registry, it should be able to connect even if its registry credentials are revoked, deleted, or modified.
        """
        return pulumi.get(self, "credentials")

    @property
    @pulumi.getter(name="eventNotificationConfigs")
    def event_notification_configs(self) -> Sequence['outputs.EventNotificationConfigResponse']:
        """
        The configuration for notification of telemetry events received from the device. All telemetry events that were successfully published by the device and acknowledged by Cloud IoT Core are guaranteed to be delivered to Cloud Pub/Sub. If multiple configurations match a message, only the first matching configuration is used. If you try to publish a device telemetry event using MQTT without specifying a Cloud Pub/Sub topic for the device's registry, the connection closes automatically. If you try to do so using an HTTP connection, an error is returned. Up to 10 configurations may be provided.
        """
        return pulumi.get(self, "event_notification_configs")

    @property
    @pulumi.getter(name="httpConfig")
    def http_config(self) -> 'outputs.HttpConfigResponse':
        """
        The DeviceService (HTTP) configuration for this device registry.
        """
        return pulumi.get(self, "http_config")

    @property
    @pulumi.getter(name="logLevel")
    def log_level(self) -> str:
        """
        **Beta Feature** The default logging verbosity for activity from devices in this registry. The verbosity level can be overridden by Device.log_level.
        """
        return pulumi.get(self, "log_level")

    @property
    @pulumi.getter(name="mqttConfig")
    def mqtt_config(self) -> 'outputs.MqttConfigResponse':
        """
        The MQTT configuration for this device registry.
        """
        return pulumi.get(self, "mqtt_config")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The resource path name. For example, `projects/example-project/locations/us-central1/registries/my-registry`.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="stateNotificationConfig")
    def state_notification_config(self) -> 'outputs.StateNotificationConfigResponse':
        """
        The configuration for notification of new states received from the device. State updates are guaranteed to be stored in the state history, but notifications to Cloud Pub/Sub are not guaranteed. For example, if permissions are misconfigured or the specified topic doesn't exist, no notification will be published but the state will still be stored in Cloud IoT Core.
        """
        return pulumi.get(self, "state_notification_config")


class AwaitableGetRegistryResult(GetRegistryResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetRegistryResult(
            credentials=self.credentials,
            event_notification_configs=self.event_notification_configs,
            http_config=self.http_config,
            log_level=self.log_level,
            mqtt_config=self.mqtt_config,
            name=self.name,
            state_notification_config=self.state_notification_config)


def get_registry(location: Optional[str] = None,
                 project: Optional[str] = None,
                 registry_id: Optional[str] = None,
                 opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetRegistryResult:
    """
    Gets a device registry configuration.
    """
    __args__ = dict()
    __args__['location'] = location
    __args__['project'] = project
    __args__['registryId'] = registry_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:cloudiot/v1:getRegistry', __args__, opts=opts, typ=GetRegistryResult).value

    return AwaitableGetRegistryResult(
        credentials=__ret__.credentials,
        event_notification_configs=__ret__.event_notification_configs,
        http_config=__ret__.http_config,
        log_level=__ret__.log_level,
        mqtt_config=__ret__.mqtt_config,
        name=__ret__.name,
        state_notification_config=__ret__.state_notification_config)


@_utilities.lift_output_func(get_registry)
def get_registry_output(location: Optional[pulumi.Input[str]] = None,
                        project: Optional[pulumi.Input[Optional[str]]] = None,
                        registry_id: Optional[pulumi.Input[str]] = None,
                        opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetRegistryResult]:
    """
    Gets a device registry configuration.
    """
    ...
