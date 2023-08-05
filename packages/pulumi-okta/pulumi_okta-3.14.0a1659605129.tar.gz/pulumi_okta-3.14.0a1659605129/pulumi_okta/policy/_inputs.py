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
    'RuleIdpDiscoveryAppExcludeArgs',
    'RuleIdpDiscoveryAppIncludeArgs',
    'RuleIdpDiscoveryPlatformIncludeArgs',
    'RuleIdpDiscoveryUserIdentifierPatternArgs',
    'RuleMfaAppExcludeArgs',
    'RuleMfaAppIncludeArgs',
    'RuleSignonFactorSequenceArgs',
    'RuleSignonFactorSequenceSecondaryCriteriaArgs',
]

@pulumi.input_type
class RuleIdpDiscoveryAppExcludeArgs:
    def __init__(__self__, *,
                 type: pulumi.Input[str],
                 id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] type: One of: `"ANY"`, `"MOBILE"`, `"DESKTOP"`
        :param pulumi.Input[str] id: Use if `type` is `"APP"` to indicate the application id to include.
        :param pulumi.Input[str] name: Use if the `type` is `"APP_TYPE"` to indicate the type of application(s) to include in instances where an entire group (i.e. `yahoo_mail`) of applications should be included.
        """
        pulumi.set(__self__, "type", type)
        if id is not None:
            pulumi.set(__self__, "id", id)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter
    def type(self) -> pulumi.Input[str]:
        """
        One of: `"ANY"`, `"MOBILE"`, `"DESKTOP"`
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: pulumi.Input[str]):
        pulumi.set(self, "type", value)

    @property
    @pulumi.getter
    def id(self) -> Optional[pulumi.Input[str]]:
        """
        Use if `type` is `"APP"` to indicate the application id to include.
        """
        return pulumi.get(self, "id")

    @id.setter
    def id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Use if the `type` is `"APP_TYPE"` to indicate the type of application(s) to include in instances where an entire group (i.e. `yahoo_mail`) of applications should be included.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)


@pulumi.input_type
class RuleIdpDiscoveryAppIncludeArgs:
    def __init__(__self__, *,
                 type: pulumi.Input[str],
                 id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] type: One of: `"ANY"`, `"MOBILE"`, `"DESKTOP"`
        :param pulumi.Input[str] id: Use if `type` is `"APP"` to indicate the application id to include.
        :param pulumi.Input[str] name: Use if the `type` is `"APP_TYPE"` to indicate the type of application(s) to include in instances where an entire group (i.e. `yahoo_mail`) of applications should be included.
        """
        pulumi.set(__self__, "type", type)
        if id is not None:
            pulumi.set(__self__, "id", id)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter
    def type(self) -> pulumi.Input[str]:
        """
        One of: `"ANY"`, `"MOBILE"`, `"DESKTOP"`
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: pulumi.Input[str]):
        pulumi.set(self, "type", value)

    @property
    @pulumi.getter
    def id(self) -> Optional[pulumi.Input[str]]:
        """
        Use if `type` is `"APP"` to indicate the application id to include.
        """
        return pulumi.get(self, "id")

    @id.setter
    def id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Use if the `type` is `"APP_TYPE"` to indicate the type of application(s) to include in instances where an entire group (i.e. `yahoo_mail`) of applications should be included.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)


