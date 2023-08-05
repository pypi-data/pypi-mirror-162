# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities
from ._inputs import *

__all__ = ['ProviderArgs', 'Provider']

@pulumi.input_type
class ProviderArgs:
    def __init__(__self__, *,
                 app_auth: Optional[pulumi.Input['ProviderAppAuthArgs']] = None,
                 base_url: Optional[pulumi.Input[str]] = None,
                 insecure: Optional[pulumi.Input[bool]] = None,
                 organization: Optional[pulumi.Input[str]] = None,
                 owner: Optional[pulumi.Input[str]] = None,
                 read_delay_ms: Optional[pulumi.Input[int]] = None,
                 token: Optional[pulumi.Input[str]] = None,
                 write_delay_ms: Optional[pulumi.Input[int]] = None):
        """
        The set of arguments for constructing a Provider resource.
        :param pulumi.Input['ProviderAppAuthArgs'] app_auth: The GitHub App credentials used to connect to GitHub. Conflicts with `token`. Anonymous mode is enabled if both `token`
               and `app_auth` are not set.
        :param pulumi.Input[str] base_url: The GitHub Base API URL
        :param pulumi.Input[bool] insecure: Enable `insecure` mode for testing purposes
        :param pulumi.Input[str] organization: The GitHub organization name to manage. Use this field instead of `owner` when managing organization accounts.
        :param pulumi.Input[str] owner: The GitHub owner name to manage. Use this field instead of `organization` when managing individual accounts.
        :param pulumi.Input[int] read_delay_ms: Amount of time in milliseconds to sleep in between non-write requests to GitHub API. Defaults to 0ms if not set.
        :param pulumi.Input[str] token: The OAuth token used to connect to GitHub. Anonymous mode is enabled if both `token` and `app_auth` are not set.
        :param pulumi.Input[int] write_delay_ms: Amount of time in milliseconds to sleep in between writes to GitHub API. Defaults to 1000ms or 1s if not set.
        """
        if app_auth is not None:
            pulumi.set(__self__, "app_auth", app_auth)
        if base_url is None:
            base_url = (_utilities.get_env('GITHUB_BASE_URL') or 'https://api.github.com/')
        if base_url is not None:
            pulumi.set(__self__, "base_url", base_url)
        if insecure is not None:
            pulumi.set(__self__, "insecure", insecure)
        if organization is not None:
            warnings.warn("""Use owner (or GITHUB_OWNER) instead of organization (or GITHUB_ORGANIZATION)""", DeprecationWarning)
            pulumi.log.warn("""organization is deprecated: Use owner (or GITHUB_OWNER) instead of organization (or GITHUB_ORGANIZATION)""")
        if organization is not None:
            pulumi.set(__self__, "organization", organization)
        if owner is not None:
            pulumi.set(__self__, "owner", owner)
        if read_delay_ms is not None:
            pulumi.set(__self__, "read_delay_ms", read_delay_ms)
        if token is not None:
            pulumi.set(__self__, "token", token)
        if write_delay_ms is not None:
            pulumi.set(__self__, "write_delay_ms", write_delay_ms)

    @property
    @pulumi.getter(name="appAuth")
    def app_auth(self) -> Optional[pulumi.Input['ProviderAppAuthArgs']]:
        """
        The GitHub App credentials used to connect to GitHub. Conflicts with `token`. Anonymous mode is enabled if both `token`
        and `app_auth` are not set.
        """
        return pulumi.get(self, "app_auth")

    @app_auth.setter
    def app_auth(self, value: Optional[pulumi.Input['ProviderAppAuthArgs']]):
        pulumi.set(self, "app_auth", value)

    @property
    @pulumi.getter(name="baseUrl")
    def base_url(self) -> Optional[pulumi.Input[str]]:
        """
        The GitHub Base API URL
        """
        return pulumi.get(self, "base_url")

    @base_url.setter
    def base_url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "base_url", value)

    @property
    @pulumi.getter
    def insecure(self) -> Optional[pulumi.Input[bool]]:
        """
        Enable `insecure` mode for testing purposes
        """
        return pulumi.get(self, "insecure")

    @insecure.setter
    def insecure(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "insecure", value)

    @property
    @pulumi.getter
    def organization(self) -> Optional[pulumi.Input[str]]:
        """
        The GitHub organization name to manage. Use this field instead of `owner` when managing organization accounts.
        """
        return pulumi.get(self, "organization")

    @organization.setter
    def organization(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "organization", value)

    @property
    @pulumi.getter
    def owner(self) -> Optional[pulumi.Input[str]]:
        """
        The GitHub owner name to manage. Use this field instead of `organization` when managing individual accounts.
        """
        return pulumi.get(self, "owner")

    @owner.setter
    def owner(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "owner", value)

    @property
    @pulumi.getter(name="readDelayMs")
    def read_delay_ms(self) -> Optional[pulumi.Input[int]]:
        """
        Amount of time in milliseconds to sleep in between non-write requests to GitHub API. Defaults to 0ms if not set.
        """
        return pulumi.get(self, "read_delay_ms")

    @read_delay_ms.setter
    def read_delay_ms(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "read_delay_ms", value)

    @property
    @pulumi.getter
    def token(self) -> Optional[pulumi.Input[str]]:
        """
        The OAuth token used to connect to GitHub. Anonymous mode is enabled if both `token` and `app_auth` are not set.
        """
        return pulumi.get(self, "token")

    @token.setter
    def token(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "token", value)

    @property
    @pulumi.getter(name="writeDelayMs")
    def write_delay_ms(self) -> Optional[pulumi.Input[int]]:
        """
        Amount of time in milliseconds to sleep in between writes to GitHub API. Defaults to 1000ms or 1s if not set.
        """
        return pulumi.get(self, "write_delay_ms")

    @write_delay_ms.setter
    def write_delay_ms(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "write_delay_ms", value)


