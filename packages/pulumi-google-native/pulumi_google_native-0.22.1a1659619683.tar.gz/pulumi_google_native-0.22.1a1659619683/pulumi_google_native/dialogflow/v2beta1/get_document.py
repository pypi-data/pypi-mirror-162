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
    'GetDocumentResult',
    'AwaitableGetDocumentResult',
    'get_document',
    'get_document_output',
]

@pulumi.output_type
class GetDocumentResult:
    def __init__(__self__, content=None, content_uri=None, display_name=None, enable_auto_reload=None, knowledge_types=None, latest_reload_status=None, metadata=None, mime_type=None, name=None, raw_content=None, state=None):
        if content and not isinstance(content, str):
            raise TypeError("Expected argument 'content' to be a str")
        pulumi.set(__self__, "content", content)
        if content_uri and not isinstance(content_uri, str):
            raise TypeError("Expected argument 'content_uri' to be a str")
        pulumi.set(__self__, "content_uri", content_uri)
        if display_name and not isinstance(display_name, str):
            raise TypeError("Expected argument 'display_name' to be a str")
        pulumi.set(__self__, "display_name", display_name)
        if enable_auto_reload and not isinstance(enable_auto_reload, bool):
            raise TypeError("Expected argument 'enable_auto_reload' to be a bool")
        pulumi.set(__self__, "enable_auto_reload", enable_auto_reload)
        if knowledge_types and not isinstance(knowledge_types, list):
            raise TypeError("Expected argument 'knowledge_types' to be a list")
        pulumi.set(__self__, "knowledge_types", knowledge_types)
        if latest_reload_status and not isinstance(latest_reload_status, dict):
            raise TypeError("Expected argument 'latest_reload_status' to be a dict")
        pulumi.set(__self__, "latest_reload_status", latest_reload_status)
        if metadata and not isinstance(metadata, dict):
            raise TypeError("Expected argument 'metadata' to be a dict")
        pulumi.set(__self__, "metadata", metadata)
        if mime_type and not isinstance(mime_type, str):
            raise TypeError("Expected argument 'mime_type' to be a str")
        pulumi.set(__self__, "mime_type", mime_type)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if raw_content and not isinstance(raw_content, str):
            raise TypeError("Expected argument 'raw_content' to be a str")
        pulumi.set(__self__, "raw_content", raw_content)
        if state and not isinstance(state, str):
            raise TypeError("Expected argument 'state' to be a str")
        pulumi.set(__self__, "state", state)

    @property
    @pulumi.getter
    def content(self) -> str:
        """
        The raw content of the document. This field is only permitted for EXTRACTIVE_QA and FAQ knowledge types. Note: This field is in the process of being deprecated, please use raw_content instead.
        """
        return pulumi.get(self, "content")

    @property
    @pulumi.getter(name="contentUri")
    def content_uri(self) -> str:
        """
        The URI where the file content is located. For documents stored in Google Cloud Storage, these URIs must have the form `gs:///`. NOTE: External URLs must correspond to public webpages, i.e., they must be indexed by Google Search. In particular, URLs for showing documents in Google Cloud Storage (i.e. the URL in your browser) are not supported. Instead use the `gs://` format URI described above.
        """
        return pulumi.get(self, "content_uri")

    @property
    @pulumi.getter(name="displayName")
    def display_name(self) -> str:
        """
        The display name of the document. The name must be 1024 bytes or less; otherwise, the creation request fails.
        """
        return pulumi.get(self, "display_name")

    @property
    @pulumi.getter(name="enableAutoReload")
    def enable_auto_reload(self) -> bool:
        """
        Optional. If true, we try to automatically reload the document every day (at a time picked by the system). If false or unspecified, we don't try to automatically reload the document. Currently you can only enable automatic reload for documents sourced from a public url, see `source` field for the source types. Reload status can be tracked in `latest_reload_status`. If a reload fails, we will keep the document unchanged. If a reload fails with internal errors, the system will try to reload the document on the next day. If a reload fails with non-retriable errors (e.g. PERMISSION_DENIED), the system will not try to reload the document anymore. You need to manually reload the document successfully by calling `ReloadDocument` and clear the errors.
        """
        return pulumi.get(self, "enable_auto_reload")

    @property
    @pulumi.getter(name="knowledgeTypes")
    def knowledge_types(self) -> Sequence[str]:
        """
        The knowledge type of document content.
        """
        return pulumi.get(self, "knowledge_types")

    @property
    @pulumi.getter(name="latestReloadStatus")
    def latest_reload_status(self) -> 'outputs.GoogleCloudDialogflowV2beta1DocumentReloadStatusResponse':
        """
        The time and status of the latest reload. This reload may have been triggered automatically or manually and may not have succeeded.
        """
        return pulumi.get(self, "latest_reload_status")

    @property
    @pulumi.getter
    def metadata(self) -> Mapping[str, str]:
        """
        Optional. Metadata for the document. The metadata supports arbitrary key-value pairs. Suggested use cases include storing a document's title, an external URL distinct from the document's content_uri, etc. The max size of a `key` or a `value` of the metadata is 1024 bytes.
        """
        return pulumi.get(self, "metadata")

    @property
    @pulumi.getter(name="mimeType")
    def mime_type(self) -> str:
        """
        The MIME type of this document.
        """
        return pulumi.get(self, "mime_type")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Optional. The document resource name. The name must be empty when creating a document. Format: `projects//locations//knowledgeBases//documents/`.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="rawContent")
    def raw_content(self) -> str:
        """
        The raw content of the document. This field is only permitted for EXTRACTIVE_QA and FAQ knowledge types.
        """
        return pulumi.get(self, "raw_content")

    @property
    @pulumi.getter
    def state(self) -> str:
        """
        The current state of the document.
        """
        return pulumi.get(self, "state")


