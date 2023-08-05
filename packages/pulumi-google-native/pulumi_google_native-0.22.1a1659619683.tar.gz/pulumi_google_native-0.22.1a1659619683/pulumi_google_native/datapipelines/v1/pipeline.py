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
from ._inputs import *

__all__ = ['PipelineArgs', 'Pipeline']

@pulumi.input_type
class PipelineArgs:
    def __init__(__self__, *,
                 display_name: pulumi.Input[str],
                 state: pulumi.Input['PipelineState'],
                 type: pulumi.Input['PipelineType'],
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 pipeline_sources: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 schedule_info: Optional[pulumi.Input['GoogleCloudDatapipelinesV1ScheduleSpecArgs']] = None,
                 scheduler_service_account_email: Optional[pulumi.Input[str]] = None,
                 workload: Optional[pulumi.Input['GoogleCloudDatapipelinesV1WorkloadArgs']] = None):
        """
        The set of arguments for constructing a Pipeline resource.
        :param pulumi.Input[str] display_name: The display name of the pipeline. It can contain only letters ([A-Za-z]), numbers ([0-9]), hyphens (-), and underscores (_).
        :param pulumi.Input['PipelineState'] state: The state of the pipeline. When the pipeline is created, the state is set to 'PIPELINE_STATE_ACTIVE' by default. State changes can be requested by setting the state to stopping, paused, or resuming. State cannot be changed through UpdatePipeline requests.
        :param pulumi.Input['PipelineType'] type: The type of the pipeline. This field affects the scheduling of the pipeline and the type of metrics to show for the pipeline.
        :param pulumi.Input[str] name: The pipeline name. For example: `projects/PROJECT_ID/locations/LOCATION_ID/pipelines/PIPELINE_ID`. * `PROJECT_ID` can contain letters ([A-Za-z]), numbers ([0-9]), hyphens (-), colons (:), and periods (.). For more information, see [Identifying projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects). * `LOCATION_ID` is the canonical ID for the pipeline's location. The list of available locations can be obtained by calling `google.cloud.location.Locations.ListLocations`. Note that the Data Pipelines service is not available in all regions. It depends on Cloud Scheduler, an App Engine application, so it's only available in [App Engine regions](https://cloud.google.com/about/locations#region). * `PIPELINE_ID` is the ID of the pipeline. Must be unique for the selected project and location.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] pipeline_sources: Immutable. The sources of the pipeline (for example, Dataplex). The keys and values are set by the corresponding sources during pipeline creation.
        :param pulumi.Input['GoogleCloudDatapipelinesV1ScheduleSpecArgs'] schedule_info: Internal scheduling information for a pipeline. If this information is provided, periodic jobs will be created per the schedule. If not, users are responsible for creating jobs externally.
        :param pulumi.Input[str] scheduler_service_account_email: Optional. A service account email to be used with the Cloud Scheduler job. If not specified, the default compute engine service account will be used.
        :param pulumi.Input['GoogleCloudDatapipelinesV1WorkloadArgs'] workload: Workload information for creating new jobs.
        """
        pulumi.set(__self__, "display_name", display_name)
        pulumi.set(__self__, "state", state)
        pulumi.set(__self__, "type", type)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if pipeline_sources is not None:
            pulumi.set(__self__, "pipeline_sources", pipeline_sources)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if schedule_info is not None:
            pulumi.set(__self__, "schedule_info", schedule_info)
        if scheduler_service_account_email is not None:
            pulumi.set(__self__, "scheduler_service_account_email", scheduler_service_account_email)
        if workload is not None:
            pulumi.set(__self__, "workload", workload)

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> pulumi.Input[str]:
        """
        The display name of the pipeline. It can contain only letters ([A-Za-z]), numbers ([0-9]), hyphens (-), and underscores (_).
        """
        return pulumi.get(self, "display_name")

    @display_name.setter
    def display_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "display_name", value)

    @property
    @pulumi.getter
    def state(self) -> pulumi.Input['PipelineState']:
        """
        The state of the pipeline. When the pipeline is created, the state is set to 'PIPELINE_STATE_ACTIVE' by default. State changes can be requested by setting the state to stopping, paused, or resuming. State cannot be changed through UpdatePipeline requests.
        """
        return pulumi.get(self, "state")

    @state.setter
    def state(self, value: pulumi.Input['PipelineState']):
        pulumi.set(self, "state", value)

    @property
    @pulumi.getter
    def type(self) -> pulumi.Input['PipelineType']:
        """
        The type of the pipeline. This field affects the scheduling of the pipeline and the type of metrics to show for the pipeline.
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: pulumi.Input['PipelineType']):
        pulumi.set(self, "type", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The pipeline name. For example: `projects/PROJECT_ID/locations/LOCATION_ID/pipelines/PIPELINE_ID`. * `PROJECT_ID` can contain letters ([A-Za-z]), numbers ([0-9]), hyphens (-), colons (:), and periods (.). For more information, see [Identifying projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects). * `LOCATION_ID` is the canonical ID for the pipeline's location. The list of available locations can be obtained by calling `google.cloud.location.Locations.ListLocations`. Note that the Data Pipelines service is not available in all regions. It depends on Cloud Scheduler, an App Engine application, so it's only available in [App Engine regions](https://cloud.google.com/about/locations#region). * `PIPELINE_ID` is the ID of the pipeline. Must be unique for the selected project and location.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="pipelineSources")
    def pipeline_sources(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Immutable. The sources of the pipeline (for example, Dataplex). The keys and values are set by the corresponding sources during pipeline creation.
        """
        return pulumi.get(self, "pipeline_sources")

    @pipeline_sources.setter
    def pipeline_sources(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "pipeline_sources", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)

    @property
    @pulumi.getter(name="scheduleInfo")
    def schedule_info(self) -> Optional[pulumi.Input['GoogleCloudDatapipelinesV1ScheduleSpecArgs']]:
        """
        Internal scheduling information for a pipeline. If this information is provided, periodic jobs will be created per the schedule. If not, users are responsible for creating jobs externally.
        """
        return pulumi.get(self, "schedule_info")

    @schedule_info.setter
    def schedule_info(self, value: Optional[pulumi.Input['GoogleCloudDatapipelinesV1ScheduleSpecArgs']]):
        pulumi.set(self, "schedule_info", value)

    @property
    @pulumi.getter(name="schedulerServiceAccountEmail")
    def scheduler_service_account_email(self) -> Optional[pulumi.Input[str]]:
        """
        Optional. A service account email to be used with the Cloud Scheduler job. If not specified, the default compute engine service account will be used.
        """
        return pulumi.get(self, "scheduler_service_account_email")

    @scheduler_service_account_email.setter
    def scheduler_service_account_email(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "scheduler_service_account_email", value)

    @property
    @pulumi.getter
    def workload(self) -> Optional[pulumi.Input['GoogleCloudDatapipelinesV1WorkloadArgs']]:
        """
        Workload information for creating new jobs.
        """
        return pulumi.get(self, "workload")

    @workload.setter
    def workload(self, value: Optional[pulumi.Input['GoogleCloudDatapipelinesV1WorkloadArgs']]):
        pulumi.set(self, "workload", value)


