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
    'GetOriginRequestPolicyResult',
    'AwaitableGetOriginRequestPolicyResult',
    'get_origin_request_policy',
    'get_origin_request_policy_output',
]

@pulumi.output_type
class GetOriginRequestPolicyResult:
    def __init__(__self__, id=None, last_modified_time=None, origin_request_policy_config=None):
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if last_modified_time and not isinstance(last_modified_time, str):
            raise TypeError("Expected argument 'last_modified_time' to be a str")
        pulumi.set(__self__, "last_modified_time", last_modified_time)
        if origin_request_policy_config and not isinstance(origin_request_policy_config, dict):
            raise TypeError("Expected argument 'origin_request_policy_config' to be a dict")
        pulumi.set(__self__, "origin_request_policy_config", origin_request_policy_config)

    @property
    @pulumi.getter
    def id(self) -> Optional[str]:
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="lastModifiedTime")
    def last_modified_time(self) -> Optional[str]:
        return pulumi.get(self, "last_modified_time")

    @property
    @pulumi.getter(name="originRequestPolicyConfig")
    def origin_request_policy_config(self) -> Optional['outputs.OriginRequestPolicyConfig']:
        return pulumi.get(self, "origin_request_policy_config")


class AwaitableGetOriginRequestPolicyResult(GetOriginRequestPolicyResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetOriginRequestPolicyResult(
            id=self.id,
            last_modified_time=self.last_modified_time,
            origin_request_policy_config=self.origin_request_policy_config)


def get_origin_request_policy(id: Optional[str] = None,
                              opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetOriginRequestPolicyResult:
    """
    Resource Type definition for AWS::CloudFront::OriginRequestPolicy
    """
    __args__ = dict()
    __args__['id'] = id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws-native:cloudfront:getOriginRequestPolicy', __args__, opts=opts, typ=GetOriginRequestPolicyResult).value

    return AwaitableGetOriginRequestPolicyResult(
        id=__ret__.id,
        last_modified_time=__ret__.last_modified_time,
        origin_request_policy_config=__ret__.origin_request_policy_config)


@_utilities.lift_output_func(get_origin_request_policy)
def get_origin_request_policy_output(id: Optional[pulumi.Input[str]] = None,
                                     opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetOriginRequestPolicyResult]:
    """
    Resource Type definition for AWS::CloudFront::OriginRequestPolicy
    """
    ...