class AwaitableGetDocumentResult(GetDocumentResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetDocumentResult(
            content=self.content,
            content_uri=self.content_uri,
            display_name=self.display_name,
            enable_auto_reload=self.enable_auto_reload,
            knowledge_types=self.knowledge_types,
            latest_reload_status=self.latest_reload_status,
            metadata=self.metadata,
            mime_type=self.mime_type,
            name=self.name,
            raw_content=self.raw_content,
            state=self.state)


def get_document(document_id: Optional[str] = None,
                 knowledge_base_id: Optional[str] = None,
                 location: Optional[str] = None,
                 project: Optional[str] = None,
                 opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetDocumentResult:
    """
    Retrieves the specified document. Note: The `projects.agent.knowledgeBases.documents` resource is deprecated; only use `projects.knowledgeBases.documents`.
    """
    __args__ = dict()
    __args__['documentId'] = document_id
    __args__['knowledgeBaseId'] = knowledge_base_id
    __args__['location'] = location
    __args__['project'] = project
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('google-native:dialogflow/v2beta1:getDocument', __args__, opts=opts, typ=GetDocumentResult).value

    return AwaitableGetDocumentResult(
        content=__ret__.content,
        content_uri=__ret__.content_uri,
        display_name=__ret__.display_name,
        enable_auto_reload=__ret__.enable_auto_reload,
        knowledge_types=__ret__.knowledge_types,
        latest_reload_status=__ret__.latest_reload_status,
        metadata=__ret__.metadata,
        mime_type=__ret__.mime_type,
        name=__ret__.name,
        raw_content=__ret__.raw_content,
        state=__ret__.state)


@_utilities.lift_output_func(get_document)
def get_document_output(document_id: Optional[pulumi.Input[str]] = None,
                        knowledge_base_id: Optional[pulumi.Input[str]] = None,
                        location: Optional[pulumi.Input[str]] = None,
                        project: Optional[pulumi.Input[Optional[str]]] = None,
                        opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetDocumentResult]:
    """
    Retrieves the specified document. Note: The `projects.agent.knowledgeBases.documents` resource is deprecated; only use `projects.knowledgeBases.documents`.
    """
    ...
