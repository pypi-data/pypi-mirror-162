# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs

__all__ = [
    'GetTemplateResult',
    'AwaitableGetTemplateResult',
    'get_template',
    'get_template_output',
]

@pulumi.output_type
class GetTemplateResult:
    def __init__(__self__, id=None, template=None):
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if template and not isinstance(template, dict):
            raise TypeError("Expected argument 'template' to be a dict")
        pulumi.set(__self__, "template", template)

    @property
    @pulumi.getter
    def id(self) -> Optional[str]:
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def template(self) -> Optional['outputs.Template']:
        return pulumi.get(self, "template")


class AwaitableGetTemplateResult(GetTemplateResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetTemplateResult(
            id=self.id,
            template=self.template)


def get_template(id: Optional[str] = None,
                 opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetTemplateResult:
    """
    Resource Type definition for AWS::SES::Template
    """
    __args__ = dict()
    __args__['id'] = id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws-native:ses:getTemplate', __args__, opts=opts, typ=GetTemplateResult).value

    return AwaitableGetTemplateResult(
        id=__ret__.id,
        template=__ret__.template)


@_utilities.lift_output_func(get_template)
def get_template_output(id: Optional[pulumi.Input[str]] = None,
                        opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetTemplateResult]:
    """
    Resource Type definition for AWS::SES::Template
    """
    ...
