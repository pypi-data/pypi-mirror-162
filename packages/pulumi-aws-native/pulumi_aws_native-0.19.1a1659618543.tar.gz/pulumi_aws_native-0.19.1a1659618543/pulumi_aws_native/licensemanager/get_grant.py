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
    'GetGrantResult',
    'AwaitableGetGrantResult',
    'get_grant',
    'get_grant_output',
]

@pulumi.output_type
class GetGrantResult:
    def __init__(__self__, grant_arn=None, grant_name=None, home_region=None, license_arn=None, status=None, version=None):
        if grant_arn and not isinstance(grant_arn, str):
            raise TypeError("Expected argument 'grant_arn' to be a str")
        pulumi.set(__self__, "grant_arn", grant_arn)
        if grant_name and not isinstance(grant_name, str):
            raise TypeError("Expected argument 'grant_name' to be a str")
        pulumi.set(__self__, "grant_name", grant_name)
        if home_region and not isinstance(home_region, str):
            raise TypeError("Expected argument 'home_region' to be a str")
        pulumi.set(__self__, "home_region", home_region)
        if license_arn and not isinstance(license_arn, str):
            raise TypeError("Expected argument 'license_arn' to be a str")
        pulumi.set(__self__, "license_arn", license_arn)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)
        if version and not isinstance(version, str):
            raise TypeError("Expected argument 'version' to be a str")
        pulumi.set(__self__, "version", version)

    @property
    @pulumi.getter(name="grantArn")
    def grant_arn(self) -> Optional[str]:
        """
        Arn of the grant.
        """
        return pulumi.get(self, "grant_arn")

    @property
    @pulumi.getter(name="grantName")
    def grant_name(self) -> Optional[str]:
        """
        Name for the created Grant.
        """
        return pulumi.get(self, "grant_name")

    @property
    @pulumi.getter(name="homeRegion")
    def home_region(self) -> Optional[str]:
        """
        Home region for the created grant.
        """
        return pulumi.get(self, "home_region")

    @property
    @pulumi.getter(name="licenseArn")
    def license_arn(self) -> Optional[str]:
        """
        License Arn for the grant.
        """
        return pulumi.get(self, "license_arn")

    @property
    @pulumi.getter
    def status(self) -> Optional[str]:
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def version(self) -> Optional[str]:
        """
        The version of the grant.
        """
        return pulumi.get(self, "version")


class AwaitableGetGrantResult(GetGrantResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetGrantResult(
            grant_arn=self.grant_arn,
            grant_name=self.grant_name,
            home_region=self.home_region,
            license_arn=self.license_arn,
            status=self.status,
            version=self.version)


def get_grant(grant_arn: Optional[str] = None,
              opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetGrantResult:
    """
    An example resource schema demonstrating some basic constructs and validation rules.


    :param str grant_arn: Arn of the grant.
    """
    __args__ = dict()
    __args__['grantArn'] = grant_arn
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws-native:licensemanager:getGrant', __args__, opts=opts, typ=GetGrantResult).value

    return AwaitableGetGrantResult(
        grant_arn=__ret__.grant_arn,
        grant_name=__ret__.grant_name,
        home_region=__ret__.home_region,
        license_arn=__ret__.license_arn,
        status=__ret__.status,
        version=__ret__.version)


@_utilities.lift_output_func(get_grant)
def get_grant_output(grant_arn: Optional[pulumi.Input[str]] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetGrantResult]:
    """
    An example resource schema demonstrating some basic constructs and validation rules.


    :param str grant_arn: Arn of the grant.
    """
    ...
