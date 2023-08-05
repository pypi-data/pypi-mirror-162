# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'GetUserPoolUICustomizationAttachmentResult',
    'AwaitableGetUserPoolUICustomizationAttachmentResult',
    'get_user_pool_ui_customization_attachment',
    'get_user_pool_ui_customization_attachment_output',
]

@pulumi.output_type
class GetUserPoolUICustomizationAttachmentResult:
    def __init__(__self__, c_ss=None, id=None):
        if c_ss and not isinstance(c_ss, str):
            raise TypeError("Expected argument 'c_ss' to be a str")
        pulumi.set(__self__, "c_ss", c_ss)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)

    @property
    @pulumi.getter(name="cSS")
    def c_ss(self) -> Optional[str]:
        return pulumi.get(self, "c_ss")

    @property
    @pulumi.getter
    def id(self) -> Optional[str]:
        return pulumi.get(self, "id")


class AwaitableGetUserPoolUICustomizationAttachmentResult(GetUserPoolUICustomizationAttachmentResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetUserPoolUICustomizationAttachmentResult(
            c_ss=self.c_ss,
            id=self.id)


def get_user_pool_ui_customization_attachment(id: Optional[str] = None,
                                              opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetUserPoolUICustomizationAttachmentResult:
    """
    Resource Type definition for AWS::Cognito::UserPoolUICustomizationAttachment
    """
    __args__ = dict()
    __args__['id'] = id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws-native:cognito:getUserPoolUICustomizationAttachment', __args__, opts=opts, typ=GetUserPoolUICustomizationAttachmentResult).value

    return AwaitableGetUserPoolUICustomizationAttachmentResult(
        c_ss=__ret__.c_ss,
        id=__ret__.id)


@_utilities.lift_output_func(get_user_pool_ui_customization_attachment)
def get_user_pool_ui_customization_attachment_output(id: Optional[pulumi.Input[str]] = None,
                                                     opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetUserPoolUICustomizationAttachmentResult]:
    """
    Resource Type definition for AWS::Cognito::UserPoolUICustomizationAttachment
    """
    ...
