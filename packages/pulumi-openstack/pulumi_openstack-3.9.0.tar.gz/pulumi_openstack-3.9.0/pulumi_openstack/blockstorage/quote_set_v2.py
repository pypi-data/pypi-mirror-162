# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['QuoteSetV2Args', 'QuoteSetV2']

@pulumi.input_type
class QuoteSetV2Args:
    def __init__(__self__, *,
                 project_id: pulumi.Input[str],
                 backup_gigabytes: Optional[pulumi.Input[int]] = None,
                 backups: Optional[pulumi.Input[int]] = None,
                 gigabytes: Optional[pulumi.Input[int]] = None,
                 groups: Optional[pulumi.Input[int]] = None,
                 per_volume_gigabytes: Optional[pulumi.Input[int]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 snapshots: Optional[pulumi.Input[int]] = None,
                 volume_type_quota: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 volumes: Optional[pulumi.Input[int]] = None):
        """
        The set of arguments for constructing a QuoteSetV2 resource.
        :param pulumi.Input[str] project_id: ID of the project to manage quotas. Changing this
               creates a new quotaset.
        :param pulumi.Input[int] backup_gigabytes: Quota value for backup gigabytes. Changing
               this updates the existing quotaset.
        :param pulumi.Input[int] backups: Quota value for backups. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] gigabytes: Quota value for gigabytes. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] groups: Quota value for groups. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] per_volume_gigabytes: Quota value for gigabytes per volume .
               Changing this updates the existing quotaset.
        :param pulumi.Input[str] region: The region in which to create the volume. If
               omitted, the `region` argument of the provider is used. Changing this
               creates a new quotaset.
        :param pulumi.Input[int] snapshots: Quota value for snapshots. Changing this updates the
               existing quotaset.
        :param pulumi.Input[Mapping[str, Any]] volume_type_quota: Key/Value pairs for setting quota for
               volumes types. Possible keys are `snapshots_<volume_type_name>`,
               `volumes_<volume_type_name>` and `gigabytes_<volume_type_name>`.
        :param pulumi.Input[int] volumes: Quota value for volumes. Changing this updates the
               existing quotaset.
        """
        pulumi.set(__self__, "project_id", project_id)
        if backup_gigabytes is not None:
            pulumi.set(__self__, "backup_gigabytes", backup_gigabytes)
        if backups is not None:
            pulumi.set(__self__, "backups", backups)
        if gigabytes is not None:
            pulumi.set(__self__, "gigabytes", gigabytes)
        if groups is not None:
            pulumi.set(__self__, "groups", groups)
        if per_volume_gigabytes is not None:
            pulumi.set(__self__, "per_volume_gigabytes", per_volume_gigabytes)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if snapshots is not None:
            pulumi.set(__self__, "snapshots", snapshots)
        if volume_type_quota is not None:
            pulumi.set(__self__, "volume_type_quota", volume_type_quota)
        if volumes is not None:
            pulumi.set(__self__, "volumes", volumes)

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> pulumi.Input[str]:
        """
        ID of the project to manage quotas. Changing this
        creates a new quotaset.
        """
        return pulumi.get(self, "project_id")

    @project_id.setter
    def project_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "project_id", value)

    @property
    @pulumi.getter(name="backupGigabytes")
    def backup_gigabytes(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for backup gigabytes. Changing
        this updates the existing quotaset.
        """
        return pulumi.get(self, "backup_gigabytes")

    @backup_gigabytes.setter
    def backup_gigabytes(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "backup_gigabytes", value)

    @property
    @pulumi.getter
    def backups(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for backups. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "backups")

    @backups.setter
    def backups(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "backups", value)

    @property
    @pulumi.getter
    def gigabytes(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for gigabytes. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "gigabytes")

    @gigabytes.setter
    def gigabytes(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "gigabytes", value)

    @property
    @pulumi.getter
    def groups(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for groups. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "groups")

    @groups.setter
    def groups(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "groups", value)

    @property
    @pulumi.getter(name="perVolumeGigabytes")
    def per_volume_gigabytes(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for gigabytes per volume .
        Changing this updates the existing quotaset.
        """
        return pulumi.get(self, "per_volume_gigabytes")

    @per_volume_gigabytes.setter
    def per_volume_gigabytes(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "per_volume_gigabytes", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to create the volume. If
        omitted, the `region` argument of the provider is used. Changing this
        creates a new quotaset.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter
    def snapshots(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for snapshots. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "snapshots")

    @snapshots.setter
    def snapshots(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "snapshots", value)

    @property
    @pulumi.getter(name="volumeTypeQuota")
    def volume_type_quota(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        Key/Value pairs for setting quota for
        volumes types. Possible keys are `snapshots_<volume_type_name>`,
        `volumes_<volume_type_name>` and `gigabytes_<volume_type_name>`.
        """
        return pulumi.get(self, "volume_type_quota")

    @volume_type_quota.setter
    def volume_type_quota(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "volume_type_quota", value)

    @property
    @pulumi.getter
    def volumes(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for volumes. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "volumes")

    @volumes.setter
    def volumes(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "volumes", value)


@pulumi.input_type
class _QuoteSetV2State:
    def __init__(__self__, *,
                 backup_gigabytes: Optional[pulumi.Input[int]] = None,
                 backups: Optional[pulumi.Input[int]] = None,
                 gigabytes: Optional[pulumi.Input[int]] = None,
                 groups: Optional[pulumi.Input[int]] = None,
                 per_volume_gigabytes: Optional[pulumi.Input[int]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 snapshots: Optional[pulumi.Input[int]] = None,
                 volume_type_quota: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 volumes: Optional[pulumi.Input[int]] = None):
        """
        Input properties used for looking up and filtering QuoteSetV2 resources.
        :param pulumi.Input[int] backup_gigabytes: Quota value for backup gigabytes. Changing
               this updates the existing quotaset.
        :param pulumi.Input[int] backups: Quota value for backups. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] gigabytes: Quota value for gigabytes. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] groups: Quota value for groups. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] per_volume_gigabytes: Quota value for gigabytes per volume .
               Changing this updates the existing quotaset.
        :param pulumi.Input[str] project_id: ID of the project to manage quotas. Changing this
               creates a new quotaset.
        :param pulumi.Input[str] region: The region in which to create the volume. If
               omitted, the `region` argument of the provider is used. Changing this
               creates a new quotaset.
        :param pulumi.Input[int] snapshots: Quota value for snapshots. Changing this updates the
               existing quotaset.
        :param pulumi.Input[Mapping[str, Any]] volume_type_quota: Key/Value pairs for setting quota for
               volumes types. Possible keys are `snapshots_<volume_type_name>`,
               `volumes_<volume_type_name>` and `gigabytes_<volume_type_name>`.
        :param pulumi.Input[int] volumes: Quota value for volumes. Changing this updates the
               existing quotaset.
        """
        if backup_gigabytes is not None:
            pulumi.set(__self__, "backup_gigabytes", backup_gigabytes)
        if backups is not None:
            pulumi.set(__self__, "backups", backups)
        if gigabytes is not None:
            pulumi.set(__self__, "gigabytes", gigabytes)
        if groups is not None:
            pulumi.set(__self__, "groups", groups)
        if per_volume_gigabytes is not None:
            pulumi.set(__self__, "per_volume_gigabytes", per_volume_gigabytes)
        if project_id is not None:
            pulumi.set(__self__, "project_id", project_id)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if snapshots is not None:
            pulumi.set(__self__, "snapshots", snapshots)
        if volume_type_quota is not None:
            pulumi.set(__self__, "volume_type_quota", volume_type_quota)
        if volumes is not None:
            pulumi.set(__self__, "volumes", volumes)

    @property
    @pulumi.getter(name="backupGigabytes")
    def backup_gigabytes(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for backup gigabytes. Changing
        this updates the existing quotaset.
        """
        return pulumi.get(self, "backup_gigabytes")

    @backup_gigabytes.setter
    def backup_gigabytes(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "backup_gigabytes", value)

    @property
    @pulumi.getter
    def backups(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for backups. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "backups")

    @backups.setter
    def backups(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "backups", value)

    @property
    @pulumi.getter
    def gigabytes(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for gigabytes. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "gigabytes")

    @gigabytes.setter
    def gigabytes(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "gigabytes", value)

    @property
    @pulumi.getter
    def groups(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for groups. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "groups")

    @groups.setter
    def groups(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "groups", value)

    @property
    @pulumi.getter(name="perVolumeGigabytes")
    def per_volume_gigabytes(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for gigabytes per volume .
        Changing this updates the existing quotaset.
        """
        return pulumi.get(self, "per_volume_gigabytes")

    @per_volume_gigabytes.setter
    def per_volume_gigabytes(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "per_volume_gigabytes", value)

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the project to manage quotas. Changing this
        creates a new quotaset.
        """
        return pulumi.get(self, "project_id")

    @project_id.setter
    def project_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project_id", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to create the volume. If
        omitted, the `region` argument of the provider is used. Changing this
        creates a new quotaset.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter
    def snapshots(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for snapshots. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "snapshots")

    @snapshots.setter
    def snapshots(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "snapshots", value)

    @property
    @pulumi.getter(name="volumeTypeQuota")
    def volume_type_quota(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        Key/Value pairs for setting quota for
        volumes types. Possible keys are `snapshots_<volume_type_name>`,
        `volumes_<volume_type_name>` and `gigabytes_<volume_type_name>`.
        """
        return pulumi.get(self, "volume_type_quota")

    @volume_type_quota.setter
    def volume_type_quota(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "volume_type_quota", value)

    @property
    @pulumi.getter
    def volumes(self) -> Optional[pulumi.Input[int]]:
        """
        Quota value for volumes. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "volumes")

    @volumes.setter
    def volumes(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "volumes", value)


class QuoteSetV2(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 backup_gigabytes: Optional[pulumi.Input[int]] = None,
                 backups: Optional[pulumi.Input[int]] = None,
                 gigabytes: Optional[pulumi.Input[int]] = None,
                 groups: Optional[pulumi.Input[int]] = None,
                 per_volume_gigabytes: Optional[pulumi.Input[int]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 snapshots: Optional[pulumi.Input[int]] = None,
                 volume_type_quota: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 volumes: Optional[pulumi.Input[int]] = None,
                 __props__=None):
        """
        Manages a V2 block storage quotaset resource within OpenStack.

        > **Note:** This usually requires admin privileges.

        > **Note:** This resource has a no-op deletion so no actual actions will be done against the OpenStack API
            in case of delete call.

        > **Note:** This resource has all-in creation so all optional quota arguments that were not specified are
            created with zero value. This excludes volume type quota.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_openstack as openstack

        project1 = openstack.identity.Project("project1")
        quotaset1 = openstack.blockstorage.QuoteSetV2("quotaset1",
            project_id=project1.id,
            volumes=10,
            snapshots=4,
            gigabytes=100,
            per_volume_gigabytes=10,
            backups=4,
            backup_gigabytes=10,
            groups=100,
            volume_type_quota={
                "volumes_ssd": 30,
                "gigabytes_ssd": 500,
                "snapshots_ssd": 10,
            })
        ```

        ## Import

        Quotasets can be imported using the `project_id/region`, e.g.

        ```sh
         $ pulumi import openstack:blockstorage/quoteSetV2:QuoteSetV2 quotaset_1 2a0f2240-c5e6-41de-896d-e80d97428d6b/region_1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[int] backup_gigabytes: Quota value for backup gigabytes. Changing
               this updates the existing quotaset.
        :param pulumi.Input[int] backups: Quota value for backups. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] gigabytes: Quota value for gigabytes. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] groups: Quota value for groups. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] per_volume_gigabytes: Quota value for gigabytes per volume .
               Changing this updates the existing quotaset.
        :param pulumi.Input[str] project_id: ID of the project to manage quotas. Changing this
               creates a new quotaset.
        :param pulumi.Input[str] region: The region in which to create the volume. If
               omitted, the `region` argument of the provider is used. Changing this
               creates a new quotaset.
        :param pulumi.Input[int] snapshots: Quota value for snapshots. Changing this updates the
               existing quotaset.
        :param pulumi.Input[Mapping[str, Any]] volume_type_quota: Key/Value pairs for setting quota for
               volumes types. Possible keys are `snapshots_<volume_type_name>`,
               `volumes_<volume_type_name>` and `gigabytes_<volume_type_name>`.
        :param pulumi.Input[int] volumes: Quota value for volumes. Changing this updates the
               existing quotaset.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: QuoteSetV2Args,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a V2 block storage quotaset resource within OpenStack.

        > **Note:** This usually requires admin privileges.

        > **Note:** This resource has a no-op deletion so no actual actions will be done against the OpenStack API
            in case of delete call.

        > **Note:** This resource has all-in creation so all optional quota arguments that were not specified are
            created with zero value. This excludes volume type quota.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_openstack as openstack

        project1 = openstack.identity.Project("project1")
        quotaset1 = openstack.blockstorage.QuoteSetV2("quotaset1",
            project_id=project1.id,
            volumes=10,
            snapshots=4,
            gigabytes=100,
            per_volume_gigabytes=10,
            backups=4,
            backup_gigabytes=10,
            groups=100,
            volume_type_quota={
                "volumes_ssd": 30,
                "gigabytes_ssd": 500,
                "snapshots_ssd": 10,
            })
        ```

        ## Import

        Quotasets can be imported using the `project_id/region`, e.g.

        ```sh
         $ pulumi import openstack:blockstorage/quoteSetV2:QuoteSetV2 quotaset_1 2a0f2240-c5e6-41de-896d-e80d97428d6b/region_1
        ```

        :param str resource_name: The name of the resource.
        :param QuoteSetV2Args args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(QuoteSetV2Args, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 backup_gigabytes: Optional[pulumi.Input[int]] = None,
                 backups: Optional[pulumi.Input[int]] = None,
                 gigabytes: Optional[pulumi.Input[int]] = None,
                 groups: Optional[pulumi.Input[int]] = None,
                 per_volume_gigabytes: Optional[pulumi.Input[int]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 snapshots: Optional[pulumi.Input[int]] = None,
                 volume_type_quota: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 volumes: Optional[pulumi.Input[int]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = QuoteSetV2Args.__new__(QuoteSetV2Args)

            __props__.__dict__["backup_gigabytes"] = backup_gigabytes
            __props__.__dict__["backups"] = backups
            __props__.__dict__["gigabytes"] = gigabytes
            __props__.__dict__["groups"] = groups
            __props__.__dict__["per_volume_gigabytes"] = per_volume_gigabytes
            if project_id is None and not opts.urn:
                raise TypeError("Missing required property 'project_id'")
            __props__.__dict__["project_id"] = project_id
            __props__.__dict__["region"] = region
            __props__.__dict__["snapshots"] = snapshots
            __props__.__dict__["volume_type_quota"] = volume_type_quota
            __props__.__dict__["volumes"] = volumes
        super(QuoteSetV2, __self__).__init__(
            'openstack:blockstorage/quoteSetV2:QuoteSetV2',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            backup_gigabytes: Optional[pulumi.Input[int]] = None,
            backups: Optional[pulumi.Input[int]] = None,
            gigabytes: Optional[pulumi.Input[int]] = None,
            groups: Optional[pulumi.Input[int]] = None,
            per_volume_gigabytes: Optional[pulumi.Input[int]] = None,
            project_id: Optional[pulumi.Input[str]] = None,
            region: Optional[pulumi.Input[str]] = None,
            snapshots: Optional[pulumi.Input[int]] = None,
            volume_type_quota: Optional[pulumi.Input[Mapping[str, Any]]] = None,
            volumes: Optional[pulumi.Input[int]] = None) -> 'QuoteSetV2':
        """
        Get an existing QuoteSetV2 resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[int] backup_gigabytes: Quota value for backup gigabytes. Changing
               this updates the existing quotaset.
        :param pulumi.Input[int] backups: Quota value for backups. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] gigabytes: Quota value for gigabytes. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] groups: Quota value for groups. Changing this updates the
               existing quotaset.
        :param pulumi.Input[int] per_volume_gigabytes: Quota value for gigabytes per volume .
               Changing this updates the existing quotaset.
        :param pulumi.Input[str] project_id: ID of the project to manage quotas. Changing this
               creates a new quotaset.
        :param pulumi.Input[str] region: The region in which to create the volume. If
               omitted, the `region` argument of the provider is used. Changing this
               creates a new quotaset.
        :param pulumi.Input[int] snapshots: Quota value for snapshots. Changing this updates the
               existing quotaset.
        :param pulumi.Input[Mapping[str, Any]] volume_type_quota: Key/Value pairs for setting quota for
               volumes types. Possible keys are `snapshots_<volume_type_name>`,
               `volumes_<volume_type_name>` and `gigabytes_<volume_type_name>`.
        :param pulumi.Input[int] volumes: Quota value for volumes. Changing this updates the
               existing quotaset.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _QuoteSetV2State.__new__(_QuoteSetV2State)

        __props__.__dict__["backup_gigabytes"] = backup_gigabytes
        __props__.__dict__["backups"] = backups
        __props__.__dict__["gigabytes"] = gigabytes
        __props__.__dict__["groups"] = groups
        __props__.__dict__["per_volume_gigabytes"] = per_volume_gigabytes
        __props__.__dict__["project_id"] = project_id
        __props__.__dict__["region"] = region
        __props__.__dict__["snapshots"] = snapshots
        __props__.__dict__["volume_type_quota"] = volume_type_quota
        __props__.__dict__["volumes"] = volumes
        return QuoteSetV2(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="backupGigabytes")
    def backup_gigabytes(self) -> pulumi.Output[int]:
        """
        Quota value for backup gigabytes. Changing
        this updates the existing quotaset.
        """
        return pulumi.get(self, "backup_gigabytes")

    @property
    @pulumi.getter
    def backups(self) -> pulumi.Output[int]:
        """
        Quota value for backups. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "backups")

    @property
    @pulumi.getter
    def gigabytes(self) -> pulumi.Output[int]:
        """
        Quota value for gigabytes. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "gigabytes")

    @property
    @pulumi.getter
    def groups(self) -> pulumi.Output[int]:
        """
        Quota value for groups. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "groups")

    @property
    @pulumi.getter(name="perVolumeGigabytes")
    def per_volume_gigabytes(self) -> pulumi.Output[int]:
        """
        Quota value for gigabytes per volume .
        Changing this updates the existing quotaset.
        """
        return pulumi.get(self, "per_volume_gigabytes")

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> pulumi.Output[str]:
        """
        ID of the project to manage quotas. Changing this
        creates a new quotaset.
        """
        return pulumi.get(self, "project_id")

    @property
    @pulumi.getter
    def region(self) -> pulumi.Output[str]:
        """
        The region in which to create the volume. If
        omitted, the `region` argument of the provider is used. Changing this
        creates a new quotaset.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter
    def snapshots(self) -> pulumi.Output[int]:
        """
        Quota value for snapshots. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "snapshots")

    @property
    @pulumi.getter(name="volumeTypeQuota")
    def volume_type_quota(self) -> pulumi.Output[Optional[Mapping[str, Any]]]:
        """
        Key/Value pairs for setting quota for
        volumes types. Possible keys are `snapshots_<volume_type_name>`,
        `volumes_<volume_type_name>` and `gigabytes_<volume_type_name>`.
        """
        return pulumi.get(self, "volume_type_quota")

    @property
    @pulumi.getter
    def volumes(self) -> pulumi.Output[int]:
        """
        Quota value for volumes. Changing this updates the
        existing quotaset.
        """
        return pulumi.get(self, "volumes")

