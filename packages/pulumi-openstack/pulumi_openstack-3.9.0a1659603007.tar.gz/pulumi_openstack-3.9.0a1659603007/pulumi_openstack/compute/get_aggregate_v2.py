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
    'GetAggregateV2Result',
    'AwaitableGetAggregateV2Result',
    'get_aggregate_v2',
    'get_aggregate_v2_output',
]

@pulumi.output_type
class GetAggregateV2Result:
    """
    A collection of values returned by getAggregateV2.
    """
    def __init__(__self__, hosts=None, id=None, metadata=None, name=None, zone=None):
        if hosts and not isinstance(hosts, list):
            raise TypeError("Expected argument 'hosts' to be a list")
        pulumi.set(__self__, "hosts", hosts)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if metadata and not isinstance(metadata, dict):
            raise TypeError("Expected argument 'metadata' to be a dict")
        pulumi.set(__self__, "metadata", metadata)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if zone and not isinstance(zone, str):
            raise TypeError("Expected argument 'zone' to be a str")
        pulumi.set(__self__, "zone", zone)

    @property
    @pulumi.getter
    def hosts(self) -> Sequence[str]:
        """
        List of Hypervisors contained in the Host Aggregate
        """
        return pulumi.get(self, "hosts")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def metadata(self) -> Mapping[str, str]:
        """
        Metadata of the Host Aggregate
        """
        return pulumi.get(self, "metadata")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def zone(self) -> str:
        """
        Availability zone of the Host Aggregate
        """
        return pulumi.get(self, "zone")


class AwaitableGetAggregateV2Result(GetAggregateV2Result):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetAggregateV2Result(
            hosts=self.hosts,
            id=self.id,
            metadata=self.metadata,
            name=self.name,
            zone=self.zone)


def get_aggregate_v2(hosts: Optional[Sequence[str]] = None,
                     metadata: Optional[Mapping[str, str]] = None,
                     name: Optional[str] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetAggregateV2Result:
    """
    Use this data source to get information about host aggregates
    by name.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_openstack as openstack

    test = openstack.compute.get_aggregate_v2(name="test")
    ```


    :param Sequence[str] hosts: List of Hypervisors contained in the Host Aggregate
    :param Mapping[str, str] metadata: Metadata of the Host Aggregate
    :param str name: The name of the host aggregate
    """
    __args__ = dict()
    __args__['hosts'] = hosts
    __args__['metadata'] = metadata
    __args__['name'] = name
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('openstack:compute/getAggregateV2:getAggregateV2', __args__, opts=opts, typ=GetAggregateV2Result).value

    return AwaitableGetAggregateV2Result(
        hosts=__ret__.hosts,
        id=__ret__.id,
        metadata=__ret__.metadata,
        name=__ret__.name,
        zone=__ret__.zone)


@_utilities.lift_output_func(get_aggregate_v2)
def get_aggregate_v2_output(hosts: Optional[pulumi.Input[Optional[Sequence[str]]]] = None,
                            metadata: Optional[pulumi.Input[Optional[Mapping[str, str]]]] = None,
                            name: Optional[pulumi.Input[str]] = None,
                            opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetAggregateV2Result]:
    """
    Use this data source to get information about host aggregates
    by name.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_openstack as openstack

    test = openstack.compute.get_aggregate_v2(name="test")
    ```


    :param Sequence[str] hosts: List of Hypervisors contained in the Host Aggregate
    :param Mapping[str, str] metadata: Metadata of the Host Aggregate
    :param str name: The name of the host aggregate
    """
    ...