@pulumi.input_type
class RuleIdpDiscoveryPlatformIncludeArgs:
    def __init__(__self__, *,
                 os_expression: Optional[pulumi.Input[str]] = None,
                 os_type: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] os_expression: Only available when using `os_type = "OTHER"`
        :param pulumi.Input[str] os_type: One of: `"ANY"`, `"IOS"`, `"WINDOWS"`, `"ANDROID"`, `"OTHER"`, `"OSX"`
        :param pulumi.Input[str] type: One of: `"ANY"`, `"MOBILE"`, `"DESKTOP"`
        """
        if os_expression is not None:
            pulumi.set(__self__, "os_expression", os_expression)
        if os_type is not None:
            pulumi.set(__self__, "os_type", os_type)
        if type is not None:
            pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="osExpression")
    def os_expression(self) -> Optional[pulumi.Input[str]]:
        """
        Only available when using `os_type = "OTHER"`
        """
        return pulumi.get(self, "os_expression")

    @os_expression.setter
    def os_expression(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "os_expression", value)

    @property
    @pulumi.getter(name="osType")
    def os_type(self) -> Optional[pulumi.Input[str]]:
        """
        One of: `"ANY"`, `"IOS"`, `"WINDOWS"`, `"ANDROID"`, `"OTHER"`, `"OSX"`
        """
        return pulumi.get(self, "os_type")

    @os_type.setter
    def os_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "os_type", value)

    @property
    @pulumi.getter
    def type(self) -> Optional[pulumi.Input[str]]:
        """
        One of: `"ANY"`, `"MOBILE"`, `"DESKTOP"`
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "type", value)


