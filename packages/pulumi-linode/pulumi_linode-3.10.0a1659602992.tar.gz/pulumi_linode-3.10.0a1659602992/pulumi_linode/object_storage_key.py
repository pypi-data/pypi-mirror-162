# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities
from . import outputs
from ._inputs import *

__all__ = ['ObjectStorageKeyArgs', 'ObjectStorageKey']

@pulumi.input_type
class ObjectStorageKeyArgs:
    def __init__(__self__, *,
                 label: pulumi.Input[str],
                 bucket_accesses: Optional[pulumi.Input[Sequence[pulumi.Input['ObjectStorageKeyBucketAccessArgs']]]] = None):
        """
        The set of arguments for constructing a ObjectStorageKey resource.
        :param pulumi.Input[str] label: The label given to this key. For display purposes only.
        :param pulumi.Input[Sequence[pulumi.Input['ObjectStorageKeyBucketAccessArgs']]] bucket_accesses: Defines this key as a Limited Access Key. Limited Access Keys restrict this Object Storage key’s access to only the bucket(s) declared in this array and define their bucket-level permissions. Not providing this block will not limit this Object Storage Key.
        """
        pulumi.set(__self__, "label", label)
        if bucket_accesses is not None:
            pulumi.set(__self__, "bucket_accesses", bucket_accesses)

    @property
    @pulumi.getter
    def label(self) -> pulumi.Input[str]:
        """
        The label given to this key. For display purposes only.
        """
        return pulumi.get(self, "label")

    @label.setter
    def label(self, value: pulumi.Input[str]):
        pulumi.set(self, "label", value)

    @property
    @pulumi.getter(name="bucketAccesses")
    def bucket_accesses(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ObjectStorageKeyBucketAccessArgs']]]]:
        """
        Defines this key as a Limited Access Key. Limited Access Keys restrict this Object Storage key’s access to only the bucket(s) declared in this array and define their bucket-level permissions. Not providing this block will not limit this Object Storage Key.
        """
        return pulumi.get(self, "bucket_accesses")

    @bucket_accesses.setter
    def bucket_accesses(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ObjectStorageKeyBucketAccessArgs']]]]):
        pulumi.set(self, "bucket_accesses", value)


@pulumi.input_type
class _ObjectStorageKeyState:
    def __init__(__self__, *,
                 access_key: Optional[pulumi.Input[str]] = None,
                 bucket_accesses: Optional[pulumi.Input[Sequence[pulumi.Input['ObjectStorageKeyBucketAccessArgs']]]] = None,
                 label: Optional[pulumi.Input[str]] = None,
                 limited: Optional[pulumi.Input[bool]] = None,
                 secret_key: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ObjectStorageKey resources.
        :param pulumi.Input[str] access_key: This keypair's access key. This is not secret.
        :param pulumi.Input[Sequence[pulumi.Input['ObjectStorageKeyBucketAccessArgs']]] bucket_accesses: Defines this key as a Limited Access Key. Limited Access Keys restrict this Object Storage key’s access to only the bucket(s) declared in this array and define their bucket-level permissions. Not providing this block will not limit this Object Storage Key.
        :param pulumi.Input[str] label: The label given to this key. For display purposes only.
        :param pulumi.Input[bool] limited: Whether or not this key is a limited access key.
        :param pulumi.Input[str] secret_key: This keypair's secret key.
        """
        if access_key is not None:
            pulumi.set(__self__, "access_key", access_key)
        if bucket_accesses is not None:
            pulumi.set(__self__, "bucket_accesses", bucket_accesses)
        if label is not None:
            pulumi.set(__self__, "label", label)
        if limited is not None:
            pulumi.set(__self__, "limited", limited)
        if secret_key is not None:
            pulumi.set(__self__, "secret_key", secret_key)

    @property
    @pulumi.getter(name="accessKey")
    def access_key(self) -> Optional[pulumi.Input[str]]:
        """
        This keypair's access key. This is not secret.
        """
        return pulumi.get(self, "access_key")

    @access_key.setter
    def access_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "access_key", value)

    @property
    @pulumi.getter(name="bucketAccesses")
    def bucket_accesses(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ObjectStorageKeyBucketAccessArgs']]]]:
        """
        Defines this key as a Limited Access Key. Limited Access Keys restrict this Object Storage key’s access to only the bucket(s) declared in this array and define their bucket-level permissions. Not providing this block will not limit this Object Storage Key.
        """
        return pulumi.get(self, "bucket_accesses")

    @bucket_accesses.setter
    def bucket_accesses(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ObjectStorageKeyBucketAccessArgs']]]]):
        pulumi.set(self, "bucket_accesses", value)

    @property
    @pulumi.getter
    def label(self) -> Optional[pulumi.Input[str]]:
        """
        The label given to this key. For display purposes only.
        """
        return pulumi.get(self, "label")

    @label.setter
    def label(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "label", value)

    @property
    @pulumi.getter
    def limited(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether or not this key is a limited access key.
        """
        return pulumi.get(self, "limited")

    @limited.setter
    def limited(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "limited", value)

    @property
    @pulumi.getter(name="secretKey")
    def secret_key(self) -> Optional[pulumi.Input[str]]:
        """
        This keypair's secret key.
        """
        return pulumi.get(self, "secret_key")

    @secret_key.setter
    def secret_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "secret_key", value)


class ObjectStorageKey(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bucket_accesses: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ObjectStorageKeyBucketAccessArgs']]]]] = None,
                 label: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides a Linode Object Storage Key resource. This can be used to create, modify, and delete Linodes Object Storage Keys.

        ## Example Usage

        The following example shows how one might use this resource to create an Object Storage Key.

        ```python
        import pulumi
        import pulumi_linode as linode

        foo = linode.ObjectStorageKey("foo", label="image-access")
        ```
        ## Attributes

        This resource exports the following attributes:

        * `access_key` - This keypair's access key. This is not secret.

        * `secret_key` - This keypair's secret key.

        * `limited` - Whether or not this key is a limited access key.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ObjectStorageKeyBucketAccessArgs']]]] bucket_accesses: Defines this key as a Limited Access Key. Limited Access Keys restrict this Object Storage key’s access to only the bucket(s) declared in this array and define their bucket-level permissions. Not providing this block will not limit this Object Storage Key.
        :param pulumi.Input[str] label: The label given to this key. For display purposes only.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ObjectStorageKeyArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a Linode Object Storage Key resource. This can be used to create, modify, and delete Linodes Object Storage Keys.

        ## Example Usage

        The following example shows how one might use this resource to create an Object Storage Key.

        ```python
        import pulumi
        import pulumi_linode as linode

        foo = linode.ObjectStorageKey("foo", label="image-access")
        ```
        ## Attributes

        This resource exports the following attributes:

        * `access_key` - This keypair's access key. This is not secret.

        * `secret_key` - This keypair's secret key.

        * `limited` - Whether or not this key is a limited access key.

        :param str resource_name: The name of the resource.
        :param ObjectStorageKeyArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ObjectStorageKeyArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bucket_accesses: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ObjectStorageKeyBucketAccessArgs']]]]] = None,
                 label: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ObjectStorageKeyArgs.__new__(ObjectStorageKeyArgs)

            __props__.__dict__["bucket_accesses"] = bucket_accesses
            if label is None and not opts.urn:
                raise TypeError("Missing required property 'label'")
            __props__.__dict__["label"] = label
            __props__.__dict__["access_key"] = None
            __props__.__dict__["limited"] = None
            __props__.__dict__["secret_key"] = None
        super(ObjectStorageKey, __self__).__init__(
            'linode:index/objectStorageKey:ObjectStorageKey',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            access_key: Optional[pulumi.Input[str]] = None,
            bucket_accesses: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ObjectStorageKeyBucketAccessArgs']]]]] = None,
            label: Optional[pulumi.Input[str]] = None,
            limited: Optional[pulumi.Input[bool]] = None,
            secret_key: Optional[pulumi.Input[str]] = None) -> 'ObjectStorageKey':
        """
        Get an existing ObjectStorageKey resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] access_key: This keypair's access key. This is not secret.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ObjectStorageKeyBucketAccessArgs']]]] bucket_accesses: Defines this key as a Limited Access Key. Limited Access Keys restrict this Object Storage key’s access to only the bucket(s) declared in this array and define their bucket-level permissions. Not providing this block will not limit this Object Storage Key.
        :param pulumi.Input[str] label: The label given to this key. For display purposes only.
        :param pulumi.Input[bool] limited: Whether or not this key is a limited access key.
        :param pulumi.Input[str] secret_key: This keypair's secret key.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ObjectStorageKeyState.__new__(_ObjectStorageKeyState)

        __props__.__dict__["access_key"] = access_key
        __props__.__dict__["bucket_accesses"] = bucket_accesses
        __props__.__dict__["label"] = label
        __props__.__dict__["limited"] = limited
        __props__.__dict__["secret_key"] = secret_key
        return ObjectStorageKey(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="accessKey")
    def access_key(self) -> pulumi.Output[str]:
        """
        This keypair's access key. This is not secret.
        """
        return pulumi.get(self, "access_key")

    @property
    @pulumi.getter(name="bucketAccesses")
    def bucket_accesses(self) -> pulumi.Output[Optional[Sequence['outputs.ObjectStorageKeyBucketAccess']]]:
        """
        Defines this key as a Limited Access Key. Limited Access Keys restrict this Object Storage key’s access to only the bucket(s) declared in this array and define their bucket-level permissions. Not providing this block will not limit this Object Storage Key.
        """
        return pulumi.get(self, "bucket_accesses")

    @property
    @pulumi.getter
    def label(self) -> pulumi.Output[str]:
        """
        The label given to this key. For display purposes only.
        """
        return pulumi.get(self, "label")

    @property
    @pulumi.getter
    def limited(self) -> pulumi.Output[bool]:
        """
        Whether or not this key is a limited access key.
        """
        return pulumi.get(self, "limited")

    @property
    @pulumi.getter(name="secretKey")
    def secret_key(self) -> pulumi.Output[str]:
        """
        This keypair's secret key.
        """
        return pulumi.get(self, "secret_key")

