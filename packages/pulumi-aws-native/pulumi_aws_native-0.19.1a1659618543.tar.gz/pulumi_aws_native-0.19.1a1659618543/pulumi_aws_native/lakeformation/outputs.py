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
    'DataLakeSettingsAdmins',
    'PermissionsColumnWildcard',
    'PermissionsDataLakePrincipal',
    'PermissionsDataLocationResource',
    'PermissionsDatabaseResource',
    'PermissionsResource',
    'PermissionsTableResource',
    'PermissionsTableWildcard',
    'PermissionsTableWithColumnsResource',
]

@pulumi.output_type
class DataLakeSettingsAdmins(dict):
    def __init__(__self__):
        pass


@pulumi.output_type
class PermissionsColumnWildcard(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "excludedColumnNames":
            suggest = "excluded_column_names"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PermissionsColumnWildcard. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PermissionsColumnWildcard.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PermissionsColumnWildcard.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 excluded_column_names: Optional[Sequence[str]] = None):
        if excluded_column_names is not None:
            pulumi.set(__self__, "excluded_column_names", excluded_column_names)

    @property
    @pulumi.getter(name="excludedColumnNames")
    def excluded_column_names(self) -> Optional[Sequence[str]]:
        return pulumi.get(self, "excluded_column_names")


@pulumi.output_type
class PermissionsDataLakePrincipal(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "dataLakePrincipalIdentifier":
            suggest = "data_lake_principal_identifier"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PermissionsDataLakePrincipal. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PermissionsDataLakePrincipal.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PermissionsDataLakePrincipal.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 data_lake_principal_identifier: Optional[str] = None):
        if data_lake_principal_identifier is not None:
            pulumi.set(__self__, "data_lake_principal_identifier", data_lake_principal_identifier)

    @property
    @pulumi.getter(name="dataLakePrincipalIdentifier")
    def data_lake_principal_identifier(self) -> Optional[str]:
        return pulumi.get(self, "data_lake_principal_identifier")


@pulumi.output_type
class PermissionsDataLocationResource(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "catalogId":
            suggest = "catalog_id"
        elif key == "s3Resource":
            suggest = "s3_resource"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PermissionsDataLocationResource. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PermissionsDataLocationResource.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PermissionsDataLocationResource.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 catalog_id: Optional[str] = None,
                 s3_resource: Optional[str] = None):
        if catalog_id is not None:
            pulumi.set(__self__, "catalog_id", catalog_id)
        if s3_resource is not None:
            pulumi.set(__self__, "s3_resource", s3_resource)

    @property
    @pulumi.getter(name="catalogId")
    def catalog_id(self) -> Optional[str]:
        return pulumi.get(self, "catalog_id")

    @property
    @pulumi.getter(name="s3Resource")
    def s3_resource(self) -> Optional[str]:
        return pulumi.get(self, "s3_resource")


@pulumi.output_type
class PermissionsDatabaseResource(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "catalogId":
            suggest = "catalog_id"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PermissionsDatabaseResource. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PermissionsDatabaseResource.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PermissionsDatabaseResource.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 catalog_id: Optional[str] = None,
                 name: Optional[str] = None):
        if catalog_id is not None:
            pulumi.set(__self__, "catalog_id", catalog_id)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter(name="catalogId")
    def catalog_id(self) -> Optional[str]:
        return pulumi.get(self, "catalog_id")

    @property
    @pulumi.getter
    def name(self) -> Optional[str]:
        return pulumi.get(self, "name")


