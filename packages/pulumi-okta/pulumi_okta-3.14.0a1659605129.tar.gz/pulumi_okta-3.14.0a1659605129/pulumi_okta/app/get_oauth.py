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
    'GetOauthResult',
    'AwaitableGetOauthResult',
    'get_oauth',
    'get_oauth_output',
]

@pulumi.output_type
class GetOauthResult:
    """
    A collection of values returned by getOauth.
    """
    def __init__(__self__, active_only=None, auto_submit_toolbar=None, client_id=None, client_uri=None, grant_types=None, groups=None, hide_ios=None, hide_web=None, id=None, label=None, label_prefix=None, links=None, login_mode=None, login_scopes=None, login_uri=None, logo_uri=None, name=None, policy_uri=None, post_logout_redirect_uris=None, redirect_uris=None, response_types=None, skip_groups=None, skip_users=None, status=None, type=None, users=None, wildcard_redirect=None):
        if active_only and not isinstance(active_only, bool):
            raise TypeError("Expected argument 'active_only' to be a bool")
        pulumi.set(__self__, "active_only", active_only)
        if auto_submit_toolbar and not isinstance(auto_submit_toolbar, bool):
            raise TypeError("Expected argument 'auto_submit_toolbar' to be a bool")
        pulumi.set(__self__, "auto_submit_toolbar", auto_submit_toolbar)
        if client_id and not isinstance(client_id, str):
            raise TypeError("Expected argument 'client_id' to be a str")
        pulumi.set(__self__, "client_id", client_id)
        if client_uri and not isinstance(client_uri, str):
            raise TypeError("Expected argument 'client_uri' to be a str")
        pulumi.set(__self__, "client_uri", client_uri)
        if grant_types and not isinstance(grant_types, list):
            raise TypeError("Expected argument 'grant_types' to be a list")
        pulumi.set(__self__, "grant_types", grant_types)
        if groups and not isinstance(groups, list):
            raise TypeError("Expected argument 'groups' to be a list")
        if groups is not None:
            warnings.warn("""The `groups` field is now deprecated for the data source `okta_app_oauth`, please replace all uses of this with: `okta_app_group_assignments`""", DeprecationWarning)
            pulumi.log.warn("""groups is deprecated: The `groups` field is now deprecated for the data source `okta_app_oauth`, please replace all uses of this with: `okta_app_group_assignments`""")

        pulumi.set(__self__, "groups", groups)
        if hide_ios and not isinstance(hide_ios, bool):
            raise TypeError("Expected argument 'hide_ios' to be a bool")
        pulumi.set(__self__, "hide_ios", hide_ios)
        if hide_web and not isinstance(hide_web, bool):
            raise TypeError("Expected argument 'hide_web' to be a bool")
        pulumi.set(__self__, "hide_web", hide_web)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if label and not isinstance(label, str):
            raise TypeError("Expected argument 'label' to be a str")
        pulumi.set(__self__, "label", label)
        if label_prefix and not isinstance(label_prefix, str):
            raise TypeError("Expected argument 'label_prefix' to be a str")
        pulumi.set(__self__, "label_prefix", label_prefix)
        if links and not isinstance(links, str):
            raise TypeError("Expected argument 'links' to be a str")
        pulumi.set(__self__, "links", links)
        if login_mode and not isinstance(login_mode, str):
            raise TypeError("Expected argument 'login_mode' to be a str")
        pulumi.set(__self__, "login_mode", login_mode)
        if login_scopes and not isinstance(login_scopes, list):
            raise TypeError("Expected argument 'login_scopes' to be a list")
        pulumi.set(__self__, "login_scopes", login_scopes)
        if login_uri and not isinstance(login_uri, str):
            raise TypeError("Expected argument 'login_uri' to be a str")
        pulumi.set(__self__, "login_uri", login_uri)
        if logo_uri and not isinstance(logo_uri, str):
            raise TypeError("Expected argument 'logo_uri' to be a str")
        pulumi.set(__self__, "logo_uri", logo_uri)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if policy_uri and not isinstance(policy_uri, str):
            raise TypeError("Expected argument 'policy_uri' to be a str")
        pulumi.set(__self__, "policy_uri", policy_uri)
        if post_logout_redirect_uris and not isinstance(post_logout_redirect_uris, list):
            raise TypeError("Expected argument 'post_logout_redirect_uris' to be a list")
        pulumi.set(__self__, "post_logout_redirect_uris", post_logout_redirect_uris)
        if redirect_uris and not isinstance(redirect_uris, list):
            raise TypeError("Expected argument 'redirect_uris' to be a list")
        pulumi.set(__self__, "redirect_uris", redirect_uris)
        if response_types and not isinstance(response_types, list):
            raise TypeError("Expected argument 'response_types' to be a list")
        pulumi.set(__self__, "response_types", response_types)
        if skip_groups and not isinstance(skip_groups, bool):
            raise TypeError("Expected argument 'skip_groups' to be a bool")
        pulumi.set(__self__, "skip_groups", skip_groups)
        if skip_users and not isinstance(skip_users, bool):
            raise TypeError("Expected argument 'skip_users' to be a bool")
        pulumi.set(__self__, "skip_users", skip_users)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)
        if type and not isinstance(type, str):
            raise TypeError("Expected argument 'type' to be a str")
        pulumi.set(__self__, "type", type)
        if users and not isinstance(users, list):
            raise TypeError("Expected argument 'users' to be a list")
        if users is not None:
            warnings.warn("""The `users` field is now deprecated for the data source `okta_app_oauth`, please replace all uses of this with: `okta_app_user_assignments`""", DeprecationWarning)
            pulumi.log.warn("""users is deprecated: The `users` field is now deprecated for the data source `okta_app_oauth`, please replace all uses of this with: `okta_app_user_assignments`""")

        pulumi.set(__self__, "users", users)
        if wildcard_redirect and not isinstance(wildcard_redirect, str):
            raise TypeError("Expected argument 'wildcard_redirect' to be a str")
        pulumi.set(__self__, "wildcard_redirect", wildcard_redirect)

    @property
    @pulumi.getter(name="activeOnly")
    def active_only(self) -> Optional[bool]:
        return pulumi.get(self, "active_only")

    @property
    @pulumi.getter(name="autoSubmitToolbar")
    def auto_submit_toolbar(self) -> bool:
        """
        Display auto submit toolbar.
        """
        return pulumi.get(self, "auto_submit_toolbar")

    @property
    @pulumi.getter(name="clientId")
    def client_id(self) -> str:
        """
        OAuth client ID. If set during creation, app is created with this id.
        """
        return pulumi.get(self, "client_id")

    @property
    @pulumi.getter(name="clientUri")
    def client_uri(self) -> str:
        """
        URI to a web page providing information about the client.
        """
        return pulumi.get(self, "client_uri")

    @property
    @pulumi.getter(name="grantTypes")
    def grant_types(self) -> Sequence[str]:
        """
        List of OAuth 2.0 grant types.
        """
        return pulumi.get(self, "grant_types")

    @property
    @pulumi.getter
    def groups(self) -> Sequence[str]:
        """
        List of groups IDs assigned to the application.
        - `DEPRECATED`: Please replace all usage of this field with the data source `AppGroupAssignments`.
        """
        return pulumi.get(self, "groups")

    @property
    @pulumi.getter(name="hideIos")
    def hide_ios(self) -> bool:
        """
        Do not display application icon on mobile app.
        """
        return pulumi.get(self, "hide_ios")

    @property
    @pulumi.getter(name="hideWeb")
    def hide_web(self) -> bool:
        """
        Do not display application icon to users.
        """
        return pulumi.get(self, "hide_web")

    @property
    @pulumi.getter
    def id(self) -> Optional[str]:
        """
        ID of application.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def label(self) -> Optional[str]:
        """
        Label of application.
        """
        return pulumi.get(self, "label")

    @property
    @pulumi.getter(name="labelPrefix")
    def label_prefix(self) -> Optional[str]:
        return pulumi.get(self, "label_prefix")

    @property
    @pulumi.getter
    def links(self) -> str:
        """
        generic JSON containing discoverable resources related to the app
        """
        return pulumi.get(self, "links")

    @property
    @pulumi.getter(name="loginMode")
    def login_mode(self) -> str:
        """
        The type of Idp-Initiated login that the client supports, if any.
        """
        return pulumi.get(self, "login_mode")

    @property
    @pulumi.getter(name="loginScopes")
    def login_scopes(self) -> Sequence[str]:
        """
        List of scopes to use for the request.
        """
        return pulumi.get(self, "login_scopes")

    @property
    @pulumi.getter(name="loginUri")
    def login_uri(self) -> str:
        """
        URI that initiates login.
        """
        return pulumi.get(self, "login_uri")

    @property
    @pulumi.getter(name="logoUri")
    def logo_uri(self) -> str:
        """
        URI that references a logo for the client.
        """
        return pulumi.get(self, "logo_uri")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of application.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="policyUri")
    def policy_uri(self) -> str:
        """
        URI to web page providing client policy document.
        """
        return pulumi.get(self, "policy_uri")

    @property
    @pulumi.getter(name="postLogoutRedirectUris")
    def post_logout_redirect_uris(self) -> Sequence[str]:
        """
        List of URIs for redirection after logout.
        """
        return pulumi.get(self, "post_logout_redirect_uris")

    @property
    @pulumi.getter(name="redirectUris")
    def redirect_uris(self) -> Sequence[str]:
        """
        List of URIs for use in the redirect-based flow.
        """
        return pulumi.get(self, "redirect_uris")

    @property
    @pulumi.getter(name="responseTypes")
    def response_types(self) -> Sequence[str]:
        """
        List of OAuth 2.0 response type strings.
        """
        return pulumi.get(self, "response_types")

    @property
    @pulumi.getter(name="skipGroups")
    def skip_groups(self) -> Optional[bool]:
        return pulumi.get(self, "skip_groups")

    @property
    @pulumi.getter(name="skipUsers")
    def skip_users(self) -> Optional[bool]:
        return pulumi.get(self, "skip_users")

    @property
    @pulumi.getter
    def status(self) -> str:
        """
        Status of application.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        The type of OAuth application.
        """
        return pulumi.get(self, "type")

    @property
    @pulumi.getter
    def users(self) -> Sequence[str]:
        """
        List of users IDs assigned to the application.
        - `DEPRECATED`: Please replace all usage of this field with the data source `get_app_user_assignments`.
        """
        return pulumi.get(self, "users")

    @property
    @pulumi.getter(name="wildcardRedirect")
    def wildcard_redirect(self) -> str:
        return pulumi.get(self, "wildcard_redirect")


class AwaitableGetOauthResult(GetOauthResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetOauthResult(
            active_only=self.active_only,
            auto_submit_toolbar=self.auto_submit_toolbar,
            client_id=self.client_id,
            client_uri=self.client_uri,
            grant_types=self.grant_types,
            groups=self.groups,
            hide_ios=self.hide_ios,
            hide_web=self.hide_web,
            id=self.id,
            label=self.label,
            label_prefix=self.label_prefix,
            links=self.links,
            login_mode=self.login_mode,
            login_scopes=self.login_scopes,
            login_uri=self.login_uri,
            logo_uri=self.logo_uri,
            name=self.name,
            policy_uri=self.policy_uri,
            post_logout_redirect_uris=self.post_logout_redirect_uris,
            redirect_uris=self.redirect_uris,
            response_types=self.response_types,
            skip_groups=self.skip_groups,
            skip_users=self.skip_users,
            status=self.status,
            type=self.type,
            users=self.users,
            wildcard_redirect=self.wildcard_redirect)


def get_oauth(active_only: Optional[bool] = None,
              id: Optional[str] = None,
              label: Optional[str] = None,
              label_prefix: Optional[str] = None,
              skip_groups: Optional[bool] = None,
              skip_users: Optional[bool] = None,
              opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetOauthResult:
    """
    Use this data source to retrieve an OIDC application from Okta.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_okta as okta

    test = okta.app.get_oauth(label="Example App")
    ```


    :param bool active_only: tells the provider to query for only `ACTIVE` applications.
    :param str id: `id` of application to retrieve, conflicts with `label` and `label_prefix`.
    :param str label: The label of the app to retrieve, conflicts with `label_prefix` and `id`. Label uses
           the `?q=<label>` query parameter exposed by Okta's API. It should be noted that at this time this searches both `name`
           and `label`. This is used to avoid paginating through all applications.
    :param str label_prefix: Label prefix of the app to retrieve, conflicts with `label` and `id`. This will tell the
           provider to do a `starts with` query as opposed to an `equals` query.
    :param bool skip_groups: Indicator that allows the app to skip `groups` sync. Default is `false`.
    :param bool skip_users: Indicator that allows the app to skip `users` sync. Default is `false`.
    """
    __args__ = dict()
    __args__['activeOnly'] = active_only
    __args__['id'] = id
    __args__['label'] = label
    __args__['labelPrefix'] = label_prefix
    __args__['skipGroups'] = skip_groups
    __args__['skipUsers'] = skip_users
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('okta:app/getOauth:getOauth', __args__, opts=opts, typ=GetOauthResult).value

    return AwaitableGetOauthResult(
        active_only=__ret__.active_only,
        auto_submit_toolbar=__ret__.auto_submit_toolbar,
        client_id=__ret__.client_id,
        client_uri=__ret__.client_uri,
        grant_types=__ret__.grant_types,
        groups=__ret__.groups,
        hide_ios=__ret__.hide_ios,
        hide_web=__ret__.hide_web,
        id=__ret__.id,
        label=__ret__.label,
        label_prefix=__ret__.label_prefix,
        links=__ret__.links,
        login_mode=__ret__.login_mode,
        login_scopes=__ret__.login_scopes,
        login_uri=__ret__.login_uri,
        logo_uri=__ret__.logo_uri,
        name=__ret__.name,
        policy_uri=__ret__.policy_uri,
        post_logout_redirect_uris=__ret__.post_logout_redirect_uris,
        redirect_uris=__ret__.redirect_uris,
        response_types=__ret__.response_types,
        skip_groups=__ret__.skip_groups,
        skip_users=__ret__.skip_users,
        status=__ret__.status,
        type=__ret__.type,
        users=__ret__.users,
        wildcard_redirect=__ret__.wildcard_redirect)


@_utilities.lift_output_func(get_oauth)
def get_oauth_output(active_only: Optional[pulumi.Input[Optional[bool]]] = None,
                     id: Optional[pulumi.Input[Optional[str]]] = None,
                     label: Optional[pulumi.Input[Optional[str]]] = None,
                     label_prefix: Optional[pulumi.Input[Optional[str]]] = None,
                     skip_groups: Optional[pulumi.Input[Optional[bool]]] = None,
                     skip_users: Optional[pulumi.Input[Optional[bool]]] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetOauthResult]:
    """
    Use this data source to retrieve an OIDC application from Okta.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_okta as okta

    test = okta.app.get_oauth(label="Example App")
    ```


    :param bool active_only: tells the provider to query for only `ACTIVE` applications.
    :param str id: `id` of application to retrieve, conflicts with `label` and `label_prefix`.
    :param str label: The label of the app to retrieve, conflicts with `label_prefix` and `id`. Label uses
           the `?q=<label>` query parameter exposed by Okta's API. It should be noted that at this time this searches both `name`
           and `label`. This is used to avoid paginating through all applications.
    :param str label_prefix: Label prefix of the app to retrieve, conflicts with `label` and `id`. This will tell the
           provider to do a `starts with` query as opposed to an `equals` query.
    :param bool skip_groups: Indicator that allows the app to skip `groups` sync. Default is `false`.
    :param bool skip_users: Indicator that allows the app to skip `users` sync. Default is `false`.
    """
    ...
