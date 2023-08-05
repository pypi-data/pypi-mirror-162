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
    'GetConversationResult',
    'AwaitableGetConversationResult',
    'get_conversation',
    'get_conversation_output',
]

@pulumi.output_type
class GetConversationResult:
    def __init__(__self__, conversation_profile=None, conversation_stage=None, end_time=None, lifecycle_state=None, name=None, phone_number=None, start_time=None):
        if conversation_profile and not isinstance(conversation_profile, str):
            raise TypeError("Expected argument 'conversation_profile' to be a str")
        pulumi.set(__self__, "conversation_profile", conversation_profile)
        if conversation_stage and not isinstance(conversation_stage, str):
            raise TypeError("Expected argument 'conversation_stage' to be a str")
        pulumi.set(__self__, "conversation_stage", conversation_stage)
        if end_time and not isinstance(end_time, str):
            raise TypeError("Expected argument 'end_time' to be a str")
        pulumi.set(__self__, "end_time", end_time)
        if lifecycle_state and not isinstance(lifecycle_state, str):
            raise TypeError("Expected argument 'lifecycle_state' to be a str")
        pulumi.set(__self__, "lifecycle_state", lifecycle_state)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if phone_number and not isinstance(phone_number, dict):
            raise TypeError("Expected argument 'phone_number' to be a dict")
        pulumi.set(__self__, "phone_number", phone_number)
        if start_time and not isinstance(start_time, str):
            raise TypeError("Expected argument 'start_time' to be a str")
        pulumi.set(__self__, "start_time", start_time)

    @property
    @pulumi.getter(name="conversationProfile")
    def conversation_profile(self) -> str:
        """
        The Conversation Profile to be used to configure this Conversation. This field cannot be updated. Format: `projects//locations//conversationProfiles/`.
        """
        return pulumi.get(self, "conversation_profile")

    @property
    @pulumi.getter(name="conversationStage")
    def conversation_stage(self) -> str:
        """
        The stage of a conversation. It indicates whether the virtual agent or a human agent is handling the conversation. If the conversation is created with the conversation profile that has Dialogflow config set, defaults to ConversationStage.VIRTUAL_AGENT_STAGE; Otherwise, defaults to ConversationStage.HUMAN_ASSIST_STAGE. If the conversation is created with the conversation profile that has Dialogflow config set but explicitly sets conversation_stage to ConversationStage.HUMAN_ASSIST_STAGE, it skips ConversationStage.VIRTUAL_AGENT_STAGE stage and directly goes to ConversationStage.HUMAN_ASSIST_STAGE.
        """
        return pulumi.get(self, "conversation_stage")

    @property
    @pulumi.getter(name="endTime")
    def end_time(self) -> str:
        """
        The time the conversation was finished.
        """
        return pulumi.get(self, "end_time")

    @property
    @pulumi.getter(name="lifecycleState")
    def lifecycle_state(self) -> str:
        """
        The current state of the Conversation.
        """
        return pulumi.get(self, "lifecycle_state")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The unique identifier of this conversation. Format: `projects//locations//conversations/`.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="phoneNumber")
    def phone_number(self) -> 'outputs.GoogleCloudDialogflowV2beta1ConversationPhoneNumberResponse':
        """
        Required if the conversation is to be connected over telephony.
        """
        return pulumi.get(self, "phone_number")

    @property
    @pulumi.getter(name="startTime")
    def start_time(self) -> str:
        """
        The time the conversation was started.
        """
        return pulumi.get(self, "start_time")


class AwaitableGetConversationResult(GetConversationResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetConversationResult(
            conversation_profile=self.conversation_profile,
            conversation_stage=self.conversation_stage,
            end_time=self.end_time,
            lifecycle_state=self.lifecycle_state,
            name=self.name,
            phone_number=self.phone_number,
            start_time=self.start_time)


def get_conversation(conversation_id: Optional[str] = None,
                     location: Optional[str] = None,
                     project: Optional[str] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetConversationResult:
    """
    Retrieves the specific conversation.
    """
    __args__ = dict()
    __args__['conversationId'] = conversation_id
    __args__['location'] = location
    __args__['project'] = project
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:dialogflow/v2beta1:getConversation', __args__, opts=opts, typ=GetConversationResult).value

    return AwaitableGetConversationResult(
        conversation_profile=__ret__.conversation_profile,
        conversation_stage=__ret__.conversation_stage,
        end_time=__ret__.end_time,
        lifecycle_state=__ret__.lifecycle_state,
        name=__ret__.name,
        phone_number=__ret__.phone_number,
        start_time=__ret__.start_time)


@_utilities.lift_output_func(get_conversation)
def get_conversation_output(conversation_id: Optional[pulumi.Input[str]] = None,
                            location: Optional[pulumi.Input[str]] = None,
                            project: Optional[pulumi.Input[Optional[str]]] = None,
                            opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetConversationResult]:
    """
    Retrieves the specific conversation.
    """
    ...