@pulumi.input_type
class RuleIdpDiscoveryUserIdentifierPatternArgs:
    def __init__(__self__, *,
                 match_type: Optional[pulumi.Input[str]] = None,
                 value: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] match_type: The kind of pattern. For regex, use `"EXPRESSION"`. For simple string matches, use one of the following: `"SUFFIX"`, `"EQUALS"`, `"STARTS_WITH"`, `"CONTAINS"`
        :param pulumi.Input[str] value: The regex or simple match string to match against.
        """
        if match_type is not None:
            pulumi.set(__self__, "match_type", match_type)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter(name="matchType")
    def match_type(self) -> Optional[pulumi.Input[str]]:
        """
        The kind of pattern. For regex, use `"EXPRESSION"`. For simple string matches, use one of the following: `"SUFFIX"`, `"EQUALS"`, `"STARTS_WITH"`, `"CONTAINS"`
        """
        return pulumi.get(self, "match_type")

    @match_type.setter
    def match_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "match_type", value)

    @property
    @pulumi.getter
    def value(self) -> Optional[pulumi.Input[str]]:
        """
        The regex or simple match string to match against.
        """
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class RuleMfaAppExcludeArgs:
    def __init__(__self__, *,
                 type: pulumi.Input[str],
                 id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] type: One of: `"APP"`, `"APP_TYPE"`
        :param pulumi.Input[str] id: Use if `type` is `"APP"` to indicate the application id to include.
        :param pulumi.Input[str] name: Use if the `type` is `"APP_TYPE"` to indicate the type of application(s) to include in instances where an entire group (i.e. `yahoo_mail`) of applications should be included.
        """
        pulumi.set(__self__, "type", type)
        if id is not None:
            pulumi.set(__self__, "id", id)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter
    def type(self) -> pulumi.Input[str]:
        """
        One of: `"APP"`, `"APP_TYPE"`
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: pulumi.Input[str]):
        pulumi.set(self, "type", value)

    @property
    @pulumi.getter
    def id(self) -> Optional[pulumi.Input[str]]:
        """
        Use if `type` is `"APP"` to indicate the application id to include.
        """
        return pulumi.get(self, "id")

    @id.setter
    def id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Use if the `type` is `"APP_TYPE"` to indicate the type of application(s) to include in instances where an entire group (i.e. `yahoo_mail`) of applications should be included.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)


@pulumi.input_type
class RuleMfaAppIncludeArgs:
    def __init__(__self__, *,
                 type: pulumi.Input[str],
                 id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] type: One of: `"APP"`, `"APP_TYPE"`
        :param pulumi.Input[str] id: Use if `type` is `"APP"` to indicate the application id to include.
        :param pulumi.Input[str] name: Use if the `type` is `"APP_TYPE"` to indicate the type of application(s) to include in instances where an entire group (i.e. `yahoo_mail`) of applications should be included.
        """
        pulumi.set(__self__, "type", type)
        if id is not None:
            pulumi.set(__self__, "id", id)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter
    def type(self) -> pulumi.Input[str]:
        """
        One of: `"APP"`, `"APP_TYPE"`
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: pulumi.Input[str]):
        pulumi.set(self, "type", value)

    @property
    @pulumi.getter
    def id(self) -> Optional[pulumi.Input[str]]:
        """
        Use if `type` is `"APP"` to indicate the application id to include.
        """
        return pulumi.get(self, "id")

    @id.setter
    def id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Use if the `type` is `"APP_TYPE"` to indicate the type of application(s) to include in instances where an entire group (i.e. `yahoo_mail`) of applications should be included.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)


@pulumi.input_type
class RuleSignonFactorSequenceArgs:
    def __init__(__self__, *,
                 primary_criteria_factor_type: pulumi.Input[str],
                 primary_criteria_provider: pulumi.Input[str],
                 secondary_criterias: Optional[pulumi.Input[Sequence[pulumi.Input['RuleSignonFactorSequenceSecondaryCriteriaArgs']]]] = None):
        """
        :param pulumi.Input[str] primary_criteria_factor_type: Primary factor type of the auth section.
        :param pulumi.Input[str] primary_criteria_provider: Primary provider of the auth section.
        :param pulumi.Input[Sequence[pulumi.Input['RuleSignonFactorSequenceSecondaryCriteriaArgs']]] secondary_criterias: Additional authentication steps.
        """
        pulumi.set(__self__, "primary_criteria_factor_type", primary_criteria_factor_type)
        pulumi.set(__self__, "primary_criteria_provider", primary_criteria_provider)
        if secondary_criterias is not None:
            pulumi.set(__self__, "secondary_criterias", secondary_criterias)

    @property
    @pulumi.getter(name="primaryCriteriaFactorType")
    def primary_criteria_factor_type(self) -> pulumi.Input[str]:
        """
        Primary factor type of the auth section.
        """
        return pulumi.get(self, "primary_criteria_factor_type")

    @primary_criteria_factor_type.setter
    def primary_criteria_factor_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "primary_criteria_factor_type", value)

    @property
    @pulumi.getter(name="primaryCriteriaProvider")
    def primary_criteria_provider(self) -> pulumi.Input[str]:
        """
        Primary provider of the auth section.
        """
        return pulumi.get(self, "primary_criteria_provider")

    @primary_criteria_provider.setter
    def primary_criteria_provider(self, value: pulumi.Input[str]):
        pulumi.set(self, "primary_criteria_provider", value)

    @property
    @pulumi.getter(name="secondaryCriterias")
    def secondary_criterias(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['RuleSignonFactorSequenceSecondaryCriteriaArgs']]]]:
        """
        Additional authentication steps.
        """
        return pulumi.get(self, "secondary_criterias")

    @secondary_criterias.setter
    def secondary_criterias(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['RuleSignonFactorSequenceSecondaryCriteriaArgs']]]]):
        pulumi.set(self, "secondary_criterias", value)


@pulumi.input_type
class RuleSignonFactorSequenceSecondaryCriteriaArgs:
    def __init__(__self__, *,
                 factor_type: pulumi.Input[str],
                 provider: pulumi.Input[str]):
        """
        :param pulumi.Input[str] factor_type: Factor type of the additional authentication step.
        :param pulumi.Input[str] provider: Provider of the additional authentication step.
        """
        pulumi.set(__self__, "factor_type", factor_type)
        pulumi.set(__self__, "provider", provider)

    @property
    @pulumi.getter(name="factorType")
    def factor_type(self) -> pulumi.Input[str]:
        """
        Factor type of the additional authentication step.
        """
        return pulumi.get(self, "factor_type")

    @factor_type.setter
    def factor_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "factor_type", value)

    @property
    @pulumi.getter
    def provider(self) -> pulumi.Input[str]:
        """
        Provider of the additional authentication step.
        """
        return pulumi.get(self, "provider")

    @provider.setter
    def provider(self, value: pulumi.Input[str]):
        pulumi.set(self, "provider", value)


