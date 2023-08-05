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
    'GetEvaluationResult',
    'AwaitableGetEvaluationResult',
    'get_evaluation',
    'get_evaluation_output',
]

@pulumi.output_type
class GetEvaluationResult:
    def __init__(__self__, create_time=None, display_name=None, evaluation_config=None, name=None, smart_reply_metrics=None):
        if create_time and not isinstance(create_time, str):
            raise TypeError("Expected argument 'create_time' to be a str")
        pulumi.set(__self__, "create_time", create_time)
        if display_name and not isinstance(display_name, str):
            raise TypeError("Expected argument 'display_name' to be a str")
        pulumi.set(__self__, "display_name", display_name)
        if evaluation_config and not isinstance(evaluation_config, dict):
            raise TypeError("Expected argument 'evaluation_config' to be a dict")
        pulumi.set(__self__, "evaluation_config", evaluation_config)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if smart_reply_metrics and not isinstance(smart_reply_metrics, dict):
            raise TypeError("Expected argument 'smart_reply_metrics' to be a dict")
        pulumi.set(__self__, "smart_reply_metrics", smart_reply_metrics)

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> str:
        """
        Creation time of this model.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> str:
        """
        Optional. The display name of the model evaluation. At most 64 bytes long.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter(name="evaluationConfig")
    def evaluation_config(self) -> 'outputs.GoogleCloudDialogflowV2EvaluationConfigResponse':
        """
        Optional. The configuration of the evaluation task.
        """
        return pulumi.get(self, "evaluation_config")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The resource name of the evaluation. Format: `projects//conversationModels//evaluations/`
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="smartReplyMetrics")
    def smart_reply_metrics(self) -> 'outputs.GoogleCloudDialogflowV2SmartReplyMetricsResponse':
        """
        Only available when model is for smart reply.
        """
        return pulumi.get(self, "smart_reply_metrics")


class AwaitableGetEvaluationResult(GetEvaluationResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetEvaluationResult(
            create_time=self.create_time,
            display_name=self.display_name,
            evaluation_config=self.evaluation_config,
            name=self.name,
            smart_reply_metrics=self.smart_reply_metrics)


def get_evaluation(conversation_model_id: Optional[str] = None,
                   evaluation_id: Optional[str] = None,
                   location: Optional[str] = None,
                   project: Optional[str] = None,
                   opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetEvaluationResult:
    """
    Gets an evaluation of conversation model.
    """
    __args__ = dict()
    __args__['conversationModelId'] = conversation_model_id
    __args__['evaluationId'] = evaluation_id
    __args__['location'] = location
    __args__['project'] = project
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:dialogflow/v2:getEvaluation', __args__, opts=opts, typ=GetEvaluationResult).value

    return AwaitableGetEvaluationResult(
        create_time=__ret__.create_time,
        display_name=__ret__.display_name,
        evaluation_config=__ret__.evaluation_config,
        name=__ret__.name,
        smart_reply_metrics=__ret__.smart_reply_metrics)


@_utilities.lift_output_func(get_evaluation)
def get_evaluation_output(conversation_model_id: Optional[pulumi.Input[str]] = None,
                          evaluation_id: Optional[pulumi.Input[str]] = None,
                          location: Optional[pulumi.Input[str]] = None,
                          project: Optional[pulumi.Input[Optional[str]]] = None,
                          opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetEvaluationResult]:
    """
    Gets an evaluation of conversation model.
    """
    ...
