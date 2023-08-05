# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities

__all__ = [
    'CertificateRawDataArgs',
    'SslSettingsArgs',
]

@pulumi.input_type
class CertificateRawDataArgs:
    def __init__(__self__, *,
                 private_key: Optional[pulumi.Input[str]] = None,
                 public_certificate: Optional[pulumi.Input[str]] = None):
        """
        An SSL certificate obtained from a certificate authority.
        :param pulumi.Input[str] private_key: Unencrypted PEM encoded RSA private key. This field is set once on certificate creation and then encrypted. The key size must be 2048 bits or fewer. Must include the header and footer. Example: -----BEGIN RSA PRIVATE KEY----- -----END RSA PRIVATE KEY----- @InputOnly
        :param pulumi.Input[str] public_certificate: PEM encoded x.509 public key certificate. This field is set once on certificate creation. Must include the header and footer. Example: -----BEGIN CERTIFICATE----- -----END CERTIFICATE----- 
        """
        if private_key is not None:
            pulumi.set(__self__, "private_key", private_key)
        if public_certificate is not None:
            pulumi.set(__self__, "public_certificate", public_certificate)

    @property
    @pulumi.getter(name="privateKey")
    def private_key(self) -> Optional[pulumi.Input[str]]:
        """
        Unencrypted PEM encoded RSA private key. This field is set once on certificate creation and then encrypted. The key size must be 2048 bits or fewer. Must include the header and footer. Example: -----BEGIN RSA PRIVATE KEY----- -----END RSA PRIVATE KEY----- @InputOnly
        """
        return pulumi.get(self, "private_key")

    @private_key.setter
    def private_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "private_key", value)

    @property
    @pulumi.getter(name="publicCertificate")
    def public_certificate(self) -> Optional[pulumi.Input[str]]:
        """
        PEM encoded x.509 public key certificate. This field is set once on certificate creation. Must include the header and footer. Example: -----BEGIN CERTIFICATE----- -----END CERTIFICATE----- 
        """
        return pulumi.get(self, "public_certificate")

    @public_certificate.setter
    def public_certificate(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "public_certificate", value)


@pulumi.input_type
class SslSettingsArgs:
    def __init__(__self__, *,
                 certificate_id: Optional[pulumi.Input[str]] = None):
        """
        SSL configuration for a DomainMapping resource.
        :param pulumi.Input[str] certificate_id: ID of the AuthorizedCertificate resource configuring SSL for the application. Clearing this field will remove SSL support.By default, a managed certificate is automatically created for every domain mapping. To omit SSL support or to configure SSL manually, specify no_managed_certificate on a CREATE or UPDATE request. You must be authorized to administer the AuthorizedCertificate resource to manually map it to a DomainMapping resource. Example: 12345.
        """
        if certificate_id is not None:
            pulumi.set(__self__, "certificate_id", certificate_id)

    @property
    @pulumi.getter(name="certificateId")
    def certificate_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the AuthorizedCertificate resource configuring SSL for the application. Clearing this field will remove SSL support.By default, a managed certificate is automatically created for every domain mapping. To omit SSL support or to configure SSL manually, specify no_managed_certificate on a CREATE or UPDATE request. You must be authorized to administer the AuthorizedCertificate resource to manually map it to a DomainMapping resource. Example: 12345.
        """
        return pulumi.get(self, "certificate_id")

    @certificate_id.setter
    def certificate_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "certificate_id", value)


