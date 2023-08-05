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
    'GetPolicyResult',
    'AwaitableGetPolicyResult',
    'get_policy',
    'get_policy_output',
]

@pulumi.output_type
class GetPolicyResult:
    """
    A collection of values returned by getPolicy.
    """
    def __init__(__self__, id=None, name=None, status=None, type=None):
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)
        if type and not isinstance(type, str):
            raise TypeError("Expected argument 'type' to be a str")
        pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        name of policy.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def status(self) -> str:
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        type of policy.
        """
        return pulumi.get(self, "type")


class AwaitableGetPolicyResult(GetPolicyResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetPolicyResult(
            id=self.id,
            name=self.name,
            status=self.status,
            type=self.type)


def get_policy(name: Optional[str] = None,
               type: Optional[str] = None,
               opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetPolicyResult:
    """
    Use this data source to retrieve a policy from Okta.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_okta as okta

    example = okta.policy.get_policy(name="Password Policy Example",
        type="PASSWORD")
    ```


    :param str name: Name of policy to retrieve.
    :param str type: Type of policy to retrieve. Valid values: `"OKTA_SIGN_ON"`, `"PASSWORD"`, `"MFA_ENROLL"`, 
           `"IDP_DISCOVERY"`, `"ACCESS_POLICY"` (**only available as a part of the Identity Engine**), `"PROFILE_ENROLLMENT"` (**only available as a part of the Identity Engine**)
    """
    __args__ = dict()
    __args__['name'] = name
    __args__['type'] = type
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('okta:policy/getPolicy:getPolicy', __args__, opts=opts, typ=GetPolicyResult).value

    return AwaitableGetPolicyResult(
        id=__ret__.id,
        name=__ret__.name,
        status=__ret__.status,
        type=__ret__.type)


@_utilities.lift_output_func(get_policy)
def get_policy_output(name: Optional[pulumi.Input[str]] = None,
                      type: Optional[pulumi.Input[str]] = None,
                      opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetPolicyResult]:
    """
    Use this data source to retrieve a policy from Okta.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_okta as okta

    example = okta.policy.get_policy(name="Password Policy Example",
        type="PASSWORD")
    ```


    :param str name: Name of policy to retrieve.
    :param str type: Type of policy to retrieve. Valid values: `"OKTA_SIGN_ON"`, `"PASSWORD"`, `"MFA_ENROLL"`, 
           `"IDP_DISCOVERY"`, `"ACCESS_POLICY"` (**only available as a part of the Identity Engine**), `"PROFILE_ENROLLMENT"` (**only available as a part of the Identity Engine**)
    """
    ...
