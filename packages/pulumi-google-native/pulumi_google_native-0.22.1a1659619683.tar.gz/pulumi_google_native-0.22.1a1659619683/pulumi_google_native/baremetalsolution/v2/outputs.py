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
    'GoogleCloudBaremetalsolutionV2LogicalInterfaceResponse',
    'InstanceConfigResponse',
    'IntakeVlanAttachmentResponse',
    'LogicalNetworkInterfaceResponse',
    'LunRangeResponse',
    'NetworkAddressResponse',
    'NetworkConfigResponse',
    'NfsExportResponse',
    'VolumeConfigResponse',
]

@pulumi.output_type
class GoogleCloudBaremetalsolutionV2LogicalInterfaceResponse(dict):
    """
    Each logical interface represents a logical abstraction of the underlying physical interface (for eg. bond, nic) of the instance. Each logical interface can effectively map to multiple network-IP pairs and still be mapped to one underlying physical interface.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "interfaceIndex":
            suggest = "interface_index"
        elif key == "logicalNetworkInterfaces":
            suggest = "logical_network_interfaces"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in GoogleCloudBaremetalsolutionV2LogicalInterfaceResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        GoogleCloudBaremetalsolutionV2LogicalInterfaceResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        GoogleCloudBaremetalsolutionV2LogicalInterfaceResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 interface_index: int,
                 logical_network_interfaces: Sequence['outputs.LogicalNetworkInterfaceResponse'],
                 name: str):
        """
        Each logical interface represents a logical abstraction of the underlying physical interface (for eg. bond, nic) of the instance. Each logical interface can effectively map to multiple network-IP pairs and still be mapped to one underlying physical interface.
        :param int interface_index: The index of the logical interface mapping to the index of the hardware bond or nic on the chosen network template. This field is deprecated.
        :param Sequence['LogicalNetworkInterfaceResponse'] logical_network_interfaces: List of logical network interfaces within a logical interface.
        :param str name: Interface name. This is of syntax or and forms part of the network template name.
        """
        pulumi.set(__self__, "interface_index", interface_index)
        pulumi.set(__self__, "logical_network_interfaces", logical_network_interfaces)
        pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter(name="interfaceIndex")
    def interface_index(self) -> int:
        """
        The index of the logical interface mapping to the index of the hardware bond or nic on the chosen network template. This field is deprecated.
        """
        return pulumi.get(self, "interface_index")

    @property
    @pulumi.getter(name="logicalNetworkInterfaces")
    def logical_network_interfaces(self) -> Sequence['outputs.LogicalNetworkInterfaceResponse']:
        """
        List of logical network interfaces within a logical interface.
        """
        return pulumi.get(self, "logical_network_interfaces")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Interface name. This is of syntax or and forms part of the network template name.
        """
        return pulumi.get(self, "name")


