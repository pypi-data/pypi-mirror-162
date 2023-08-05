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
from ._inputs import *

__all__ = ['JobArgs', 'Job']

@pulumi.input_type
class JobArgs:
    def __init__(__self__, *,
                 configuration: Optional[pulumi.Input['JobConfigurationArgs']] = None,
                 job_reference: Optional[pulumi.Input['JobReferenceArgs']] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 source: Optional[pulumi.Input[Union[pulumi.Asset, pulumi.Archive]]] = None):
        """
        The set of arguments for constructing a Job resource.
        :param pulumi.Input['JobConfigurationArgs'] configuration: [Required] Describes the job configuration.
        :param pulumi.Input['JobReferenceArgs'] job_reference: [Optional] Reference describing the unique-per-user name of the job.
        """
        if configuration is not None:
            pulumi.set(__self__, "configuration", configuration)
        if job_reference is not None:
            pulumi.set(__self__, "job_reference", job_reference)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if source is not None:
            pulumi.set(__self__, "source", source)

    @property
    @pulumi.getter
    def configuration(self) -> Optional[pulumi.Input['JobConfigurationArgs']]:
        """
        [Required] Describes the job configuration.
        """
        return pulumi.get(self, "configuration")

    @configuration.setter
    def configuration(self, value: Optional[pulumi.Input['JobConfigurationArgs']]):
        pulumi.set(self, "configuration", value)

    @property
    @pulumi.getter(name="jobReference")
    def job_reference(self) -> Optional[pulumi.Input['JobReferenceArgs']]:
        """
        [Optional] Reference describing the unique-per-user name of the job.
        """
        return pulumi.get(self, "job_reference")

    @job_reference.setter
    def job_reference(self, value: Optional[pulumi.Input['JobReferenceArgs']]):
        pulumi.set(self, "job_reference", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)

    @property
    @pulumi.getter
    def source(self) -> Optional[pulumi.Input[Union[pulumi.Asset, pulumi.Archive]]]:
        return pulumi.get(self, "source")

    @source.setter
    def source(self, value: Optional[pulumi.Input[Union[pulumi.Asset, pulumi.Archive]]]):
        pulumi.set(self, "source", value)


class Job(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 configuration: Optional[pulumi.Input[pulumi.InputType['JobConfigurationArgs']]] = None,
                 job_reference: Optional[pulumi.Input[pulumi.InputType['JobReferenceArgs']]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 source: Optional[pulumi.Input[Union[pulumi.Asset, pulumi.Archive]]] = None,
                 __props__=None):
        """
        Starts a new asynchronous job. Requires the Can View project role.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['JobConfigurationArgs']] configuration: [Required] Describes the job configuration.
        :param pulumi.Input[pulumi.InputType['JobReferenceArgs']] job_reference: [Optional] Reference describing the unique-per-user name of the job.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[JobArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Starts a new asynchronous job. Requires the Can View project role.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param JobArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(JobArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 configuration: Optional[pulumi.Input[pulumi.InputType['JobConfigurationArgs']]] = None,
                 job_reference: Optional[pulumi.Input[pulumi.InputType['JobReferenceArgs']]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 source: Optional[pulumi.Input[Union[pulumi.Asset, pulumi.Archive]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = JobArgs.__new__(JobArgs)

            __props__.__dict__["configuration"] = configuration
            __props__.__dict__["job_reference"] = job_reference
            __props__.__dict__["project"] = project
            __props__.__dict__["source"] = source
            __props__.__dict__["etag"] = None
            __props__.__dict__["kind"] = None
            __props__.__dict__["self_link"] = None
            __props__.__dict__["statistics"] = None
            __props__.__dict__["status"] = None
            __props__.__dict__["user_email"] = None
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["project"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(Job, __self__).__init__(
            'google-native:bigquery/v2:Job',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Job':
        """
        Get an existing Job resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = JobArgs.__new__(JobArgs)

        __props__.__dict__["configuration"] = None
        __props__.__dict__["etag"] = None
        __props__.__dict__["job_reference"] = None
        __props__.__dict__["kind"] = None
        __props__.__dict__["project"] = None
        __props__.__dict__["self_link"] = None
        __props__.__dict__["statistics"] = None
        __props__.__dict__["status"] = None
        __props__.__dict__["user_email"] = None
        return Job(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def configuration(self) -> pulumi.Output['outputs.JobConfigurationResponse']:
        """
        [Required] Describes the job configuration.
        """
        return pulumi.get(self, "configuration")

    @property
    @pulumi.getter
    def etag(self) -> pulumi.Output[str]:
        """
        A hash of this resource.
        """
        return pulumi.get(self, "etag")

    @property
    @pulumi.getter(name="jobReference")
    def job_reference(self) -> pulumi.Output['outputs.JobReferenceResponse']:
        """
        [Optional] Reference describing the unique-per-user name of the job.
        """
        return pulumi.get(self, "job_reference")

    @property
    @pulumi.getter
    def kind(self) -> pulumi.Output[str]:
        """
        The type of the resource.
        """
        return pulumi.get(self, "kind")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        return pulumi.get(self, "project")

    @property
    @pulumi.getter(name="selfLink")
    def self_link(self) -> pulumi.Output[str]:
        """
        A URL that can be used to access this resource again.
        """
        return pulumi.get(self, "self_link")

    @property
    @pulumi.getter
    def statistics(self) -> pulumi.Output['outputs.JobStatisticsResponse']:
        """
        Information about the job, including starting time and ending time of the job.
        """
        return pulumi.get(self, "statistics")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output['outputs.JobStatusResponse']:
        """
        The status of this job. Examine this value when polling an asynchronous job to see if the job is complete.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter(name="userEmail")
    def user_email(self) -> pulumi.Output[str]:
        """
        Email address of the user who ran the job.
        """
        return pulumi.get(self, "user_email")

