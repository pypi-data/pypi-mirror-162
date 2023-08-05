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
    'GetNetworkResult',
    'AwaitableGetNetworkResult',
    'get_network',
    'get_network_output',
]

@pulumi.output_type
class GetNetworkResult:
    """
    A collection of values returned by getNetwork.
    """
    def __init__(__self__, admin_state_up=None, all_tags=None, availability_zone_hints=None, description=None, dns_domain=None, external=None, id=None, matching_subnet_cidr=None, mtu=None, name=None, network_id=None, region=None, shared=None, status=None, subnets=None, tags=None, tenant_id=None, transparent_vlan=None):
        if admin_state_up and not isinstance(admin_state_up, str):
            raise TypeError("Expected argument 'admin_state_up' to be a str")
        pulumi.set(__self__, "admin_state_up", admin_state_up)
        if all_tags and not isinstance(all_tags, list):
            raise TypeError("Expected argument 'all_tags' to be a list")
        pulumi.set(__self__, "all_tags", all_tags)
        if availability_zone_hints and not isinstance(availability_zone_hints, list):
            raise TypeError("Expected argument 'availability_zone_hints' to be a list")
        pulumi.set(__self__, "availability_zone_hints", availability_zone_hints)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if dns_domain and not isinstance(dns_domain, str):
            raise TypeError("Expected argument 'dns_domain' to be a str")
        pulumi.set(__self__, "dns_domain", dns_domain)
        if external and not isinstance(external, bool):
            raise TypeError("Expected argument 'external' to be a bool")
        pulumi.set(__self__, "external", external)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if matching_subnet_cidr and not isinstance(matching_subnet_cidr, str):
            raise TypeError("Expected argument 'matching_subnet_cidr' to be a str")
        pulumi.set(__self__, "matching_subnet_cidr", matching_subnet_cidr)
        if mtu and not isinstance(mtu, int):
            raise TypeError("Expected argument 'mtu' to be a int")
        pulumi.set(__self__, "mtu", mtu)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if network_id and not isinstance(network_id, str):
            raise TypeError("Expected argument 'network_id' to be a str")
        pulumi.set(__self__, "network_id", network_id)
        if region and not isinstance(region, str):
            raise TypeError("Expected argument 'region' to be a str")
        pulumi.set(__self__, "region", region)
        if shared and not isinstance(shared, str):
            raise TypeError("Expected argument 'shared' to be a str")
        pulumi.set(__self__, "shared", shared)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)
        if subnets and not isinstance(subnets, list):
            raise TypeError("Expected argument 'subnets' to be a list")
        pulumi.set(__self__, "subnets", subnets)
        if tags and not isinstance(tags, list):
            raise TypeError("Expected argument 'tags' to be a list")
        pulumi.set(__self__, "tags", tags)
        if tenant_id and not isinstance(tenant_id, str):
            raise TypeError("Expected argument 'tenant_id' to be a str")
        pulumi.set(__self__, "tenant_id", tenant_id)
        if transparent_vlan and not isinstance(transparent_vlan, bool):
            raise TypeError("Expected argument 'transparent_vlan' to be a bool")
        pulumi.set(__self__, "transparent_vlan", transparent_vlan)

    @property
    @pulumi.getter(name="adminStateUp")
    def admin_state_up(self) -> str:
        """
        The administrative state of the network.
        """
        return pulumi.get(self, "admin_state_up")

    @property
    @pulumi.getter(name="allTags")
    def all_tags(self) -> Sequence[str]:
        """
        The set of string tags applied on the network.
        """
        return pulumi.get(self, "all_tags")

    @property
    @pulumi.getter(name="availabilityZoneHints")
    def availability_zone_hints(self) -> Sequence[str]:
        """
        The availability zone candidates for the network.
        """
        return pulumi.get(self, "availability_zone_hints")

    @property
    @pulumi.getter
    def description(self) -> Optional[str]:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="dnsDomain")
    def dns_domain(self) -> str:
        """
        The network DNS domain. Available, when Neutron DNS extension
        is enabled
        """
        return pulumi.get(self, "dns_domain")

    @property
    @pulumi.getter
    def external(self) -> Optional[bool]:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "external")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="matchingSubnetCidr")
    def matching_subnet_cidr(self) -> Optional[str]:
        return pulumi.get(self, "matching_subnet_cidr")

    @property
    @pulumi.getter
    def mtu(self) -> Optional[int]:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "mtu")

    @property
    @pulumi.getter
    def name(self) -> Optional[str]:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="networkId")
    def network_id(self) -> Optional[str]:
        return pulumi.get(self, "network_id")

    @property
    @pulumi.getter
    def region(self) -> str:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter
    def shared(self) -> str:
        """
        Specifies whether the network resource can be accessed by any
        tenant or not.
        """
        return pulumi.get(self, "shared")

    @property
    @pulumi.getter
    def status(self) -> Optional[str]:
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def subnets(self) -> Sequence[str]:
        """
        A list of subnet IDs belonging to the network.
        """
        return pulumi.get(self, "subnets")

    @property
    @pulumi.getter
    def tags(self) -> Optional[Sequence[str]]:
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="tenantId")
    def tenant_id(self) -> Optional[str]:
        return pulumi.get(self, "tenant_id")

    @property
    @pulumi.getter(name="transparentVlan")
    def transparent_vlan(self) -> Optional[bool]:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "transparent_vlan")


