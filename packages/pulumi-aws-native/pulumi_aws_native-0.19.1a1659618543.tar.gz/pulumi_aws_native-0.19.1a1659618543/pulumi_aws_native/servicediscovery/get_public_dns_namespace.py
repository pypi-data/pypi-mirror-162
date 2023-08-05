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
    'GetPublicDnsNamespaceResult',
    'AwaitableGetPublicDnsNamespaceResult',
    'get_public_dns_namespace',
    'get_public_dns_namespace_output',
]

@pulumi.output_type
class GetPublicDnsNamespaceResult:
    def __init__(__self__, arn=None, description=None, hosted_zone_id=None, id=None, properties=None, tags=None):
        if arn and not isinstance(arn, str):
            raise TypeError("Expected argument 'arn' to be a str")
        pulumi.set(__self__, "arn", arn)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if hosted_zone_id and not isinstance(hosted_zone_id, str):
            raise TypeError("Expected argument 'hosted_zone_id' to be a str")
        pulumi.set(__self__, "hosted_zone_id", hosted_zone_id)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if properties and not isinstance(properties, dict):
            raise TypeError("Expected argument 'properties' to be a dict")
        pulumi.set(__self__, "properties", properties)
        if tags and not isinstance(tags, list):
            raise TypeError("Expected argument 'tags' to be a list")
        pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter
    def arn(self) -> Optional[str]:
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter
    def description(self) -> Optional[str]:
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="hostedZoneId")
    def hosted_zone_id(self) -> Optional[str]:
        return pulumi.get(self, "hosted_zone_id")

    @property
    @pulumi.getter
    def id(self) -> Optional[str]:
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def properties(self) -> Optional['outputs.PublicDnsNamespaceProperties']:
        return pulumi.get(self, "properties")

    @property
    @pulumi.getter
    def tags(self) -> Optional[Sequence['outputs.PublicDnsNamespaceTag']]:
        return pulumi.get(self, "tags")


class AwaitableGetPublicDnsNamespaceResult(GetPublicDnsNamespaceResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetPublicDnsNamespaceResult(
            arn=self.arn,
            description=self.description,
            hosted_zone_id=self.hosted_zone_id,
            id=self.id,
            properties=self.properties,
            tags=self.tags)


def get_public_dns_namespace(id: Optional[str] = None,
                             opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetPublicDnsNamespaceResult:
    """
    Resource Type definition for AWS::ServiceDiscovery::PublicDnsNamespace
    """
    __args__ = dict()
    __args__['id'] = id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws-native:servicediscovery:getPublicDnsNamespace', __args__, opts=opts, typ=GetPublicDnsNamespaceResult).value

    return AwaitableGetPublicDnsNamespaceResult(
        arn=__ret__.arn,
        description=__ret__.description,
        hosted_zone_id=__ret__.hosted_zone_id,
        id=__ret__.id,
        properties=__ret__.properties,
        tags=__ret__.tags)


@_utilities.lift_output_func(get_public_dns_namespace)
def get_public_dns_namespace_output(id: Optional[pulumi.Input[str]] = None,
                                    opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetPublicDnsNamespaceResult]:
    """
    Resource Type definition for AWS::ServiceDiscovery::PublicDnsNamespace
    """
    ...