@pulumi.output_type
class InstanceConfigResponse(dict):
    """
    Configuration parameters for a new instance.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "accountNetworksEnabled":
            suggest = "account_networks_enabled"
        elif key == "clientNetwork":
            suggest = "client_network"
        elif key == "instanceType":
            suggest = "instance_type"
        elif key == "logicalInterfaces":
            suggest = "logical_interfaces"
        elif key == "networkConfig":
            suggest = "network_config"
        elif key == "networkTemplate":
            suggest = "network_template"
        elif key == "osImage":
            suggest = "os_image"
        elif key == "privateNetwork":
            suggest = "private_network"
        elif key == "userNote":
            suggest = "user_note"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in InstanceConfigResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        InstanceConfigResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        InstanceConfigResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 account_networks_enabled: bool,
                 client_network: 'outputs.NetworkAddressResponse',
                 hyperthreading: bool,
                 instance_type: str,
                 logical_interfaces: Sequence['outputs.GoogleCloudBaremetalsolutionV2LogicalInterfaceResponse'],
                 name: str,
                 network_config: str,
                 network_template: str,
                 os_image: str,
                 private_network: 'outputs.NetworkAddressResponse',
                 user_note: str):
        """
        Configuration parameters for a new instance.
        :param bool account_networks_enabled: If true networks can be from different projects of the same vendor account.
        :param 'NetworkAddressResponse' client_network: Client network address. Filled if InstanceConfig.multivlan_config is false.
        :param bool hyperthreading: Whether the instance should be provisioned with Hyperthreading enabled.
        :param str instance_type: Instance type. [Available types](https://cloud.google.com/bare-metal/docs/bms-planning#server_configurations)
        :param Sequence['GoogleCloudBaremetalsolutionV2LogicalInterfaceResponse'] logical_interfaces: List of logical interfaces for the instance. The number of logical interfaces will be the same as number of hardware bond/nic on the chosen network template. Filled if InstanceConfig.multivlan_config is true.
        :param str name: The name of the instance config.
        :param str network_config: The type of network configuration on the instance.
        :param str network_template: Server network template name. Filled if InstanceConfig.multivlan_config is true.
        :param str os_image: OS image to initialize the instance. [Available images](https://cloud.google.com/bare-metal/docs/bms-planning#server_configurations)
        :param 'NetworkAddressResponse' private_network: Private network address, if any. Filled if InstanceConfig.multivlan_config is false.
        :param str user_note: User note field, it can be used by customers to add additional information for the BMS Ops team .
        """
        pulumi.set(__self__, "account_networks_enabled", account_networks_enabled)
        pulumi.set(__self__, "client_network", client_network)
        pulumi.set(__self__, "hyperthreading", hyperthreading)
        pulumi.set(__self__, "instance_type", instance_type)
        pulumi.set(__self__, "logical_interfaces", logical_interfaces)
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "network_config", network_config)
        pulumi.set(__self__, "network_template", network_template)
        pulumi.set(__self__, "os_image", os_image)
        pulumi.set(__self__, "private_network", private_network)
        pulumi.set(__self__, "user_note", user_note)

    @property
    @pulumi.getter(name="accountNetworksEnabled")
    def account_networks_enabled(self) -> bool:
        """
        If true networks can be from different projects of the same vendor account.
        """
        return pulumi.get(self, "account_networks_enabled")

    @property
    @pulumi.getter(name="clientNetwork")
    def client_network(self) -> 'outputs.NetworkAddressResponse':
        """
        Client network address. Filled if InstanceConfig.multivlan_config is false.
        """
        return pulumi.get(self, "client_network")

    @property
    @pulumi.getter
    def hyperthreading(self) -> bool:
        """
        Whether the instance should be provisioned with Hyperthreading enabled.
        """
        return pulumi.get(self, "hyperthreading")

    @property
    @pulumi.getter(name="instanceType")
    def instance_type(self) -> str:
        """
        Instance type. [Available types](https://cloud.google.com/bare-metal/docs/bms-planning#server_configurations)
        """
        return pulumi.get(self, "instance_type")

    @property
    @pulumi.getter(name="logicalInterfaces")
    def logical_interfaces(self) -> Sequence['outputs.GoogleCloudBaremetalsolutionV2LogicalInterfaceResponse']:
        """
        List of logical interfaces for the instance. The number of logical interfaces will be the same as number of hardware bond/nic on the chosen network template. Filled if InstanceConfig.multivlan_config is true.
        """
        return pulumi.get(self, "logical_interfaces")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the instance config.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="networkConfig")
    def network_config(self) -> str:
        """
        The type of network configuration on the instance.
        """
        return pulumi.get(self, "network_config")

    @property
    @pulumi.getter(name="networkTemplate")
    def network_template(self) -> str:
        """
        Server network template name. Filled if InstanceConfig.multivlan_config is true.
        """
        return pulumi.get(self, "network_template")

    @property
    @pulumi.getter(name="osImage")
    def os_image(self) -> str:
        """
        OS image to initialize the instance. [Available images](https://cloud.google.com/bare-metal/docs/bms-planning#server_configurations)
        """
        return pulumi.get(self, "os_image")

    @property
    @pulumi.getter(name="privateNetwork")
    def private_network(self) -> 'outputs.NetworkAddressResponse':
        """
        Private network address, if any. Filled if InstanceConfig.multivlan_config is false.
        """
        return pulumi.get(self, "private_network")

    @property
    @pulumi.getter(name="userNote")
    def user_note(self) -> str:
        """
        User note field, it can be used by customers to add additional information for the BMS Ops team .
        """
        return pulumi.get(self, "user_note")


@pulumi.output_type
class IntakeVlanAttachmentResponse(dict):
    """
    A GCP vlan attachment.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "pairingKey":
            suggest = "pairing_key"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in IntakeVlanAttachmentResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        IntakeVlanAttachmentResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        IntakeVlanAttachmentResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 pairing_key: str):
        """
        A GCP vlan attachment.
        :param str pairing_key: Attachment pairing key.
        """
        pulumi.set(__self__, "pairing_key", pairing_key)

    @property
    @pulumi.getter(name="pairingKey")
    def pairing_key(self) -> str:
        """
        Attachment pairing key.
        """
        return pulumi.get(self, "pairing_key")


@pulumi.output_type
class LogicalNetworkInterfaceResponse(dict):
    """
    Each logical network interface is effectively a network and IP pair.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "defaultGateway":
            suggest = "default_gateway"
        elif key == "ipAddress":
            suggest = "ip_address"
        elif key == "networkType":
            suggest = "network_type"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in LogicalNetworkInterfaceResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        LogicalNetworkInterfaceResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        LogicalNetworkInterfaceResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 default_gateway: bool,
                 ip_address: str,
                 network: str,
                 network_type: str):
        """
        Each logical network interface is effectively a network and IP pair.
        :param bool default_gateway: Whether this interface is the default gateway for the instance. Only one interface can be the default gateway for the instance.
        :param str ip_address: IP address in the network
        :param str network: Name of the network
        :param str network_type: Type of network.
        """
        pulumi.set(__self__, "default_gateway", default_gateway)
        pulumi.set(__self__, "ip_address", ip_address)
        pulumi.set(__self__, "network", network)
        pulumi.set(__self__, "network_type", network_type)

    @property
    @pulumi.getter(name="defaultGateway")
    def default_gateway(self) -> bool:
        """
        Whether this interface is the default gateway for the instance. Only one interface can be the default gateway for the instance.
        """
        return pulumi.get(self, "default_gateway")

    @property
    @pulumi.getter(name="ipAddress")
    def ip_address(self) -> str:
        """
        IP address in the network
        """
        return pulumi.get(self, "ip_address")

    @property
    @pulumi.getter
    def network(self) -> str:
        """
        Name of the network
        """
        return pulumi.get(self, "network")

    @property
    @pulumi.getter(name="networkType")
    def network_type(self) -> str:
        """
        Type of network.
        """
        return pulumi.get(self, "network_type")


@pulumi.output_type
class LunRangeResponse(dict):
    """
    A LUN(Logical Unit Number) range.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "sizeGb":
            suggest = "size_gb"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in LunRangeResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        LunRangeResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        LunRangeResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 quantity: int,
                 size_gb: int):
        """
        A LUN(Logical Unit Number) range.
        :param int quantity: Number of LUNs to create.
        :param int size_gb: The requested size of each LUN, in GB.
        """
        pulumi.set(__self__, "quantity", quantity)
        pulumi.set(__self__, "size_gb", size_gb)

    @property
    @pulumi.getter
    def quantity(self) -> int:
        """
        Number of LUNs to create.
        """
        return pulumi.get(self, "quantity")

    @property
    @pulumi.getter(name="sizeGb")
    def size_gb(self) -> int:
        """
        The requested size of each LUN, in GB.
        """
        return pulumi.get(self, "size_gb")


@pulumi.output_type
class NetworkAddressResponse(dict):
    """
    A network.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "existingNetworkId":
            suggest = "existing_network_id"
        elif key == "networkId":
            suggest = "network_id"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in NetworkAddressResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        NetworkAddressResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        NetworkAddressResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 address: str,
                 existing_network_id: str,
                 network_id: str):
        """
        A network.
        :param str address: IPv4 address to be assigned to the server.
        :param str existing_network_id: Name of the existing network to use.
        :param str network_id: Id of the network to use, within the same ProvisioningConfig request.
        """
        pulumi.set(__self__, "address", address)
        pulumi.set(__self__, "existing_network_id", existing_network_id)
        pulumi.set(__self__, "network_id", network_id)

    @property
    @pulumi.getter
    def address(self) -> str:
        """
        IPv4 address to be assigned to the server.
        """
        return pulumi.get(self, "address")

    @property
    @pulumi.getter(name="existingNetworkId")
    def existing_network_id(self) -> str:
        """
        Name of the existing network to use.
        """
        return pulumi.get(self, "existing_network_id")

    @property
    @pulumi.getter(name="networkId")
    def network_id(self) -> str:
        """
        Id of the network to use, within the same ProvisioningConfig request.
        """
        return pulumi.get(self, "network_id")


@pulumi.output_type
class NetworkConfigResponse(dict):
    """
    Configuration parameters for a new network.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "gcpService":
            suggest = "gcp_service"
        elif key == "jumboFramesEnabled":
            suggest = "jumbo_frames_enabled"
        elif key == "serviceCidr":
            suggest = "service_cidr"
        elif key == "userNote":
            suggest = "user_note"
        elif key == "vlanAttachments":
            suggest = "vlan_attachments"
        elif key == "vlanSameProject":
            suggest = "vlan_same_project"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in NetworkConfigResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        NetworkConfigResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        NetworkConfigResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 bandwidth: str,
                 cidr: str,
                 gcp_service: str,
                 jumbo_frames_enabled: bool,
                 name: str,
                 service_cidr: str,
                 type: str,
                 user_note: str,
                 vlan_attachments: Sequence['outputs.IntakeVlanAttachmentResponse'],
                 vlan_same_project: bool):
        """
        Configuration parameters for a new network.
        :param str bandwidth: Interconnect bandwidth. Set only when type is CLIENT.
        :param str cidr: CIDR range of the network.
        :param str gcp_service: The GCP service of the network. Available gcp_service are in https://cloud.google.com/bare-metal/docs/bms-planning.
        :param bool jumbo_frames_enabled: The JumboFramesEnabled option for customer to set.
        :param str name: The name of the network config.
        :param str service_cidr: Service CIDR, if any.
        :param str type: The type of this network, either Client or Private.
        :param str user_note: User note field, it can be used by customers to add additional information for the BMS Ops team .
        :param Sequence['IntakeVlanAttachmentResponse'] vlan_attachments: List of VLAN attachments. As of now there are always 2 attachments, but it is going to change in the future (multi vlan).
        :param bool vlan_same_project: Whether the VLAN attachment pair is located in the same project.
        """
        pulumi.set(__self__, "bandwidth", bandwidth)
        pulumi.set(__self__, "cidr", cidr)
        pulumi.set(__self__, "gcp_service", gcp_service)
        pulumi.set(__self__, "jumbo_frames_enabled", jumbo_frames_enabled)
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "service_cidr", service_cidr)
        pulumi.set(__self__, "type", type)
        pulumi.set(__self__, "user_note", user_note)
        pulumi.set(__self__, "vlan_attachments", vlan_attachments)
        pulumi.set(__self__, "vlan_same_project", vlan_same_project)

    @property
    @pulumi.getter
    def bandwidth(self) -> str:
        """
        Interconnect bandwidth. Set only when type is CLIENT.
        """
        return pulumi.get(self, "bandwidth")

    @property
    @pulumi.getter
    def cidr(self) -> str:
        """
        CIDR range of the network.
        """
        return pulumi.get(self, "cidr")

    @property
    @pulumi.getter(name="gcpService")
    def gcp_service(self) -> str:
        """
        The GCP service of the network. Available gcp_service are in https://cloud.google.com/bare-metal/docs/bms-planning.
        """
        return pulumi.get(self, "gcp_service")

    @property
    @pulumi.getter(name="jumboFramesEnabled")
    def jumbo_frames_enabled(self) -> bool:
        """
        The JumboFramesEnabled option for customer to set.
        """
        return pulumi.get(self, "jumbo_frames_enabled")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the network config.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="serviceCidr")
    def service_cidr(self) -> str:
        """
        Service CIDR, if any.
        """
        return pulumi.get(self, "service_cidr")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        The type of this network, either Client or Private.
        """
        return pulumi.get(self, "type")

    @property
    @pulumi.getter(name="userNote")
    def user_note(self) -> str:
        """
        User note field, it can be used by customers to add additional information for the BMS Ops team .
        """
        return pulumi.get(self, "user_note")

    @property
    @pulumi.getter(name="vlanAttachments")
    def vlan_attachments(self) -> Sequence['outputs.IntakeVlanAttachmentResponse']:
        """
        List of VLAN attachments. As of now there are always 2 attachments, but it is going to change in the future (multi vlan).
        """
        return pulumi.get(self, "vlan_attachments")

    @property
    @pulumi.getter(name="vlanSameProject")
    def vlan_same_project(self) -> bool:
        """
        Whether the VLAN attachment pair is located in the same project.
        """
        return pulumi.get(self, "vlan_same_project")


@pulumi.output_type
class NfsExportResponse(dict):
    """
    A NFS export entry.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "allowDev":
            suggest = "allow_dev"
        elif key == "allowSuid":
            suggest = "allow_suid"
        elif key == "machineId":
            suggest = "machine_id"
        elif key == "networkId":
            suggest = "network_id"
        elif key == "noRootSquash":
            suggest = "no_root_squash"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in NfsExportResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        NfsExportResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        NfsExportResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 allow_dev: bool,
                 allow_suid: bool,
                 cidr: str,
                 machine_id: str,
                 network_id: str,
                 no_root_squash: bool,
                 permissions: str):
        """
        A NFS export entry.
        :param bool allow_dev: Allow dev flag in NfsShare AllowedClientsRequest.
        :param bool allow_suid: Allow the setuid flag.
        :param str cidr: A CIDR range.
        :param str machine_id: Either a single machine, identified by an ID, or a comma-separated list of machine IDs.
        :param str network_id: Network to use to publish the export.
        :param bool no_root_squash: Disable root squashing, which is a feature of NFS. Root squash is a special mapping of the remote superuser (root) identity when using identity authentication.
        :param str permissions: Export permissions.
        """
        pulumi.set(__self__, "allow_dev", allow_dev)
        pulumi.set(__self__, "allow_suid", allow_suid)
        pulumi.set(__self__, "cidr", cidr)
        pulumi.set(__self__, "machine_id", machine_id)
        pulumi.set(__self__, "network_id", network_id)
        pulumi.set(__self__, "no_root_squash", no_root_squash)
        pulumi.set(__self__, "permissions", permissions)

    @property
    @pulumi.getter(name="allowDev")
    def allow_dev(self) -> bool:
        """
        Allow dev flag in NfsShare AllowedClientsRequest.
        """
        return pulumi.get(self, "allow_dev")

    @property
    @pulumi.getter(name="allowSuid")
    def allow_suid(self) -> bool:
        """
        Allow the setuid flag.
        """
        return pulumi.get(self, "allow_suid")

    @property
    @pulumi.getter
    def cidr(self) -> str:
        """
        A CIDR range.
        """
        return pulumi.get(self, "cidr")

    @property
    @pulumi.getter(name="machineId")
    def machine_id(self) -> str:
        """
        Either a single machine, identified by an ID, or a comma-separated list of machine IDs.
        """
        return pulumi.get(self, "machine_id")

    @property
    @pulumi.getter(name="networkId")
    def network_id(self) -> str:
        """
        Network to use to publish the export.
        """
        return pulumi.get(self, "network_id")

    @property
    @pulumi.getter(name="noRootSquash")
    def no_root_squash(self) -> bool:
        """
        Disable root squashing, which is a feature of NFS. Root squash is a special mapping of the remote superuser (root) identity when using identity authentication.
        """
        return pulumi.get(self, "no_root_squash")

    @property
    @pulumi.getter
    def permissions(self) -> str:
        """
        Export permissions.
        """
        return pulumi.get(self, "permissions")