class AwaitableGetNetworkResult(GetNetworkResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetNetworkResult(
            admin_state_up=self.admin_state_up,
            all_tags=self.all_tags,
            availability_zone_hints=self.availability_zone_hints,
            description=self.description,
            dns_domain=self.dns_domain,
            external=self.external,
            id=self.id,
            matching_subnet_cidr=self.matching_subnet_cidr,
            mtu=self.mtu,
            name=self.name,
            network_id=self.network_id,
            region=self.region,
            shared=self.shared,
            status=self.status,
            subnets=self.subnets,
            tags=self.tags,
            tenant_id=self.tenant_id,
            transparent_vlan=self.transparent_vlan)


def get_network(description: Optional[str] = None,
                external: Optional[bool] = None,
                matching_subnet_cidr: Optional[str] = None,
                mtu: Optional[int] = None,
                name: Optional[str] = None,
                network_id: Optional[str] = None,
                region: Optional[str] = None,
                status: Optional[str] = None,
                tags: Optional[Sequence[str]] = None,
                tenant_id: Optional[str] = None,
                transparent_vlan: Optional[bool] = None,
                opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetNetworkResult:
    """
    Use this data source to get the ID of an available OpenStack network.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_openstack as openstack

    network = openstack.networking.get_network(name="tf_test_network")
    ```


    :param str description: Human-readable description of the network.
    :param bool external: The external routing facility of the network.
    :param str matching_subnet_cidr: The CIDR of a subnet within the network.
    :param int mtu: The network MTU to filter. Available, when Neutron `net-mtu`
           extension is enabled.
    :param str name: The name of the network.
    :param str network_id: The ID of the network.
    :param str region: The region in which to obtain the V2 Neutron client.
           A Neutron client is needed to retrieve networks ids. If omitted, the
           `region` argument of the provider is used.
    :param str status: The status of the network.
    :param Sequence[str] tags: The list of network tags to filter.
    :param str tenant_id: The owner of the network.
    :param bool transparent_vlan: The VLAN transparent attribute for the
           network.
    """
    __args__ = dict()
    __args__['description'] = description
    __args__['external'] = external
    __args__['matchingSubnetCidr'] = matching_subnet_cidr
    __args__['mtu'] = mtu
    __args__['name'] = name
    __args__['networkId'] = network_id
    __args__['region'] = region
    __args__['status'] = status
    __args__['tags'] = tags
    __args__['tenantId'] = tenant_id
    __args__['transparentVlan'] = transparent_vlan
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('openstack:networking/getNetwork:getNetwork', __args__, opts=opts, typ=GetNetworkResult).value

    return AwaitableGetNetworkResult(
        admin_state_up=__ret__.admin_state_up,
        all_tags=__ret__.all_tags,
        availability_zone_hints=__ret__.availability_zone_hints,
        description=__ret__.description,
        dns_domain=__ret__.dns_domain,
        external=__ret__.external,
        id=__ret__.id,
        matching_subnet_cidr=__ret__.matching_subnet_cidr,
        mtu=__ret__.mtu,
        name=__ret__.name,
        network_id=__ret__.network_id,
        region=__ret__.region,
        shared=__ret__.shared,
        status=__ret__.status,
        subnets=__ret__.subnets,
        tags=__ret__.tags,
        tenant_id=__ret__.tenant_id,
        transparent_vlan=__ret__.transparent_vlan)


@_utilities.lift_output_func(get_network)
def get_network_output(description: Optional[pulumi.Input[Optional[str]]] = None,
                       external: Optional[pulumi.Input[Optional[bool]]] = None,
                       matching_subnet_cidr: Optional[pulumi.Input[Optional[str]]] = None,
                       mtu: Optional[pulumi.Input[Optional[int]]] = None,
                       name: Optional[pulumi.Input[Optional[str]]] = None,
                       network_id: Optional[pulumi.Input[Optional[str]]] = None,
                       region: Optional[pulumi.Input[Optional[str]]] = None,
                       status: Optional[pulumi.Input[Optional[str]]] = None,
                       tags: Optional[pulumi.Input[Optional[Sequence[str]]]] = None,
                       tenant_id: Optional[pulumi.Input[Optional[str]]] = None,
                       transparent_vlan: Optional[pulumi.Input[Optional[bool]]] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetNetworkResult]:
    """
    Use this data source to get the ID of an available OpenStack network.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_openstack as openstack

    network = openstack.networking.get_network(name="tf_test_network")
    ```


    :param str description: Human-readable description of the network.
    :param bool external: The external routing facility of the network.
    :param str matching_subnet_cidr: The CIDR of a subnet within the network.
    :param int mtu: The network MTU to filter. Available, when Neutron `net-mtu`
           extension is enabled.
    :param str name: The name of the network.
    :param str network_id: The ID of the network.
    :param str region: The region in which to obtain the V2 Neutron client.
           A Neutron client is needed to retrieve networks ids. If omitted, the
           `region` argument of the provider is used.
    :param str status: The status of the network.
    :param Sequence[str] tags: The list of network tags to filter.
    :param str tenant_id: The owner of the network.
    :param bool transparent_vlan: The VLAN transparent attribute for the
           network.
    """
    ...
