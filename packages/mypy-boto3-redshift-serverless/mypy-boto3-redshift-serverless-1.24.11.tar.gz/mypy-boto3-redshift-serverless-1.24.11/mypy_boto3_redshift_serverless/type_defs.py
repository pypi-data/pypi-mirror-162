"""
Type annotations for redshiftserverless service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_redshift_serverless/type_defs/)

Usage::

    ```python
    from mypy_boto3_redshift_serverless.type_defs import ConfigParameterTypeDef

    data: ConfigParameterTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Sequence, Union

from .literals import (
    LogExportType,
    NamespaceStatusType,
    SnapshotStatusType,
    UsageLimitBreachActionType,
    UsageLimitPeriodType,
    UsageLimitUsageTypeType,
    WorkgroupStatusType,
)

if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "ConfigParameterTypeDef",
    "ConvertRecoveryPointToSnapshotRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "SnapshotTypeDef",
    "CreateEndpointAccessRequestRequestTypeDef",
    "TagTypeDef",
    "NamespaceTypeDef",
    "CreateSnapshotRequestRequestTypeDef",
    "CreateUsageLimitRequestRequestTypeDef",
    "UsageLimitTypeDef",
    "DeleteEndpointAccessRequestRequestTypeDef",
    "DeleteNamespaceRequestRequestTypeDef",
    "DeleteResourcePolicyRequestRequestTypeDef",
    "DeleteSnapshotRequestRequestTypeDef",
    "DeleteUsageLimitRequestRequestTypeDef",
    "DeleteWorkgroupRequestRequestTypeDef",
    "VpcSecurityGroupMembershipTypeDef",
    "GetCredentialsRequestRequestTypeDef",
    "GetEndpointAccessRequestRequestTypeDef",
    "GetNamespaceRequestRequestTypeDef",
    "GetRecoveryPointRequestRequestTypeDef",
    "RecoveryPointTypeDef",
    "GetResourcePolicyRequestRequestTypeDef",
    "ResourcePolicyTypeDef",
    "GetSnapshotRequestRequestTypeDef",
    "GetUsageLimitRequestRequestTypeDef",
    "GetWorkgroupRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "ListEndpointAccessRequestRequestTypeDef",
    "ListNamespacesRequestRequestTypeDef",
    "ListRecoveryPointsRequestRequestTypeDef",
    "ListSnapshotsRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListUsageLimitsRequestRequestTypeDef",
    "ListWorkgroupsRequestRequestTypeDef",
    "NetworkInterfaceTypeDef",
    "PutResourcePolicyRequestRequestTypeDef",
    "RestoreFromRecoveryPointRequestRequestTypeDef",
    "RestoreFromSnapshotRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateEndpointAccessRequestRequestTypeDef",
    "UpdateNamespaceRequestRequestTypeDef",
    "UpdateSnapshotRequestRequestTypeDef",
    "UpdateUsageLimitRequestRequestTypeDef",
    "UpdateWorkgroupRequestRequestTypeDef",
    "GetCredentialsResponseTypeDef",
    "ConvertRecoveryPointToSnapshotResponseTypeDef",
    "CreateSnapshotResponseTypeDef",
    "DeleteSnapshotResponseTypeDef",
    "GetSnapshotResponseTypeDef",
    "ListSnapshotsResponseTypeDef",
    "UpdateSnapshotResponseTypeDef",
    "CreateNamespaceRequestRequestTypeDef",
    "CreateWorkgroupRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreateNamespaceResponseTypeDef",
    "DeleteNamespaceResponseTypeDef",
    "GetNamespaceResponseTypeDef",
    "ListNamespacesResponseTypeDef",
    "RestoreFromRecoveryPointResponseTypeDef",
    "RestoreFromSnapshotResponseTypeDef",
    "UpdateNamespaceResponseTypeDef",
    "CreateUsageLimitResponseTypeDef",
    "DeleteUsageLimitResponseTypeDef",
    "GetUsageLimitResponseTypeDef",
    "ListUsageLimitsResponseTypeDef",
    "UpdateUsageLimitResponseTypeDef",
    "GetRecoveryPointResponseTypeDef",
    "ListRecoveryPointsResponseTypeDef",
    "GetResourcePolicyResponseTypeDef",
    "PutResourcePolicyResponseTypeDef",
    "ListEndpointAccessRequestListEndpointAccessPaginateTypeDef",
    "ListNamespacesRequestListNamespacesPaginateTypeDef",
    "ListRecoveryPointsRequestListRecoveryPointsPaginateTypeDef",
    "ListSnapshotsRequestListSnapshotsPaginateTypeDef",
    "ListUsageLimitsRequestListUsageLimitsPaginateTypeDef",
    "ListWorkgroupsRequestListWorkgroupsPaginateTypeDef",
    "VpcEndpointTypeDef",
    "EndpointAccessTypeDef",
    "EndpointTypeDef",
    "CreateEndpointAccessResponseTypeDef",
    "DeleteEndpointAccessResponseTypeDef",
    "GetEndpointAccessResponseTypeDef",
    "ListEndpointAccessResponseTypeDef",
    "UpdateEndpointAccessResponseTypeDef",
    "WorkgroupTypeDef",
    "CreateWorkgroupResponseTypeDef",
    "DeleteWorkgroupResponseTypeDef",
    "GetWorkgroupResponseTypeDef",
    "ListWorkgroupsResponseTypeDef",
    "UpdateWorkgroupResponseTypeDef",
)

ConfigParameterTypeDef = TypedDict(
    "ConfigParameterTypeDef",
    {
        "parameterKey": str,
        "parameterValue": str,
    },
    total=False,
)

_RequiredConvertRecoveryPointToSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredConvertRecoveryPointToSnapshotRequestRequestTypeDef",
    {
        "recoveryPointId": str,
        "snapshotName": str,
    },
)
_OptionalConvertRecoveryPointToSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalConvertRecoveryPointToSnapshotRequestRequestTypeDef",
    {
        "retentionPeriod": int,
    },
    total=False,
)


class ConvertRecoveryPointToSnapshotRequestRequestTypeDef(
    _RequiredConvertRecoveryPointToSnapshotRequestRequestTypeDef,
    _OptionalConvertRecoveryPointToSnapshotRequestRequestTypeDef,
):
    pass


ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

SnapshotTypeDef = TypedDict(
    "SnapshotTypeDef",
    {
        "accountsWithProvisionedRestoreAccess": List[str],
        "accountsWithRestoreAccess": List[str],
        "actualIncrementalBackupSizeInMegaBytes": float,
        "adminUsername": str,
        "backupProgressInMegaBytes": float,
        "currentBackupRateInMegaBytesPerSecond": float,
        "elapsedTimeInSeconds": int,
        "estimatedSecondsToCompletion": int,
        "kmsKeyId": str,
        "namespaceArn": str,
        "namespaceName": str,
        "ownerAccount": str,
        "snapshotArn": str,
        "snapshotCreateTime": datetime,
        "snapshotName": str,
        "snapshotRemainingDays": int,
        "snapshotRetentionPeriod": int,
        "snapshotRetentionStartTime": datetime,
        "status": SnapshotStatusType,
        "totalBackupSizeInMegaBytes": float,
    },
    total=False,
)

_RequiredCreateEndpointAccessRequestRequestTypeDef = TypedDict(
    "_RequiredCreateEndpointAccessRequestRequestTypeDef",
    {
        "endpointName": str,
        "subnetIds": Sequence[str],
        "workgroupName": str,
    },
)
_OptionalCreateEndpointAccessRequestRequestTypeDef = TypedDict(
    "_OptionalCreateEndpointAccessRequestRequestTypeDef",
    {
        "vpcSecurityGroupIds": Sequence[str],
    },
    total=False,
)


class CreateEndpointAccessRequestRequestTypeDef(
    _RequiredCreateEndpointAccessRequestRequestTypeDef,
    _OptionalCreateEndpointAccessRequestRequestTypeDef,
):
    pass


TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "key": str,
        "value": str,
    },
)

NamespaceTypeDef = TypedDict(
    "NamespaceTypeDef",
    {
        "adminUsername": str,
        "creationDate": datetime,
        "dbName": str,
        "defaultIamRoleArn": str,
        "iamRoles": List[str],
        "kmsKeyId": str,
        "logExports": List[LogExportType],
        "namespaceArn": str,
        "namespaceId": str,
        "namespaceName": str,
        "status": NamespaceStatusType,
    },
    total=False,
)

_RequiredCreateSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSnapshotRequestRequestTypeDef",
    {
        "namespaceName": str,
        "snapshotName": str,
    },
)
_OptionalCreateSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSnapshotRequestRequestTypeDef",
    {
        "retentionPeriod": int,
    },
    total=False,
)


class CreateSnapshotRequestRequestTypeDef(
    _RequiredCreateSnapshotRequestRequestTypeDef, _OptionalCreateSnapshotRequestRequestTypeDef
):
    pass


_RequiredCreateUsageLimitRequestRequestTypeDef = TypedDict(
    "_RequiredCreateUsageLimitRequestRequestTypeDef",
    {
        "amount": int,
        "resourceArn": str,
        "usageType": UsageLimitUsageTypeType,
    },
)
_OptionalCreateUsageLimitRequestRequestTypeDef = TypedDict(
    "_OptionalCreateUsageLimitRequestRequestTypeDef",
    {
        "breachAction": UsageLimitBreachActionType,
        "period": UsageLimitPeriodType,
    },
    total=False,
)


class CreateUsageLimitRequestRequestTypeDef(
    _RequiredCreateUsageLimitRequestRequestTypeDef, _OptionalCreateUsageLimitRequestRequestTypeDef
):
    pass


UsageLimitTypeDef = TypedDict(
    "UsageLimitTypeDef",
    {
        "amount": int,
        "breachAction": UsageLimitBreachActionType,
        "period": UsageLimitPeriodType,
        "resourceArn": str,
        "usageLimitArn": str,
        "usageLimitId": str,
        "usageType": UsageLimitUsageTypeType,
    },
    total=False,
)

DeleteEndpointAccessRequestRequestTypeDef = TypedDict(
    "DeleteEndpointAccessRequestRequestTypeDef",
    {
        "endpointName": str,
    },
)

_RequiredDeleteNamespaceRequestRequestTypeDef = TypedDict(
    "_RequiredDeleteNamespaceRequestRequestTypeDef",
    {
        "namespaceName": str,
    },
)
_OptionalDeleteNamespaceRequestRequestTypeDef = TypedDict(
    "_OptionalDeleteNamespaceRequestRequestTypeDef",
    {
        "finalSnapshotName": str,
        "finalSnapshotRetentionPeriod": int,
    },
    total=False,
)


class DeleteNamespaceRequestRequestTypeDef(
    _RequiredDeleteNamespaceRequestRequestTypeDef, _OptionalDeleteNamespaceRequestRequestTypeDef
):
    pass


DeleteResourcePolicyRequestRequestTypeDef = TypedDict(
    "DeleteResourcePolicyRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

DeleteSnapshotRequestRequestTypeDef = TypedDict(
    "DeleteSnapshotRequestRequestTypeDef",
    {
        "snapshotName": str,
    },
)

DeleteUsageLimitRequestRequestTypeDef = TypedDict(
    "DeleteUsageLimitRequestRequestTypeDef",
    {
        "usageLimitId": str,
    },
)

DeleteWorkgroupRequestRequestTypeDef = TypedDict(
    "DeleteWorkgroupRequestRequestTypeDef",
    {
        "workgroupName": str,
    },
)

VpcSecurityGroupMembershipTypeDef = TypedDict(
    "VpcSecurityGroupMembershipTypeDef",
    {
        "status": str,
        "vpcSecurityGroupId": str,
    },
    total=False,
)

_RequiredGetCredentialsRequestRequestTypeDef = TypedDict(
    "_RequiredGetCredentialsRequestRequestTypeDef",
    {
        "workgroupName": str,
    },
)
_OptionalGetCredentialsRequestRequestTypeDef = TypedDict(
    "_OptionalGetCredentialsRequestRequestTypeDef",
    {
        "dbName": str,
        "durationSeconds": int,
    },
    total=False,
)


class GetCredentialsRequestRequestTypeDef(
    _RequiredGetCredentialsRequestRequestTypeDef, _OptionalGetCredentialsRequestRequestTypeDef
):
    pass


GetEndpointAccessRequestRequestTypeDef = TypedDict(
    "GetEndpointAccessRequestRequestTypeDef",
    {
        "endpointName": str,
    },
)

GetNamespaceRequestRequestTypeDef = TypedDict(
    "GetNamespaceRequestRequestTypeDef",
    {
        "namespaceName": str,
    },
)

GetRecoveryPointRequestRequestTypeDef = TypedDict(
    "GetRecoveryPointRequestRequestTypeDef",
    {
        "recoveryPointId": str,
    },
)

RecoveryPointTypeDef = TypedDict(
    "RecoveryPointTypeDef",
    {
        "namespaceName": str,
        "recoveryPointCreateTime": datetime,
        "recoveryPointId": str,
        "totalSizeInMegaBytes": float,
        "workgroupName": str,
    },
    total=False,
)

GetResourcePolicyRequestRequestTypeDef = TypedDict(
    "GetResourcePolicyRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

ResourcePolicyTypeDef = TypedDict(
    "ResourcePolicyTypeDef",
    {
        "policy": str,
        "resourceArn": str,
    },
    total=False,
)

GetSnapshotRequestRequestTypeDef = TypedDict(
    "GetSnapshotRequestRequestTypeDef",
    {
        "ownerAccount": str,
        "snapshotArn": str,
        "snapshotName": str,
    },
    total=False,
)

GetUsageLimitRequestRequestTypeDef = TypedDict(
    "GetUsageLimitRequestRequestTypeDef",
    {
        "usageLimitId": str,
    },
)

GetWorkgroupRequestRequestTypeDef = TypedDict(
    "GetWorkgroupRequestRequestTypeDef",
    {
        "workgroupName": str,
    },
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": int,
        "PageSize": int,
        "StartingToken": str,
    },
    total=False,
)

ListEndpointAccessRequestRequestTypeDef = TypedDict(
    "ListEndpointAccessRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
        "vpcId": str,
        "workgroupName": str,
    },
    total=False,
)

ListNamespacesRequestRequestTypeDef = TypedDict(
    "ListNamespacesRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

ListRecoveryPointsRequestRequestTypeDef = TypedDict(
    "ListRecoveryPointsRequestRequestTypeDef",
    {
        "endTime": Union[datetime, str],
        "maxResults": int,
        "namespaceName": str,
        "nextToken": str,
        "startTime": Union[datetime, str],
    },
    total=False,
)

ListSnapshotsRequestRequestTypeDef = TypedDict(
    "ListSnapshotsRequestRequestTypeDef",
    {
        "endTime": Union[datetime, str],
        "maxResults": int,
        "namespaceArn": str,
        "namespaceName": str,
        "nextToken": str,
        "ownerAccount": str,
        "startTime": Union[datetime, str],
    },
    total=False,
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

ListUsageLimitsRequestRequestTypeDef = TypedDict(
    "ListUsageLimitsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
        "resourceArn": str,
        "usageType": UsageLimitUsageTypeType,
    },
    total=False,
)

ListWorkgroupsRequestRequestTypeDef = TypedDict(
    "ListWorkgroupsRequestRequestTypeDef",
    {
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

NetworkInterfaceTypeDef = TypedDict(
    "NetworkInterfaceTypeDef",
    {
        "availabilityZone": str,
        "networkInterfaceId": str,
        "privateIpAddress": str,
        "subnetId": str,
    },
    total=False,
)

PutResourcePolicyRequestRequestTypeDef = TypedDict(
    "PutResourcePolicyRequestRequestTypeDef",
    {
        "policy": str,
        "resourceArn": str,
    },
)

RestoreFromRecoveryPointRequestRequestTypeDef = TypedDict(
    "RestoreFromRecoveryPointRequestRequestTypeDef",
    {
        "namespaceName": str,
        "recoveryPointId": str,
        "workgroupName": str,
    },
)

_RequiredRestoreFromSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredRestoreFromSnapshotRequestRequestTypeDef",
    {
        "namespaceName": str,
        "workgroupName": str,
    },
)
_OptionalRestoreFromSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalRestoreFromSnapshotRequestRequestTypeDef",
    {
        "ownerAccount": str,
        "snapshotArn": str,
        "snapshotName": str,
    },
    total=False,
)


class RestoreFromSnapshotRequestRequestTypeDef(
    _RequiredRestoreFromSnapshotRequestRequestTypeDef,
    _OptionalRestoreFromSnapshotRequestRequestTypeDef,
):
    pass


UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)

_RequiredUpdateEndpointAccessRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateEndpointAccessRequestRequestTypeDef",
    {
        "endpointName": str,
    },
)
_OptionalUpdateEndpointAccessRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateEndpointAccessRequestRequestTypeDef",
    {
        "vpcSecurityGroupIds": Sequence[str],
    },
    total=False,
)


class UpdateEndpointAccessRequestRequestTypeDef(
    _RequiredUpdateEndpointAccessRequestRequestTypeDef,
    _OptionalUpdateEndpointAccessRequestRequestTypeDef,
):
    pass


_RequiredUpdateNamespaceRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateNamespaceRequestRequestTypeDef",
    {
        "namespaceName": str,
    },
)
_OptionalUpdateNamespaceRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateNamespaceRequestRequestTypeDef",
    {
        "adminUserPassword": str,
        "adminUsername": str,
        "defaultIamRoleArn": str,
        "iamRoles": Sequence[str],
        "kmsKeyId": str,
        "logExports": Sequence[LogExportType],
    },
    total=False,
)


class UpdateNamespaceRequestRequestTypeDef(
    _RequiredUpdateNamespaceRequestRequestTypeDef, _OptionalUpdateNamespaceRequestRequestTypeDef
):
    pass


_RequiredUpdateSnapshotRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateSnapshotRequestRequestTypeDef",
    {
        "snapshotName": str,
    },
)
_OptionalUpdateSnapshotRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateSnapshotRequestRequestTypeDef",
    {
        "retentionPeriod": int,
    },
    total=False,
)


class UpdateSnapshotRequestRequestTypeDef(
    _RequiredUpdateSnapshotRequestRequestTypeDef, _OptionalUpdateSnapshotRequestRequestTypeDef
):
    pass


_RequiredUpdateUsageLimitRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateUsageLimitRequestRequestTypeDef",
    {
        "usageLimitId": str,
    },
)
_OptionalUpdateUsageLimitRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateUsageLimitRequestRequestTypeDef",
    {
        "amount": int,
        "breachAction": UsageLimitBreachActionType,
    },
    total=False,
)


class UpdateUsageLimitRequestRequestTypeDef(
    _RequiredUpdateUsageLimitRequestRequestTypeDef, _OptionalUpdateUsageLimitRequestRequestTypeDef
):
    pass


_RequiredUpdateWorkgroupRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateWorkgroupRequestRequestTypeDef",
    {
        "workgroupName": str,
    },
)
_OptionalUpdateWorkgroupRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateWorkgroupRequestRequestTypeDef",
    {
        "baseCapacity": int,
        "configParameters": Sequence[ConfigParameterTypeDef],
        "enhancedVpcRouting": bool,
        "publiclyAccessible": bool,
        "securityGroupIds": Sequence[str],
        "subnetIds": Sequence[str],
    },
    total=False,
)


class UpdateWorkgroupRequestRequestTypeDef(
    _RequiredUpdateWorkgroupRequestRequestTypeDef, _OptionalUpdateWorkgroupRequestRequestTypeDef
):
    pass


GetCredentialsResponseTypeDef = TypedDict(
    "GetCredentialsResponseTypeDef",
    {
        "dbPassword": str,
        "dbUser": str,
        "expiration": datetime,
        "nextRefreshTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ConvertRecoveryPointToSnapshotResponseTypeDef = TypedDict(
    "ConvertRecoveryPointToSnapshotResponseTypeDef",
    {
        "snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSnapshotResponseTypeDef = TypedDict(
    "CreateSnapshotResponseTypeDef",
    {
        "snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteSnapshotResponseTypeDef = TypedDict(
    "DeleteSnapshotResponseTypeDef",
    {
        "snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetSnapshotResponseTypeDef = TypedDict(
    "GetSnapshotResponseTypeDef",
    {
        "snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSnapshotsResponseTypeDef = TypedDict(
    "ListSnapshotsResponseTypeDef",
    {
        "nextToken": str,
        "snapshots": List[SnapshotTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateSnapshotResponseTypeDef = TypedDict(
    "UpdateSnapshotResponseTypeDef",
    {
        "snapshot": SnapshotTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateNamespaceRequestRequestTypeDef = TypedDict(
    "_RequiredCreateNamespaceRequestRequestTypeDef",
    {
        "namespaceName": str,
    },
)
_OptionalCreateNamespaceRequestRequestTypeDef = TypedDict(
    "_OptionalCreateNamespaceRequestRequestTypeDef",
    {
        "adminUserPassword": str,
        "adminUsername": str,
        "dbName": str,
        "defaultIamRoleArn": str,
        "iamRoles": Sequence[str],
        "kmsKeyId": str,
        "logExports": Sequence[LogExportType],
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateNamespaceRequestRequestTypeDef(
    _RequiredCreateNamespaceRequestRequestTypeDef, _OptionalCreateNamespaceRequestRequestTypeDef
):
    pass


_RequiredCreateWorkgroupRequestRequestTypeDef = TypedDict(
    "_RequiredCreateWorkgroupRequestRequestTypeDef",
    {
        "namespaceName": str,
        "workgroupName": str,
    },
)
_OptionalCreateWorkgroupRequestRequestTypeDef = TypedDict(
    "_OptionalCreateWorkgroupRequestRequestTypeDef",
    {
        "baseCapacity": int,
        "configParameters": Sequence[ConfigParameterTypeDef],
        "enhancedVpcRouting": bool,
        "publiclyAccessible": bool,
        "securityGroupIds": Sequence[str],
        "subnetIds": Sequence[str],
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateWorkgroupRequestRequestTypeDef(
    _RequiredCreateWorkgroupRequestRequestTypeDef, _OptionalCreateWorkgroupRequestRequestTypeDef
):
    pass


ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Sequence[TagTypeDef],
    },
)

CreateNamespaceResponseTypeDef = TypedDict(
    "CreateNamespaceResponseTypeDef",
    {
        "namespace": NamespaceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteNamespaceResponseTypeDef = TypedDict(
    "DeleteNamespaceResponseTypeDef",
    {
        "namespace": NamespaceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetNamespaceResponseTypeDef = TypedDict(
    "GetNamespaceResponseTypeDef",
    {
        "namespace": NamespaceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListNamespacesResponseTypeDef = TypedDict(
    "ListNamespacesResponseTypeDef",
    {
        "namespaces": List[NamespaceTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RestoreFromRecoveryPointResponseTypeDef = TypedDict(
    "RestoreFromRecoveryPointResponseTypeDef",
    {
        "namespace": NamespaceTypeDef,
        "recoveryPointId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RestoreFromSnapshotResponseTypeDef = TypedDict(
    "RestoreFromSnapshotResponseTypeDef",
    {
        "namespace": NamespaceTypeDef,
        "ownerAccount": str,
        "snapshotName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateNamespaceResponseTypeDef = TypedDict(
    "UpdateNamespaceResponseTypeDef",
    {
        "namespace": NamespaceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateUsageLimitResponseTypeDef = TypedDict(
    "CreateUsageLimitResponseTypeDef",
    {
        "usageLimit": UsageLimitTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteUsageLimitResponseTypeDef = TypedDict(
    "DeleteUsageLimitResponseTypeDef",
    {
        "usageLimit": UsageLimitTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetUsageLimitResponseTypeDef = TypedDict(
    "GetUsageLimitResponseTypeDef",
    {
        "usageLimit": UsageLimitTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListUsageLimitsResponseTypeDef = TypedDict(
    "ListUsageLimitsResponseTypeDef",
    {
        "nextToken": str,
        "usageLimits": List[UsageLimitTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateUsageLimitResponseTypeDef = TypedDict(
    "UpdateUsageLimitResponseTypeDef",
    {
        "usageLimit": UsageLimitTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetRecoveryPointResponseTypeDef = TypedDict(
    "GetRecoveryPointResponseTypeDef",
    {
        "recoveryPoint": RecoveryPointTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListRecoveryPointsResponseTypeDef = TypedDict(
    "ListRecoveryPointsResponseTypeDef",
    {
        "nextToken": str,
        "recoveryPoints": List[RecoveryPointTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetResourcePolicyResponseTypeDef = TypedDict(
    "GetResourcePolicyResponseTypeDef",
    {
        "resourcePolicy": ResourcePolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutResourcePolicyResponseTypeDef = TypedDict(
    "PutResourcePolicyResponseTypeDef",
    {
        "resourcePolicy": ResourcePolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEndpointAccessRequestListEndpointAccessPaginateTypeDef = TypedDict(
    "ListEndpointAccessRequestListEndpointAccessPaginateTypeDef",
    {
        "vpcId": str,
        "workgroupName": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListNamespacesRequestListNamespacesPaginateTypeDef = TypedDict(
    "ListNamespacesRequestListNamespacesPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListRecoveryPointsRequestListRecoveryPointsPaginateTypeDef = TypedDict(
    "ListRecoveryPointsRequestListRecoveryPointsPaginateTypeDef",
    {
        "endTime": Union[datetime, str],
        "namespaceName": str,
        "startTime": Union[datetime, str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListSnapshotsRequestListSnapshotsPaginateTypeDef = TypedDict(
    "ListSnapshotsRequestListSnapshotsPaginateTypeDef",
    {
        "endTime": Union[datetime, str],
        "namespaceArn": str,
        "namespaceName": str,
        "ownerAccount": str,
        "startTime": Union[datetime, str],
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListUsageLimitsRequestListUsageLimitsPaginateTypeDef = TypedDict(
    "ListUsageLimitsRequestListUsageLimitsPaginateTypeDef",
    {
        "resourceArn": str,
        "usageType": UsageLimitUsageTypeType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListWorkgroupsRequestListWorkgroupsPaginateTypeDef = TypedDict(
    "ListWorkgroupsRequestListWorkgroupsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

VpcEndpointTypeDef = TypedDict(
    "VpcEndpointTypeDef",
    {
        "networkInterfaces": List[NetworkInterfaceTypeDef],
        "vpcEndpointId": str,
        "vpcId": str,
    },
    total=False,
)

EndpointAccessTypeDef = TypedDict(
    "EndpointAccessTypeDef",
    {
        "address": str,
        "endpointArn": str,
        "endpointCreateTime": datetime,
        "endpointName": str,
        "endpointStatus": str,
        "port": int,
        "subnetIds": List[str],
        "vpcEndpoint": VpcEndpointTypeDef,
        "vpcSecurityGroups": List[VpcSecurityGroupMembershipTypeDef],
        "workgroupName": str,
    },
    total=False,
)

EndpointTypeDef = TypedDict(
    "EndpointTypeDef",
    {
        "address": str,
        "port": int,
        "vpcEndpoints": List[VpcEndpointTypeDef],
    },
    total=False,
)

CreateEndpointAccessResponseTypeDef = TypedDict(
    "CreateEndpointAccessResponseTypeDef",
    {
        "endpoint": EndpointAccessTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteEndpointAccessResponseTypeDef = TypedDict(
    "DeleteEndpointAccessResponseTypeDef",
    {
        "endpoint": EndpointAccessTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetEndpointAccessResponseTypeDef = TypedDict(
    "GetEndpointAccessResponseTypeDef",
    {
        "endpoint": EndpointAccessTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEndpointAccessResponseTypeDef = TypedDict(
    "ListEndpointAccessResponseTypeDef",
    {
        "endpoints": List[EndpointAccessTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateEndpointAccessResponseTypeDef = TypedDict(
    "UpdateEndpointAccessResponseTypeDef",
    {
        "endpoint": EndpointAccessTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

WorkgroupTypeDef = TypedDict(
    "WorkgroupTypeDef",
    {
        "baseCapacity": int,
        "configParameters": List[ConfigParameterTypeDef],
        "creationDate": datetime,
        "endpoint": EndpointTypeDef,
        "enhancedVpcRouting": bool,
        "namespaceName": str,
        "publiclyAccessible": bool,
        "securityGroupIds": List[str],
        "status": WorkgroupStatusType,
        "subnetIds": List[str],
        "workgroupArn": str,
        "workgroupId": str,
        "workgroupName": str,
    },
    total=False,
)

CreateWorkgroupResponseTypeDef = TypedDict(
    "CreateWorkgroupResponseTypeDef",
    {
        "workgroup": WorkgroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteWorkgroupResponseTypeDef = TypedDict(
    "DeleteWorkgroupResponseTypeDef",
    {
        "workgroup": WorkgroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetWorkgroupResponseTypeDef = TypedDict(
    "GetWorkgroupResponseTypeDef",
    {
        "workgroup": WorkgroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListWorkgroupsResponseTypeDef = TypedDict(
    "ListWorkgroupsResponseTypeDef",
    {
        "nextToken": str,
        "workgroups": List[WorkgroupTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateWorkgroupResponseTypeDef = TypedDict(
    "UpdateWorkgroupResponseTypeDef",
    {
        "workgroup": WorkgroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
