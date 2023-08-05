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
from ._inputs import *

__all__ = ['LicenseArgs', 'License']

@pulumi.input_type
class LicenseArgs:
    def __init__(__self__, *,
                 consumption_configuration: pulumi.Input['LicenseConsumptionConfigurationArgs'],
                 entitlements: pulumi.Input[Sequence[pulumi.Input['LicenseEntitlementArgs']]],
                 home_region: pulumi.Input[str],
                 issuer: pulumi.Input['LicenseIssuerDataArgs'],
                 product_name: pulumi.Input[str],
                 validity: pulumi.Input['LicenseValidityDateFormatArgs'],
                 beneficiary: Optional[pulumi.Input[str]] = None,
                 license_metadata: Optional[pulumi.Input[Sequence[pulumi.Input['LicenseMetadataArgs']]]] = None,
                 license_name: Optional[pulumi.Input[str]] = None,
                 product_sku: Optional[pulumi.Input[str]] = None,
                 status: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a License resource.
        :param pulumi.Input[str] home_region: Home region for the created license.
        :param pulumi.Input[str] product_name: Product name for the created license.
        :param pulumi.Input[str] beneficiary: Beneficiary of the license.
        :param pulumi.Input[str] license_name: Name for the created license.
        :param pulumi.Input[str] product_sku: ProductSKU of the license.
        """
        pulumi.set(__self__, "consumption_configuration", consumption_configuration)
        pulumi.set(__self__, "entitlements", entitlements)
        pulumi.set(__self__, "home_region", home_region)
        pulumi.set(__self__, "issuer", issuer)
        pulumi.set(__self__, "product_name", product_name)
        pulumi.set(__self__, "validity", validity)
        if beneficiary is not None:
            pulumi.set(__self__, "beneficiary", beneficiary)
        if license_metadata is not None:
            pulumi.set(__self__, "license_metadata", license_metadata)
        if license_name is not None:
            pulumi.set(__self__, "license_name", license_name)
        if product_sku is not None:
            pulumi.set(__self__, "product_sku", product_sku)
        if status is not None:
            pulumi.set(__self__, "status", status)

    @property
    @pulumi.getter(name="consumptionConfiguration")
    def consumption_configuration(self) -> pulumi.Input['LicenseConsumptionConfigurationArgs']:
        return pulumi.get(self, "consumption_configuration")

    @consumption_configuration.setter
    def consumption_configuration(self, value: pulumi.Input['LicenseConsumptionConfigurationArgs']):
        pulumi.set(self, "consumption_configuration", value)

    @property
    @pulumi.getter
    def entitlements(self) -> pulumi.Input[Sequence[pulumi.Input['LicenseEntitlementArgs']]]:
        return pulumi.get(self, "entitlements")

    @entitlements.setter
    def entitlements(self, value: pulumi.Input[Sequence[pulumi.Input['LicenseEntitlementArgs']]]):
        pulumi.set(self, "entitlements", value)

    @property
    @pulumi.getter(name="homeRegion")
    def home_region(self) -> pulumi.Input[str]:
        """
        Home region for the created license.
        """
        return pulumi.get(self, "home_region")

    @home_region.setter
    def home_region(self, value: pulumi.Input[str]):
        pulumi.set(self, "home_region", value)

    @property
    @pulumi.getter
    def issuer(self) -> pulumi.Input['LicenseIssuerDataArgs']:
        return pulumi.get(self, "issuer")

    @issuer.setter
    def issuer(self, value: pulumi.Input['LicenseIssuerDataArgs']):
        pulumi.set(self, "issuer", value)

    @property
    @pulumi.getter(name="productName")
    def product_name(self) -> pulumi.Input[str]:
        """
        Product name for the created license.
        """
        return pulumi.get(self, "product_name")

    @product_name.setter
    def product_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "product_name", value)

    @property
    @pulumi.getter
    def validity(self) -> pulumi.Input['LicenseValidityDateFormatArgs']:
        return pulumi.get(self, "validity")

    @validity.setter
    def validity(self, value: pulumi.Input['LicenseValidityDateFormatArgs']):
        pulumi.set(self, "validity", value)

    @property
    @pulumi.getter
    def beneficiary(self) -> Optional[pulumi.Input[str]]:
        """
        Beneficiary of the license.
        """
        return pulumi.get(self, "beneficiary")

    @beneficiary.setter
    def beneficiary(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "beneficiary", value)

    @property
    @pulumi.getter(name="licenseMetadata")
    def license_metadata(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['LicenseMetadataArgs']]]]:
        return pulumi.get(self, "license_metadata")

    @license_metadata.setter
    def license_metadata(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['LicenseMetadataArgs']]]]):
        pulumi.set(self, "license_metadata", value)

    @property
    @pulumi.getter(name="licenseName")
    def license_name(self) -> Optional[pulumi.Input[str]]:
        """
        Name for the created license.
        """
        return pulumi.get(self, "license_name")

    @license_name.setter
    def license_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "license_name", value)

    @property
    @pulumi.getter(name="productSKU")
    def product_sku(self) -> Optional[pulumi.Input[str]]:
        """
        ProductSKU of the license.
        """
        return pulumi.get(self, "product_sku")

    @product_sku.setter
    def product_sku(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "product_sku", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "status", value)


class License(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 beneficiary: Optional[pulumi.Input[str]] = None,
                 consumption_configuration: Optional[pulumi.Input[pulumi.InputType['LicenseConsumptionConfigurationArgs']]] = None,
                 entitlements: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['LicenseEntitlementArgs']]]]] = None,
                 home_region: Optional[pulumi.Input[str]] = None,
                 issuer: Optional[pulumi.Input[pulumi.InputType['LicenseIssuerDataArgs']]] = None,
                 license_metadata: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['LicenseMetadataArgs']]]]] = None,
                 license_name: Optional[pulumi.Input[str]] = None,
                 product_name: Optional[pulumi.Input[str]] = None,
                 product_sku: Optional[pulumi.Input[str]] = None,
                 status: Optional[pulumi.Input[str]] = None,
                 validity: Optional[pulumi.Input[pulumi.InputType['LicenseValidityDateFormatArgs']]] = None,
                 __props__=None):
        """
        Resource Type definition for AWS::LicenseManager::License

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] beneficiary: Beneficiary of the license.
        :param pulumi.Input[str] home_region: Home region for the created license.
        :param pulumi.Input[str] license_name: Name for the created license.
        :param pulumi.Input[str] product_name: Product name for the created license.
        :param pulumi.Input[str] product_sku: ProductSKU of the license.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: LicenseArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource Type definition for AWS::LicenseManager::License

        :param str resource_name: The name of the resource.
        :param LicenseArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(LicenseArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 beneficiary: Optional[pulumi.Input[str]] = None,
                 consumption_configuration: Optional[pulumi.Input[pulumi.InputType['LicenseConsumptionConfigurationArgs']]] = None,
                 entitlements: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['LicenseEntitlementArgs']]]]] = None,
                 home_region: Optional[pulumi.Input[str]] = None,
                 issuer: Optional[pulumi.Input[pulumi.InputType['LicenseIssuerDataArgs']]] = None,
                 license_metadata: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['LicenseMetadataArgs']]]]] = None,
                 license_name: Optional[pulumi.Input[str]] = None,
                 product_name: Optional[pulumi.Input[str]] = None,
                 product_sku: Optional[pulumi.Input[str]] = None,
                 status: Optional[pulumi.Input[str]] = None,
                 validity: Optional[pulumi.Input[pulumi.InputType['LicenseValidityDateFormatArgs']]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = LicenseArgs.__new__(LicenseArgs)

            __props__.__dict__["beneficiary"] = beneficiary
            if consumption_configuration is None and not opts.urn:
                raise TypeError("Missing required property 'consumption_configuration'")
            __props__.__dict__["consumption_configuration"] = consumption_configuration
            if entitlements is None and not opts.urn:
                raise TypeError("Missing required property 'entitlements'")
            __props__.__dict__["entitlements"] = entitlements
            if home_region is None and not opts.urn:
                raise TypeError("Missing required property 'home_region'")
            __props__.__dict__["home_region"] = home_region
            if issuer is None and not opts.urn:
                raise TypeError("Missing required property 'issuer'")
            __props__.__dict__["issuer"] = issuer
            __props__.__dict__["license_metadata"] = license_metadata
            __props__.__dict__["license_name"] = license_name
            if product_name is None and not opts.urn:
                raise TypeError("Missing required property 'product_name'")
            __props__.__dict__["product_name"] = product_name
            __props__.__dict__["product_sku"] = product_sku
            __props__.__dict__["status"] = status
            if validity is None and not opts.urn:
                raise TypeError("Missing required property 'validity'")
            __props__.__dict__["validity"] = validity
            __props__.__dict__["license_arn"] = None
            __props__.__dict__["version"] = None
        super(License, __self__).__init__(
            'aws-native:licensemanager:License',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'License':
        """
        Get an existing License resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = LicenseArgs.__new__(LicenseArgs)

        __props__.__dict__["beneficiary"] = None
        __props__.__dict__["consumption_configuration"] = None
        __props__.__dict__["entitlements"] = None
        __props__.__dict__["home_region"] = None
        __props__.__dict__["issuer"] = None
        __props__.__dict__["license_arn"] = None
        __props__.__dict__["license_metadata"] = None
        __props__.__dict__["license_name"] = None
        __props__.__dict__["product_name"] = None
        __props__.__dict__["product_sku"] = None
        __props__.__dict__["status"] = None
        __props__.__dict__["validity"] = None
        __props__.__dict__["version"] = None
        return License(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def beneficiary(self) -> pulumi.Output[Optional[str]]:
        """
        Beneficiary of the license.
        """
        return pulumi.get(self, "beneficiary")

    @property
    @pulumi.getter(name="consumptionConfiguration")
    def consumption_configuration(self) -> pulumi.Output['outputs.LicenseConsumptionConfiguration']:
        return pulumi.get(self, "consumption_configuration")

    @property
    @pulumi.getter
    def entitlements(self) -> pulumi.Output[Sequence['outputs.LicenseEntitlement']]:
        return pulumi.get(self, "entitlements")

    @property
    @pulumi.getter(name="homeRegion")
    def home_region(self) -> pulumi.Output[str]:
        """
        Home region for the created license.
        """
        return pulumi.get(self, "home_region")

    @property
    @pulumi.getter
    def issuer(self) -> pulumi.Output['outputs.LicenseIssuerData']:
        return pulumi.get(self, "issuer")

    @property
    @pulumi.getter(name="licenseArn")
    def license_arn(self) -> pulumi.Output[str]:
        """
        Amazon Resource Name is a unique name for each resource.
        """
        return pulumi.get(self, "license_arn")

    @property
    @pulumi.getter(name="licenseMetadata")
    def license_metadata(self) -> pulumi.Output[Optional[Sequence['outputs.LicenseMetadata']]]:
        return pulumi.get(self, "license_metadata")

    @property
    @pulumi.getter(name="licenseName")
    def license_name(self) -> pulumi.Output[str]:
        """
        Name for the created license.
        """
        return pulumi.get(self, "license_name")

    @property
    @pulumi.getter(name="productName")
    def product_name(self) -> pulumi.Output[str]:
        """
        Product name for the created license.
        """
        return pulumi.get(self, "product_name")

    @property
    @pulumi.getter(name="productSKU")
    def product_sku(self) -> pulumi.Output[Optional[str]]:
        """
        ProductSKU of the license.
        """
        return pulumi.get(self, "product_sku")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def validity(self) -> pulumi.Output['outputs.LicenseValidityDateFormat']:
        return pulumi.get(self, "validity")

    @property
    @pulumi.getter
    def version(self) -> pulumi.Output[str]:
        """
        The version of the license.
        """
        return pulumi.get(self, "version")

