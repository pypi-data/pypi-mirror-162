# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['EmuGroupMappingArgs', 'EmuGroupMapping']

@pulumi.input_type
class EmuGroupMappingArgs:
    def __init__(__self__, *,
                 group_id: pulumi.Input[int],
                 team_slug: pulumi.Input[str]):
        """
        The set of arguments for constructing a EmuGroupMapping resource.
        :param pulumi.Input[int] group_id: Integer corresponding to the external group ID to be linked
        :param pulumi.Input[str] team_slug: Slug of the GitHub team
        """
        pulumi.set(__self__, "group_id", group_id)
        pulumi.set(__self__, "team_slug", team_slug)

    @property
    @pulumi.getter(name="groupId")
    def group_id(self) -> pulumi.Input[int]:
        """
        Integer corresponding to the external group ID to be linked
        """
        return pulumi.get(self, "group_id")

    @group_id.setter
    def group_id(self, value: pulumi.Input[int]):
        pulumi.set(self, "group_id", value)

    @property
    @pulumi.getter(name="teamSlug")
    def team_slug(self) -> pulumi.Input[str]:
        """
        Slug of the GitHub team
        """
        return pulumi.get(self, "team_slug")

    @team_slug.setter
    def team_slug(self, value: pulumi.Input[str]):
        pulumi.set(self, "team_slug", value)


@pulumi.input_type
class _EmuGroupMappingState:
    def __init__(__self__, *,
                 etag: Optional[pulumi.Input[str]] = None,
                 group_id: Optional[pulumi.Input[int]] = None,
                 team_slug: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering EmuGroupMapping resources.
        :param pulumi.Input[int] group_id: Integer corresponding to the external group ID to be linked
        :param pulumi.Input[str] team_slug: Slug of the GitHub team
        """
        if etag is not None:
            pulumi.set(__self__, "etag", etag)
        if group_id is not None:
            pulumi.set(__self__, "group_id", group_id)
        if team_slug is not None:
            pulumi.set(__self__, "team_slug", team_slug)

    @property
    @pulumi.getter
    def etag(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "etag")

    @etag.setter
    def etag(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "etag", value)

    @property
    @pulumi.getter(name="groupId")
    def group_id(self) -> Optional[pulumi.Input[int]]:
        """
        Integer corresponding to the external group ID to be linked
        """
        return pulumi.get(self, "group_id")

    @group_id.setter
    def group_id(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "group_id", value)

    @property
    @pulumi.getter(name="teamSlug")
    def team_slug(self) -> Optional[pulumi.Input[str]]:
        """
        Slug of the GitHub team
        """
        return pulumi.get(self, "team_slug")

    @team_slug.setter
    def team_slug(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "team_slug", value)


class EmuGroupMapping(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 group_id: Optional[pulumi.Input[int]] = None,
                 team_slug: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        This resource manages mappings between external groups for enterprise managed users and GitHub teams. It wraps the API detailed [here](https://docs.github.com/en/rest/reference/teams#external-groups). Note that this is a distinct resource from `TeamSyncGroupMapping`. `EmuGroupMapping` is special to the Enterprise Managed User (EMU) external group feature, whereas `TeamSyncGroupMapping` is specific to Identity Provider Groups.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_github as github

        example_emu_group_mapping = github.EmuGroupMapping("exampleEmuGroupMapping",
            group_id=28836,
            team_slug="emu-test-team")
        # The GitHub team name to modify
        ```

        ## Import

        GitHub EMU External Group Mappings can be imported using the external `group_id`, e.g.

        ```sh
         $ pulumi import github:index/emuGroupMapping:EmuGroupMapping example_emu_group_mapping 28836
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[int] group_id: Integer corresponding to the external group ID to be linked
        :param pulumi.Input[str] team_slug: Slug of the GitHub team
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: EmuGroupMappingArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        This resource manages mappings between external groups for enterprise managed users and GitHub teams. It wraps the API detailed [here](https://docs.github.com/en/rest/reference/teams#external-groups). Note that this is a distinct resource from `TeamSyncGroupMapping`. `EmuGroupMapping` is special to the Enterprise Managed User (EMU) external group feature, whereas `TeamSyncGroupMapping` is specific to Identity Provider Groups.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_github as github

        example_emu_group_mapping = github.EmuGroupMapping("exampleEmuGroupMapping",
            group_id=28836,
            team_slug="emu-test-team")
        # The GitHub team name to modify
        ```

        ## Import

        GitHub EMU External Group Mappings can be imported using the external `group_id`, e.g.

        ```sh
         $ pulumi import github:index/emuGroupMapping:EmuGroupMapping example_emu_group_mapping 28836
        ```

        :param str resource_name: The name of the resource.
        :param EmuGroupMappingArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(EmuGroupMappingArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 group_id: Optional[pulumi.Input[int]] = None,
                 team_slug: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = EmuGroupMappingArgs.__new__(EmuGroupMappingArgs)

            if group_id is None and not opts.urn:
                raise TypeError("Missing required property 'group_id'")
            __props__.__dict__["group_id"] = group_id
            if team_slug is None and not opts.urn:
                raise TypeError("Missing required property 'team_slug'")
            __props__.__dict__["team_slug"] = team_slug
            __props__.__dict__["etag"] = None
        super(EmuGroupMapping, __self__).__init__(
            'github:index/emuGroupMapping:EmuGroupMapping',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            etag: Optional[pulumi.Input[str]] = None,
            group_id: Optional[pulumi.Input[int]] = None,
            team_slug: Optional[pulumi.Input[str]] = None) -> 'EmuGroupMapping':
        """
        Get an existing EmuGroupMapping resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[int] group_id: Integer corresponding to the external group ID to be linked
        :param pulumi.Input[str] team_slug: Slug of the GitHub team
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _EmuGroupMappingState.__new__(_EmuGroupMappingState)

        __props__.__dict__["etag"] = etag
        __props__.__dict__["group_id"] = group_id
        __props__.__dict__["team_slug"] = team_slug
        return EmuGroupMapping(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def etag(self) -> pulumi.Output[str]:
        return pulumi.get(self, "etag")

    @property
    @pulumi.getter(name="groupId")
    def group_id(self) -> pulumi.Output[int]:
        """
        Integer corresponding to the external group ID to be linked
        """
        return pulumi.get(self, "group_id")

    @property
    @pulumi.getter(name="teamSlug")
    def team_slug(self) -> pulumi.Output[str]:
        """
        Slug of the GitHub team
        """
        return pulumi.get(self, "team_slug")