class Pipeline(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 pipeline_sources: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 schedule_info: Optional[pulumi.Input[pulumi.InputType['GoogleCloudDatapipelinesV1ScheduleSpecArgs']]] = None,
                 scheduler_service_account_email: Optional[pulumi.Input[str]] = None,
                 state: Optional[pulumi.Input['PipelineState']] = None,
                 type: Optional[pulumi.Input['PipelineType']] = None,
                 workload: Optional[pulumi.Input[pulumi.InputType['GoogleCloudDatapipelinesV1WorkloadArgs']]] = None,
                 __props__=None):
        """
        Creates a pipeline. For a batch pipeline, you can pass scheduler information. Data Pipelines uses the scheduler information to create an internal scheduler that runs jobs periodically. If the internal scheduler is not configured, you can use RunPipeline to run jobs.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] display_name: The display name of the pipeline. It can contain only letters ([A-Za-z]), numbers ([0-9]), hyphens (-), and underscores (_).
        :param pulumi.Input[str] name: The pipeline name. For example: `projects/PROJECT_ID/locations/LOCATION_ID/pipelines/PIPELINE_ID`. * `PROJECT_ID` can contain letters ([A-Za-z]), numbers ([0-9]), hyphens (-), colons (:), and periods (.). For more information, see [Identifying projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects). * `LOCATION_ID` is the canonical ID for the pipeline's location. The list of available locations can be obtained by calling `google.cloud.location.Locations.ListLocations`. Note that the Data Pipelines service is not available in all regions. It depends on Cloud Scheduler, an App Engine application, so it's only available in [App Engine regions](https://cloud.google.com/about/locations#region). * `PIPELINE_ID` is the ID of the pipeline. Must be unique for the selected project and location.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] pipeline_sources: Immutable. The sources of the pipeline (for example, Dataplex). The keys and values are set by the corresponding sources during pipeline creation.
        :param pulumi.Input[pulumi.InputType['GoogleCloudDatapipelinesV1ScheduleSpecArgs']] schedule_info: Internal scheduling information for a pipeline. If this information is provided, periodic jobs will be created per the schedule. If not, users are responsible for creating jobs externally.
        :param pulumi.Input[str] scheduler_service_account_email: Optional. A service account email to be used with the Cloud Scheduler job. If not specified, the default compute engine service account will be used.
        :param pulumi.Input['PipelineState'] state: The state of the pipeline. When the pipeline is created, the state is set to 'PIPELINE_STATE_ACTIVE' by default. State changes can be requested by setting the state to stopping, paused, or resuming. State cannot be changed through UpdatePipeline requests.
        :param pulumi.Input['PipelineType'] type: The type of the pipeline. This field affects the scheduling of the pipeline and the type of metrics to show for the pipeline.
        :param pulumi.Input[pulumi.InputType['GoogleCloudDatapipelinesV1WorkloadArgs']] workload: Workload information for creating new jobs.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: PipelineArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a pipeline. For a batch pipeline, you can pass scheduler information. Data Pipelines uses the scheduler information to create an internal scheduler that runs jobs periodically. If the internal scheduler is not configured, you can use RunPipeline to run jobs.

        :param str resource_name: The name of the resource.
        :param PipelineArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(PipelineArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 display_name: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 pipeline_sources: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 schedule_info: Optional[pulumi.Input[pulumi.InputType['GoogleCloudDatapipelinesV1ScheduleSpecArgs']]] = None,
                 scheduler_service_account_email: Optional[pulumi.Input[str]] = None,
                 state: Optional[pulumi.Input['PipelineState']] = None,
                 type: Optional[pulumi.Input['PipelineType']] = None,
                 workload: Optional[pulumi.Input[pulumi.InputType['GoogleCloudDatapipelinesV1WorkloadArgs']]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = PipelineArgs.__new__(PipelineArgs)

            if display_name is None and not opts.urn:
                raise TypeError("Missing required property 'display_name'")
            __props__.__dict__["display_name"] = display_name
            __props__.__dict__["location"] = location
            __props__.__dict__["name"] = name
            __props__.__dict__["pipeline_sources"] = pipeline_sources
            __props__.__dict__["project"] = project
            __props__.__dict__["schedule_info"] = schedule_info
            __props__.__dict__["scheduler_service_account_email"] = scheduler_service_account_email
            if state is None and not opts.urn:
                raise TypeError("Missing required property 'state'")
            __props__.__dict__["state"] = state
            if type is None and not opts.urn:
                raise TypeError("Missing required property 'type'")
            __props__.__dict__["type"] = type
            __props__.__dict__["workload"] = workload
            __props__.__dict__["create_time"] = None
            __props__.__dict__["job_count"] = None
            __props__.__dict__["last_update_time"] = None
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["location", "project"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(Pipeline, __self__).__init__(
            'google-native:datapipelines/v1:Pipeline',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Pipeline':
        """
        Get an existing Pipeline resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = PipelineArgs.__new__(PipelineArgs)

        __props__.__dict__["create_time"] = None
        __props__.__dict__["display_name"] = None
        __props__.__dict__["job_count"] = None
        __props__.__dict__["last_update_time"] = None
        __props__.__dict__["location"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["pipeline_sources"] = None
        __props__.__dict__["project"] = None
        __props__.__dict__["schedule_info"] = None
        __props__.__dict__["scheduler_service_account_email"] = None
        __props__.__dict__["state"] = None
        __props__.__dict__["type"] = None
        __props__.__dict__["workload"] = None
        return Pipeline(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> pulumi.Output[str]:
        """
        Immutable. The timestamp when the pipeline was initially created. Set by the Data Pipelines service.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> pulumi.Output[str]:
        """
        The display name of the pipeline. It can contain only letters ([A-Za-z]), numbers ([0-9]), hyphens (-), and underscores (_).
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter(name="jobCount")
    def job_count(self) -> pulumi.Output[int]:
        """
        Number of jobs.
        """
        return pulumi.get(self, "job_count")

    @property
    @pulumi.getter(name="lastUpdateTime")
    def last_update_time(self) -> pulumi.Output[str]:
        """
        Immutable. The timestamp when the pipeline was last modified. Set by the Data Pipelines service.
        """
        return pulumi.get(self, "last_update_time")

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The pipeline name. For example: `projects/PROJECT_ID/locations/LOCATION_ID/pipelines/PIPELINE_ID`. * `PROJECT_ID` can contain letters ([A-Za-z]), numbers ([0-9]), hyphens (-), colons (:), and periods (.). For more information, see [Identifying projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects). * `LOCATION_ID` is the canonical ID for the pipeline's location. The list of available locations can be obtained by calling `google.cloud.location.Locations.ListLocations`. Note that the Data Pipelines service is not available in all regions. It depends on Cloud Scheduler, an App Engine application, so it's only available in [App Engine regions](https://cloud.google.com/about/locations#region). * `PIPELINE_ID` is the ID of the pipeline. Must be unique for the selected project and location.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="pipelineSources")
    def pipeline_sources(self) -> pulumi.Output[Mapping[str, str]]:
        """
        Immutable. The sources of the pipeline (for example, Dataplex). The keys and values are set by the corresponding sources during pipeline creation.
        """
        return pulumi.get(self, "pipeline_sources")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        return pulumi.get(self, "project")

    @property
    @pulumi.getter(name="scheduleInfo")
    def schedule_info(self) -> pulumi.Output['outputs.GoogleCloudDatapipelinesV1ScheduleSpecResponse']:
        """
        Internal scheduling information for a pipeline. If this information is provided, periodic jobs will be created per the schedule. If not, users are responsible for creating jobs externally.
        """
        return pulumi.get(self, "schedule_info")

    @property
    @pulumi.getter(name="schedulerServiceAccountEmail")
    def scheduler_service_account_email(self) -> pulumi.Output[str]:
        """
        Optional. A service account email to be used with the Cloud Scheduler job. If not specified, the default compute engine service account will be used.
        """
        return pulumi.get(self, "scheduler_service_account_email")

    @property
    @pulumi.getter
    def state(self) -> pulumi.Output[str]:
        """
        The state of the pipeline. When the pipeline is created, the state is set to 'PIPELINE_STATE_ACTIVE' by default. State changes can be requested by setting the state to stopping, paused, or resuming. State cannot be changed through UpdatePipeline requests.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter
    def type(self) -> pulumi.Output[str]:
        """
        The type of the pipeline. This field affects the scheduling of the pipeline and the type of metrics to show for the pipeline.
        """
        return pulumi.get(self, "type")

    @property
    @pulumi.getter
    def workload(self) -> pulumi.Output['outputs.GoogleCloudDatapipelinesV1WorkloadResponse']:
        """
        Workload information for creating new jobs.
        """
        return pulumi.get(self, "workload")

