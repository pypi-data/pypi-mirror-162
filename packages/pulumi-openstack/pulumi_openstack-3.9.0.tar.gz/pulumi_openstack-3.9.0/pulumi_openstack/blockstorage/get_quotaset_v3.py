# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'GetQuotasetV3Result',
    'AwaitableGetQuotasetV3Result',
    'get_quotaset_v3',
    'get_quotaset_v3_output',
]

@pulumi.output_type
class GetQuotasetV3Result:
    """
    A collection of values returned by getQuotasetV3.
    """
    def __init__(__self__, backup_gigabytes=None, backups=None, gigabytes=None, groups=None, id=None, per_volume_gigabytes=None, project_id=None, region=None, snapshots=None, volume_type_quota=None, volumes=None):
        if backup_gigabytes and not isinstance(backup_gigabytes, int):
            raise TypeError("Expected argument 'backup_gigabytes' to be a int")
        pulumi.set(__self__, "backup_gigabytes", backup_gigabytes)
        if backups and not isinstance(backups, int):
            raise TypeError("Expected argument 'backups' to be a int")
        pulumi.set(__self__, "backups", backups)
        if gigabytes and not isinstance(gigabytes, int):
            raise TypeError("Expected argument 'gigabytes' to be a int")
        pulumi.set(__self__, "gigabytes", gigabytes)
        if groups and not isinstance(groups, int):
            raise TypeError("Expected argument 'groups' to be a int")
        pulumi.set(__self__, "groups", groups)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if per_volume_gigabytes and not isinstance(per_volume_gigabytes, int):
            raise TypeError("Expected argument 'per_volume_gigabytes' to be a int")
        pulumi.set(__self__, "per_volume_gigabytes", per_volume_gigabytes)
        if project_id and not isinstance(project_id, str):
            raise TypeError("Expected argument 'project_id' to be a str")
        pulumi.set(__self__, "project_id", project_id)
        if region and not isinstance(region, str):
            raise TypeError("Expected argument 'region' to be a str")
        pulumi.set(__self__, "region", region)
        if snapshots and not isinstance(snapshots, int):
            raise TypeError("Expected argument 'snapshots' to be a int")
        pulumi.set(__self__, "snapshots", snapshots)
        if volume_type_quota and not isinstance(volume_type_quota, dict):
            raise TypeError("Expected argument 'volume_type_quota' to be a dict")
        pulumi.set(__self__, "volume_type_quota", volume_type_quota)
        if volumes and not isinstance(volumes, int):
            raise TypeError("Expected argument 'volumes' to be a int")
        pulumi.set(__self__, "volumes", volumes)

    @property
    @pulumi.getter(name="backupGigabytes")
    def backup_gigabytes(self) -> int:
        """
        The size (GB) of backups that are allowed.
        """
        return pulumi.get(self, "backup_gigabytes")

    @property
    @pulumi.getter
    def backups(self) -> int:
        """
        The number of backups that are allowed.
        """
        return pulumi.get(self, "backups")

    @property
    @pulumi.getter
    def gigabytes(self) -> int:
        """
        The size (GB) of volumes and snapshots that are allowed.
        """
        return pulumi.get(self, "gigabytes")

    @property
    @pulumi.getter
    def groups(self) -> int:
        """
        The number of groups that are allowed.
        """
        return pulumi.get(self, "groups")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="perVolumeGigabytes")
    def per_volume_gigabytes(self) -> int:
        """
        The size (GB) of volumes that are allowed for each volume.
        """
        return pulumi.get(self, "per_volume_gigabytes")

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> str:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "project_id")

    @property
    @pulumi.getter
    def region(self) -> str:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter
    def snapshots(self) -> int:
        """
        The number of snapshots that are allowed.
        """
        return pulumi.get(self, "snapshots")

    @property
    @pulumi.getter(name="volumeTypeQuota")
    def volume_type_quota(self) -> Mapping[str, Any]:
        """
        Map with gigabytes_{volume_type}, snapshots_{volume_type}, volumes_{volume_type} for each volume type.
        """
        return pulumi.get(self, "volume_type_quota")

    @property
    @pulumi.getter
    def volumes(self) -> int:
        """
        The number of volumes that are allowed.
        """
        return pulumi.get(self, "volumes")


class AwaitableGetQuotasetV3Result(GetQuotasetV3Result):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetQuotasetV3Result(
            backup_gigabytes=self.backup_gigabytes,
            backups=self.backups,
            gigabytes=self.gigabytes,
            groups=self.groups,
            id=self.id,
            per_volume_gigabytes=self.per_volume_gigabytes,
            project_id=self.project_id,
            region=self.region,
            snapshots=self.snapshots,
            volume_type_quota=self.volume_type_quota,
            volumes=self.volumes)


def get_quotaset_v3(project_id: Optional[str] = None,
                    region: Optional[str] = None,
                    opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetQuotasetV3Result:
    """
    Use this data source to get the blockstorage quotaset v3 of an OpenStack project.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_openstack as openstack

    quota = openstack.blockstorage.get_quotaset_v3(project_id="2e367a3d29f94fd988e6ec54e305ec9d")
    ```


    :param str project_id: The id of the project to retrieve the quotaset.
    :param str region: The region in which to obtain the V3 Blockstorage client.
           If omitted, the `region` argument of the provider is used.
    """
    __args__ = dict()
    __args__['projectId'] = project_id
    __args__['region'] = region
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('openstack:blockstorage/getQuotasetV3:getQuotasetV3', __args__, opts=opts, typ=GetQuotasetV3Result).value

    return AwaitableGetQuotasetV3Result(
        backup_gigabytes=__ret__.backup_gigabytes,
        backups=__ret__.backups,
        gigabytes=__ret__.gigabytes,
        groups=__ret__.groups,
        id=__ret__.id,
        per_volume_gigabytes=__ret__.per_volume_gigabytes,
        project_id=__ret__.project_id,
        region=__ret__.region,
        snapshots=__ret__.snapshots,
        volume_type_quota=__ret__.volume_type_quota,
        volumes=__ret__.volumes)


@_utilities.lift_output_func(get_quotaset_v3)
def get_quotaset_v3_output(project_id: Optional[pulumi.Input[str]] = None,
                           region: Optional[pulumi.Input[Optional[str]]] = None,
                           opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetQuotasetV3Result]:
    """
    Use this data source to get the blockstorage quotaset v3 of an OpenStack project.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_openstack as openstack

    quota = openstack.blockstorage.get_quotaset_v3(project_id="2e367a3d29f94fd988e6ec54e305ec9d")
    ```


    :param str project_id: The id of the project to retrieve the quotaset.
    :param str region: The region in which to obtain the V3 Blockstorage client.
           If omitted, the `region` argument of the provider is used.
    """
    ...