@pulumi.output_type
class PermissionsResource(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "dataLocationResource":
            suggest = "data_location_resource"
        elif key == "databaseResource":
            suggest = "database_resource"
        elif key == "tableResource":
            suggest = "table_resource"
        elif key == "tableWithColumnsResource":
            suggest = "table_with_columns_resource"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PermissionsResource. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PermissionsResource.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PermissionsResource.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 data_location_resource: Optional['outputs.PermissionsDataLocationResource'] = None,
                 database_resource: Optional['outputs.PermissionsDatabaseResource'] = None,
                 table_resource: Optional['outputs.PermissionsTableResource'] = None,
                 table_with_columns_resource: Optional['outputs.PermissionsTableWithColumnsResource'] = None):
        if data_location_resource is not None:
            pulumi.set(__self__, "data_location_resource", data_location_resource)
        if database_resource is not None:
            pulumi.set(__self__, "database_resource", database_resource)
        if table_resource is not None:
            pulumi.set(__self__, "table_resource", table_resource)
        if table_with_columns_resource is not None:
            pulumi.set(__self__, "table_with_columns_resource", table_with_columns_resource)

    @property
    @pulumi.getter(name="dataLocationResource")
    def data_location_resource(self) -> Optional['outputs.PermissionsDataLocationResource']:
        return pulumi.get(self, "data_location_resource")

    @property
    @pulumi.getter(name="databaseResource")
    def database_resource(self) -> Optional['outputs.PermissionsDatabaseResource']:
        return pulumi.get(self, "database_resource")

    @property
    @pulumi.getter(name="tableResource")
    def table_resource(self) -> Optional['outputs.PermissionsTableResource']:
        return pulumi.get(self, "table_resource")

    @property
    @pulumi.getter(name="tableWithColumnsResource")
    def table_with_columns_resource(self) -> Optional['outputs.PermissionsTableWithColumnsResource']:
        return pulumi.get(self, "table_with_columns_resource")


@pulumi.output_type
class PermissionsTableResource(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "catalogId":
            suggest = "catalog_id"
        elif key == "databaseName":
            suggest = "database_name"
        elif key == "tableWildcard":
            suggest = "table_wildcard"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PermissionsTableResource. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PermissionsTableResource.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PermissionsTableResource.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 catalog_id: Optional[str] = None,
                 database_name: Optional[str] = None,
                 name: Optional[str] = None,
                 table_wildcard: Optional['outputs.PermissionsTableWildcard'] = None):
        if catalog_id is not None:
            pulumi.set(__self__, "catalog_id", catalog_id)
        if database_name is not None:
            pulumi.set(__self__, "database_name", database_name)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if table_wildcard is not None:
            pulumi.set(__self__, "table_wildcard", table_wildcard)

    @property
    @pulumi.getter(name="catalogId")
    def catalog_id(self) -> Optional[str]:
        return pulumi.get(self, "catalog_id")

    @property
    @pulumi.getter(name="databaseName")
    def database_name(self) -> Optional[str]:
        return pulumi.get(self, "database_name")

    @property
    @pulumi.getter
    def name(self) -> Optional[str]:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="tableWildcard")
    def table_wildcard(self) -> Optional['outputs.PermissionsTableWildcard']:
        return pulumi.get(self, "table_wildcard")


@pulumi.output_type
class PermissionsTableWildcard(dict):
    def __init__(__self__):
        pass


@pulumi.output_type
class PermissionsTableWithColumnsResource(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "catalogId":
            suggest = "catalog_id"
        elif key == "columnNames":
            suggest = "column_names"
        elif key == "columnWildcard":
            suggest = "column_wildcard"
        elif key == "databaseName":
            suggest = "database_name"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in PermissionsTableWithColumnsResource. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        PermissionsTableWithColumnsResource.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        PermissionsTableWithColumnsResource.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 catalog_id: Optional[str] = None,
                 column_names: Optional[Sequence[str]] = None,
                 column_wildcard: Optional['outputs.PermissionsColumnWildcard'] = None,
                 database_name: Optional[str] = None,
                 name: Optional[str] = None):
        if catalog_id is not None:
            pulumi.set(__self__, "catalog_id", catalog_id)
        if column_names is not None:
            pulumi.set(__self__, "column_names", column_names)
        if column_wildcard is not None:
            pulumi.set(__self__, "column_wildcard", column_wildcard)
        if database_name is not None:
            pulumi.set(__self__, "database_name", database_name)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter(name="catalogId")
    def catalog_id(self) -> Optional[str]:
        return pulumi.get(self, "catalog_id")

    @property
    @pulumi.getter(name="columnNames")
    def column_names(self) -> Optional[Sequence[str]]:
        return pulumi.get(self, "column_names")

    @property
    @pulumi.getter(name="columnWildcard")
    def column_wildcard(self) -> Optional['outputs.PermissionsColumnWildcard']:
        return pulumi.get(self, "column_wildcard")

    @property
    @pulumi.getter(name="databaseName")
    def database_name(self) -> Optional[str]:
        return pulumi.get(self, "database_name")

    @property
    @pulumi.getter
    def name(self) -> Optional[str]:
        return pulumi.get(self, "name")