@pulumi.output_type
class VolumeConfigResponse(dict):
    """
    Configuration parameters for a new volume.
    """
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "gcpService":
            suggest = "gcp_service"
        elif key == "lunRanges":
            suggest = "lun_ranges"
        elif key == "machineIds":
            suggest = "machine_ids"
        elif key == "nfsExports":
            suggest = "nfs_exports"
        elif key == "sizeGb":
            suggest = "size_gb"
        elif key == "snapshotsEnabled":
            suggest = "snapshots_enabled"
        elif key == "userNote":
            suggest = "user_note"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in VolumeConfigResponse. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        VolumeConfigResponse.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        VolumeConfigResponse.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 gcp_service: str,
                 lun_ranges: Sequence['outputs.LunRangeResponse'],
                 machine_ids: Sequence[str],
                 name: str,
                 nfs_exports: Sequence['outputs.NfsExportResponse'],
                 protocol: str,
                 size_gb: int,
                 snapshots_enabled: bool,
                 type: str,
                 user_note: str):
        """
        Configuration parameters for a new volume.
        :param str gcp_service: The GCP service of the storage volume. Available gcp_service are in https://cloud.google.com/bare-metal/docs/bms-planning.
        :param Sequence['LunRangeResponse'] lun_ranges: LUN ranges to be configured. Set only when protocol is PROTOCOL_FC.
        :param Sequence[str] machine_ids: Machine ids connected to this volume. Set only when protocol is PROTOCOL_FC.
        :param str name: The name of the volume config.
        :param Sequence['NfsExportResponse'] nfs_exports: NFS exports. Set only when protocol is PROTOCOL_NFS.
        :param str protocol: Volume protocol.
        :param int size_gb: The requested size of this volume, in GB.
        :param bool snapshots_enabled: Whether snapshots should be enabled.
        :param str type: The type of this Volume.
        :param str user_note: User note field, it can be used by customers to add additional information for the BMS Ops team .
        """
        pulumi.set(__self__, "gcp_service", gcp_service)
        pulumi.set(__self__, "lun_ranges", lun_ranges)
        pulumi.set(__self__, "machine_ids", machine_ids)
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "nfs_exports", nfs_exports)
        pulumi.set(__self__, "protocol", protocol)
        pulumi.set(__self__, "size_gb", size_gb)
        pulumi.set(__self__, "snapshots_enabled", snapshots_enabled)
        pulumi.set(__self__, "type", type)
        pulumi.set(__self__, "user_note", user_note)

    @property
    @pulumi.getter(name="gcpService")
    def gcp_service(self) -> str:
        """
        The GCP service of the storage volume. Available gcp_service are in https://cloud.google.com/bare-metal/docs/bms-planning.
        """
        return pulumi.get(self, "gcp_service")

    @property
    @pulumi.getter(name="lunRanges")
    def lun_ranges(self) -> Sequence['outputs.LunRangeResponse']:
        """
        LUN ranges to be configured. Set only when protocol is PROTOCOL_FC.
        """
        return pulumi.get(self, "lun_ranges")

    @property
    @pulumi.getter(name="machineIds")
    def machine_ids(self) -> Sequence[str]:
        """
        Machine ids connected to this volume. Set only when protocol is PROTOCOL_FC.
        """
        return pulumi.get(self, "machine_ids")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the volume config.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="nfsExports")
    def nfs_exports(self) -> Sequence['outputs.NfsExportResponse']:
        """
        NFS exports. Set only when protocol is PROTOCOL_NFS.
        """
        return pulumi.get(self, "nfs_exports")

    @property
    @pulumi.getter
    def protocol(self) -> str:
        """
        Volume protocol.
        """
        return pulumi.get(self, "protocol")

    @property
    @pulumi.getter(name="sizeGb")
    def size_gb(self) -> int:
        """
        The requested size of this volume, in GB.
        """
        return pulumi.get(self, "size_gb")

    @property
    @pulumi.getter(name="snapshotsEnabled")
    def snapshots_enabled(self) -> bool:
        """
        Whether snapshots should be enabled.
        """
        return pulumi.get(self, "snapshots_enabled")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        The type of this Volume.
        """
        return pulumi.get(self, "type")

    @property
    @pulumi.getter(name="userNote")
    def user_note(self) -> str:
        """
        User note field, it can be used by customers to add additional information for the BMS Ops team .
        """
        return pulumi.get(self, "user_note")


