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

__all__ = ['EvaluationJobArgs', 'EvaluationJob']

@pulumi.input_type
class EvaluationJobArgs:
    def __init__(__self__, *,
                 annotation_spec_set: pulumi.Input[str],
                 description: pulumi.Input[str],
                 evaluation_job_config: pulumi.Input['GoogleCloudDatalabelingV1beta1EvaluationJobConfigArgs'],
                 label_missing_ground_truth: pulumi.Input[bool],
                 model_version: pulumi.Input[str],
                 schedule: pulumi.Input[str],
                 project: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a EvaluationJob resource.
        :param pulumi.Input[str] annotation_spec_set: Name of the AnnotationSpecSet describing all the labels that your machine learning model outputs. You must create this resource before you create an evaluation job and provide its name in the following format: "projects/{project_id}/annotationSpecSets/{annotation_spec_set_id}"
        :param pulumi.Input[str] description: Description of the job. The description can be up to 25,000 characters long.
        :param pulumi.Input['GoogleCloudDatalabelingV1beta1EvaluationJobConfigArgs'] evaluation_job_config: Configuration details for the evaluation job.
        :param pulumi.Input[bool] label_missing_ground_truth: Whether you want Data Labeling Service to provide ground truth labels for prediction input. If you want the service to assign human labelers to annotate your data, set this to `true`. If you want to provide your own ground truth labels in the evaluation job's BigQuery table, set this to `false`.
        :param pulumi.Input[str] model_version: The [AI Platform Prediction model version](/ml-engine/docs/prediction-overview) to be evaluated. Prediction input and output is sampled from this model version. When creating an evaluation job, specify the model version in the following format: "projects/{project_id}/models/{model_name}/versions/{version_name}" There can only be one evaluation job per model version.
        :param pulumi.Input[str] schedule: Describes the interval at which the job runs. This interval must be at least 1 day, and it is rounded to the nearest day. For example, if you specify a 50-hour interval, the job runs every 2 days. You can provide the schedule in [crontab format](/scheduler/docs/configuring/cron-job-schedules) or in an [English-like format](/appengine/docs/standard/python/config/cronref#schedule_format). Regardless of what you specify, the job will run at 10:00 AM UTC. Only the interval from this schedule is used, not the specific time of day.
        """
        pulumi.set(__self__, "annotation_spec_set", annotation_spec_set)
        pulumi.set(__self__, "description", description)
        pulumi.set(__self__, "evaluation_job_config", evaluation_job_config)
        pulumi.set(__self__, "label_missing_ground_truth", label_missing_ground_truth)
        pulumi.set(__self__, "model_version", model_version)
        pulumi.set(__self__, "schedule", schedule)
        if project is not None:
            pulumi.set(__self__, "project", project)

    @property
    @pulumi.getter(name="annotationSpecSet")
    def annotation_spec_set(self) -> pulumi.Input[str]:
        """
        Name of the AnnotationSpecSet describing all the labels that your machine learning model outputs. You must create this resource before you create an evaluation job and provide its name in the following format: "projects/{project_id}/annotationSpecSets/{annotation_spec_set_id}"
        """
        return pulumi.get(self, "annotation_spec_set")

    @annotation_spec_set.setter
    def annotation_spec_set(self, value: pulumi.Input[str]):
        pulumi.set(self, "annotation_spec_set", value)

    @property
    @pulumi.getter
    def description(self) -> pulumi.Input[str]:
        """
        Description of the job. The description can be up to 25,000 characters long.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: pulumi.Input[str]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="evaluationJobConfig")
    def evaluation_job_config(self) -> pulumi.Input['GoogleCloudDatalabelingV1beta1EvaluationJobConfigArgs']:
        """
        Configuration details for the evaluation job.
        """
        return pulumi.get(self, "evaluation_job_config")

    @evaluation_job_config.setter
    def evaluation_job_config(self, value: pulumi.Input['GoogleCloudDatalabelingV1beta1EvaluationJobConfigArgs']):
        pulumi.set(self, "evaluation_job_config", value)

    @property
    @pulumi.getter(name="labelMissingGroundTruth")
    def label_missing_ground_truth(self) -> pulumi.Input[bool]:
        """
        Whether you want Data Labeling Service to provide ground truth labels for prediction input. If you want the service to assign human labelers to annotate your data, set this to `true`. If you want to provide your own ground truth labels in the evaluation job's BigQuery table, set this to `false`.
        """
        return pulumi.get(self, "label_missing_ground_truth")

    @label_missing_ground_truth.setter
    def label_missing_ground_truth(self, value: pulumi.Input[bool]):
        pulumi.set(self, "label_missing_ground_truth", value)

    @property
    @pulumi.getter(name="modelVersion")
    def model_version(self) -> pulumi.Input[str]:
        """
        The [AI Platform Prediction model version](/ml-engine/docs/prediction-overview) to be evaluated. Prediction input and output is sampled from this model version. When creating an evaluation job, specify the model version in the following format: "projects/{project_id}/models/{model_name}/versions/{version_name}" There can only be one evaluation job per model version.
        """
        return pulumi.get(self, "model_version")

    @model_version.setter
    def model_version(self, value: pulumi.Input[str]):
        pulumi.set(self, "model_version", value)

    @property
    @pulumi.getter
    def schedule(self) -> pulumi.Input[str]:
        """
        Describes the interval at which the job runs. This interval must be at least 1 day, and it is rounded to the nearest day. For example, if you specify a 50-hour interval, the job runs every 2 days. You can provide the schedule in [crontab format](/scheduler/docs/configuring/cron-job-schedules) or in an [English-like format](/appengine/docs/standard/python/config/cronref#schedule_format). Regardless of what you specify, the job will run at 10:00 AM UTC. Only the interval from this schedule is used, not the specific time of day.
        """
        return pulumi.get(self, "schedule")

    @schedule.setter
    def schedule(self, value: pulumi.Input[str]):
        pulumi.set(self, "schedule", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)


class EvaluationJob(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 annotation_spec_set: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 evaluation_job_config: Optional[pulumi.Input[pulumi.InputType['GoogleCloudDatalabelingV1beta1EvaluationJobConfigArgs']]] = None,
                 label_missing_ground_truth: Optional[pulumi.Input[bool]] = None,
                 model_version: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 schedule: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Creates an evaluation job.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] annotation_spec_set: Name of the AnnotationSpecSet describing all the labels that your machine learning model outputs. You must create this resource before you create an evaluation job and provide its name in the following format: "projects/{project_id}/annotationSpecSets/{annotation_spec_set_id}"
        :param pulumi.Input[str] description: Description of the job. The description can be up to 25,000 characters long.
        :param pulumi.Input[pulumi.InputType['GoogleCloudDatalabelingV1beta1EvaluationJobConfigArgs']] evaluation_job_config: Configuration details for the evaluation job.
        :param pulumi.Input[bool] label_missing_ground_truth: Whether you want Data Labeling Service to provide ground truth labels for prediction input. If you want the service to assign human labelers to annotate your data, set this to `true`. If you want to provide your own ground truth labels in the evaluation job's BigQuery table, set this to `false`.
        :param pulumi.Input[str] model_version: The [AI Platform Prediction model version](/ml-engine/docs/prediction-overview) to be evaluated. Prediction input and output is sampled from this model version. When creating an evaluation job, specify the model version in the following format: "projects/{project_id}/models/{model_name}/versions/{version_name}" There can only be one evaluation job per model version.
        :param pulumi.Input[str] schedule: Describes the interval at which the job runs. This interval must be at least 1 day, and it is rounded to the nearest day. For example, if you specify a 50-hour interval, the job runs every 2 days. You can provide the schedule in [crontab format](/scheduler/docs/configuring/cron-job-schedules) or in an [English-like format](/appengine/docs/standard/python/config/cronref#schedule_format). Regardless of what you specify, the job will run at 10:00 AM UTC. Only the interval from this schedule is used, not the specific time of day.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: EvaluationJobArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates an evaluation job.
        Auto-naming is currently not supported for this resource.

        :param str resource_name: The name of the resource.
        :param EvaluationJobArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(EvaluationJobArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 annotation_spec_set: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 evaluation_job_config: Optional[pulumi.Input[pulumi.InputType['GoogleCloudDatalabelingV1beta1EvaluationJobConfigArgs']]] = None,
                 label_missing_ground_truth: Optional[pulumi.Input[bool]] = None,
                 model_version: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 schedule: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = EvaluationJobArgs.__new__(EvaluationJobArgs)

            if annotation_spec_set is None and not opts.urn:
                raise TypeError("Missing required property 'annotation_spec_set'")
            __props__.__dict__["annotation_spec_set"] = annotation_spec_set
            if description is None and not opts.urn:
                raise TypeError("Missing required property 'description'")
            __props__.__dict__["description"] = description
            if evaluation_job_config is None and not opts.urn:
                raise TypeError("Missing required property 'evaluation_job_config'")
            __props__.__dict__["evaluation_job_config"] = evaluation_job_config
            if label_missing_ground_truth is None and not opts.urn:
                raise TypeError("Missing required property 'label_missing_ground_truth'")
            __props__.__dict__["label_missing_ground_truth"] = label_missing_ground_truth
            if model_version is None and not opts.urn:
                raise TypeError("Missing required property 'model_version'")
            __props__.__dict__["model_version"] = model_version
            __props__.__dict__["project"] = project
            if schedule is None and not opts.urn:
                raise TypeError("Missing required property 'schedule'")
            __props__.__dict__["schedule"] = schedule
            __props__.__dict__["attempts"] = None
            __props__.__dict__["create_time"] = None
            __props__.__dict__["name"] = None
            __props__.__dict__["state"] = None
        replace_on_changes = pulumi.ResourceOptions(replace_on_changes=["project"])
        opts = pulumi.ResourceOptions.merge(opts, replace_on_changes)
        super(EvaluationJob, __self__).__init__(
            'google-native:datalabeling/v1beta1:EvaluationJob',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'EvaluationJob':
        """
        Get an existing EvaluationJob resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = EvaluationJobArgs.__new__(EvaluationJobArgs)

        __props__.__dict__["annotation_spec_set"] = None
        __props__.__dict__["attempts"] = None
        __props__.__dict__["create_time"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["evaluation_job_config"] = None
        __props__.__dict__["label_missing_ground_truth"] = None
        __props__.__dict__["model_version"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["project"] = None
        __props__.__dict__["schedule"] = None
        __props__.__dict__["state"] = None
        return EvaluationJob(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="annotationSpecSet")
    def annotation_spec_set(self) -> pulumi.Output[str]:
        """
        Name of the AnnotationSpecSet describing all the labels that your machine learning model outputs. You must create this resource before you create an evaluation job and provide its name in the following format: "projects/{project_id}/annotationSpecSets/{annotation_spec_set_id}"
        """
        return pulumi.get(self, "annotation_spec_set")

    @property
    @pulumi.getter
    def attempts(self) -> pulumi.Output[Sequence['outputs.GoogleCloudDatalabelingV1beta1AttemptResponse']]:
        """
        Every time the evaluation job runs and an error occurs, the failed attempt is appended to this array.
        """
        return pulumi.get(self, "attempts")

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> pulumi.Output[str]:
        """
        Timestamp of when this evaluation job was created.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        Description of the job. The description can be up to 25,000 characters long.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="evaluationJobConfig")
    def evaluation_job_config(self) -> pulumi.Output['outputs.GoogleCloudDatalabelingV1beta1EvaluationJobConfigResponse']:
        """
        Configuration details for the evaluation job.
        """
        return pulumi.get(self, "evaluation_job_config")

    @property
    @pulumi.getter(name="labelMissingGroundTruth")
    def label_missing_ground_truth(self) -> pulumi.Output[bool]:
        """
        Whether you want Data Labeling Service to provide ground truth labels for prediction input. If you want the service to assign human labelers to annotate your data, set this to `true`. If you want to provide your own ground truth labels in the evaluation job's BigQuery table, set this to `false`.
        """
        return pulumi.get(self, "label_missing_ground_truth")

    @property
    @pulumi.getter(name="modelVersion")
    def model_version(self) -> pulumi.Output[str]:
        """
        The [AI Platform Prediction model version](/ml-engine/docs/prediction-overview) to be evaluated. Prediction input and output is sampled from this model version. When creating an evaluation job, specify the model version in the following format: "projects/{project_id}/models/{model_name}/versions/{version_name}" There can only be one evaluation job per model version.
        """
        return pulumi.get(self, "model_version")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        After you create a job, Data Labeling Service assigns a name to the job with the following format: "projects/{project_id}/evaluationJobs/ {evaluation_job_id}"
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        return pulumi.get(self, "project")

    @property
    @pulumi.getter
    def schedule(self) -> pulumi.Output[str]:
        """
        Describes the interval at which the job runs. This interval must be at least 1 day, and it is rounded to the nearest day. For example, if you specify a 50-hour interval, the job runs every 2 days. You can provide the schedule in [crontab format](/scheduler/docs/configuring/cron-job-schedules) or in an [English-like format](/appengine/docs/standard/python/config/cronref#schedule_format). Regardless of what you specify, the job will run at 10:00 AM UTC. Only the interval from this schedule is used, not the specific time of day.
        """
        return pulumi.get(self, "schedule")

    @property
    @pulumi.getter
    def state(self) -> pulumi.Output[str]:
        """
        Describes the current state of the job.
        """
        return pulumi.get(self, "state")