class Provider(pulumi.ProviderResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 app_auth: Optional[pulumi.Input[pulumi.InputType['ProviderAppAuthArgs']]] = None,
                 base_url: Optional[pulumi.Input[str]] = None,
                 insecure: Optional[pulumi.Input[bool]] = None,
                 organization: Optional[pulumi.Input[str]] = None,
                 owner: Optional[pulumi.Input[str]] = None,
                 read_delay_ms: Optional[pulumi.Input[int]] = None,
                 token: Optional[pulumi.Input[str]] = None,
                 write_delay_ms: Optional[pulumi.Input[int]] = None,
                 __props__=None):
        """
        The provider type for the github package. By default, resources use package-wide configuration
        settings, however an explicit `Provider` instance may be created and passed during resource
        construction to achieve fine-grained programmatic control over provider settings. See the
        [documentation](https://www.pulumi.com/docs/reference/programming-model/#providers) for more information.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['ProviderAppAuthArgs']] app_auth: The GitHub App credentials used to connect to GitHub. Conflicts with `token`. Anonymous mode is enabled if both `token`
               and `app_auth` are not set.
        :param pulumi.Input[str] base_url: The GitHub Base API URL
        :param pulumi.Input[bool] insecure: Enable `insecure` mode for testing purposes
        :param pulumi.Input[str] organization: The GitHub organization name to manage. Use this field instead of `owner` when managing organization accounts.
        :param pulumi.Input[str] owner: The GitHub owner name to manage. Use this field instead of `organization` when managing individual accounts.
        :param pulumi.Input[int] read_delay_ms: Amount of time in milliseconds to sleep in between non-write requests to GitHub API. Defaults to 0ms if not set.
        :param pulumi.Input[str] token: The OAuth token used to connect to GitHub. Anonymous mode is enabled if both `token` and `app_auth` are not set.
        :param pulumi.Input[int] write_delay_ms: Amount of time in milliseconds to sleep in between writes to GitHub API. Defaults to 1000ms or 1s if not set.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[ProviderArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        The provider type for the github package. By default, resources use package-wide configuration
        settings, however an explicit `Provider` instance may be created and passed during resource
        construction to achieve fine-grained programmatic control over provider settings. See the
        [documentation](https://www.pulumi.com/docs/reference/programming-model/#providers) for more information.

        :param str resource_name: The name of the resource.
        :param ProviderArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ProviderArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 app_auth: Optional[pulumi.Input[pulumi.InputType['ProviderAppAuthArgs']]] = None,
                 base_url: Optional[pulumi.Input[str]] = None,
                 insecure: Optional[pulumi.Input[bool]] = None,
                 organization: Optional[pulumi.Input[str]] = None,
                 owner: Optional[pulumi.Input[str]] = None,
                 read_delay_ms: Optional[pulumi.Input[int]] = None,
                 token: Optional[pulumi.Input[str]] = None,
                 write_delay_ms: Optional[pulumi.Input[int]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ProviderArgs.__new__(ProviderArgs)

            __props__.__dict__["app_auth"] = pulumi.Output.from_input(app_auth).apply(pulumi.runtime.to_json) if app_auth is not None else None
            if base_url is None:
                base_url = (_utilities.get_env('GITHUB_BASE_URL') or 'https://api.github.com/')
            __props__.__dict__["base_url"] = base_url
            __props__.__dict__["insecure"] = pulumi.Output.from_input(insecure).apply(pulumi.runtime.to_json) if insecure is not None else None
            if organization is not None and not opts.urn:
                warnings.warn("""Use owner (or GITHUB_OWNER) instead of organization (or GITHUB_ORGANIZATION)""", DeprecationWarning)
                pulumi.log.warn("""organization is deprecated: Use owner (or GITHUB_OWNER) instead of organization (or GITHUB_ORGANIZATION)""")
            __props__.__dict__["organization"] = organization
            __props__.__dict__["owner"] = owner
            __props__.__dict__["read_delay_ms"] = pulumi.Output.from_input(read_delay_ms).apply(pulumi.runtime.to_json) if read_delay_ms is not None else None
            __props__.__dict__["token"] = token
            __props__.__dict__["write_delay_ms"] = pulumi.Output.from_input(write_delay_ms).apply(pulumi.runtime.to_json) if write_delay_ms is not None else None
        super(Provider, __self__).__init__(
            'github',
            resource_name,
            __props__,
            opts)

    @property
    @pulumi.getter(name="baseUrl")
    def base_url(self) -> pulumi.Output[Optional[str]]:
        """
        The GitHub Base API URL
        """
        return pulumi.get(self, "base_url")

    @property
    @pulumi.getter
    def organization(self) -> pulumi.Output[Optional[str]]:
        """
        The GitHub organization name to manage. Use this field instead of `owner` when managing organization accounts.
        """
        return pulumi.get(self, "organization")

    @property
    @pulumi.getter
    def owner(self) -> pulumi.Output[Optional[str]]:
        """
        The GitHub owner name to manage. Use this field instead of `organization` when managing individual accounts.
        """
        return pulumi.get(self, "owner")

    @property
    @pulumi.getter
    def token(self) -> pulumi.Output[Optional[str]]:
        """
        The OAuth token used to connect to GitHub. Anonymous mode is enabled if both `token` and `app_auth` are not set.
        """
        return pulumi.get(self, "token")

