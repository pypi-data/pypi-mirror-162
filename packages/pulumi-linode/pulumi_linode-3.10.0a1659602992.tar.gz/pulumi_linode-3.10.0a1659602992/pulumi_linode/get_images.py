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

__all__ = [
    'GetImagesResult',
    'AwaitableGetImagesResult',
    'get_images',
    'get_images_output',
]

@pulumi.output_type
class GetImagesResult:
    """
    A collection of values returned by getImages.
    """
    def __init__(__self__, filters=None, id=None, images=None, latest=None, order=None, order_by=None):
        if filters and not isinstance(filters, list):
            raise TypeError("Expected argument 'filters' to be a list")
        pulumi.set(__self__, "filters", filters)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if images and not isinstance(images, list):
            raise TypeError("Expected argument 'images' to be a list")
        pulumi.set(__self__, "images", images)
        if latest and not isinstance(latest, bool):
            raise TypeError("Expected argument 'latest' to be a bool")
        pulumi.set(__self__, "latest", latest)
        if order and not isinstance(order, str):
            raise TypeError("Expected argument 'order' to be a str")
        pulumi.set(__self__, "order", order)
        if order_by and not isinstance(order_by, str):
            raise TypeError("Expected argument 'order_by' to be a str")
        pulumi.set(__self__, "order_by", order_by)

    @property
    @pulumi.getter
    def filters(self) -> Optional[Sequence['outputs.GetImagesFilterResult']]:
        return pulumi.get(self, "filters")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def images(self) -> Sequence['outputs.GetImagesImageResult']:
        return pulumi.get(self, "images")

    @property
    @pulumi.getter
    def latest(self) -> Optional[bool]:
        return pulumi.get(self, "latest")

    @property
    @pulumi.getter
    def order(self) -> Optional[str]:
        return pulumi.get(self, "order")

    @property
    @pulumi.getter(name="orderBy")
    def order_by(self) -> Optional[str]:
        return pulumi.get(self, "order_by")


class AwaitableGetImagesResult(GetImagesResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetImagesResult(
            filters=self.filters,
            id=self.id,
            images=self.images,
            latest=self.latest,
            order=self.order,
            order_by=self.order_by)


def get_images(filters: Optional[Sequence[pulumi.InputType['GetImagesFilterArgs']]] = None,
               latest: Optional[bool] = None,
               order: Optional[str] = None,
               order_by: Optional[str] = None,
               opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetImagesResult:
    """
    Provides information about Linode images that match a set of filters.

    ## Example Usage

    Get information about all Linode images with a certain label and visibility:

    ```python
    import pulumi
    import pulumi_linode as linode

    specific_images = linode.get_images(filters=[
        linode.GetImagesFilterArgs(
            name="label",
            values=["Debian 8"],
        ),
        linode.GetImagesFilterArgs(
            name="is_public",
            values=["true"],
        ),
    ])
    ```

    Get information about all Linode images associated with the current token:

    ```python
    import pulumi
    import pulumi_linode as linode

    all_images = linode.get_images()
    ```
    ## Attributes

    Each Linode image will be stored in the `images` attribute and will export the following attributes:

    * `id` - The unique ID of this Image.  The ID of private images begin with `private/` followed by the numeric identifier of the private image, for example `private/12345`.

    * `label` - A short description of the Image.

    * `created` - When this Image was created.

    * `created_by` - The name of the User who created this Image, or "linode" for official Images.

    * `deprecated` - Whether or not this Image is deprecated. Will only be true for deprecated public Images.

    * `description` - A detailed description of this Image.

    * `is_public` - True if the Image is public.

    * `size` - The minimum size this Image needs to deploy. Size is in MB. example: 2500

    * `status` - The current status of this image. (`creating`, `pending_upload`, `available`)

    * `type` - How the Image was created. Manual Images can be created at any time. "Automatic" Images are created automatically from a deleted Linode. (`manual`, `automatic`)

    * `vendor` - The upstream distribution vendor. `None` for private Images.

    ## Filterable Fields

    * `created_by`

    * `deprecated`

    * `description`

    * `id`

    * `is_public`

    * `label`

    * `size`

    * `status`

    * `vendor`


    :param bool latest: If true, only the latest image will be returned. Images without a valid `created` field are not included in the result.
    :param str order: The order in which results should be returned. (`asc`, `desc`; default `asc`)
    :param str order_by: The attribute to order the results by. See the Filterable Fields section for a list of valid fields.
    """
    __args__ = dict()
    __args__['filters'] = filters
    __args__['latest'] = latest
    __args__['order'] = order
    __args__['orderBy'] = order_by
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('linode:index/getImages:getImages', __args__, opts=opts, typ=GetImagesResult).value

    return AwaitableGetImagesResult(
        filters=__ret__.filters,
        id=__ret__.id,
        images=__ret__.images,
        latest=__ret__.latest,
        order=__ret__.order,
        order_by=__ret__.order_by)


@_utilities.lift_output_func(get_images)
def get_images_output(filters: Optional[pulumi.Input[Optional[Sequence[pulumi.InputType['GetImagesFilterArgs']]]]] = None,
                      latest: Optional[pulumi.Input[Optional[bool]]] = None,
                      order: Optional[pulumi.Input[Optional[str]]] = None,
                      order_by: Optional[pulumi.Input[Optional[str]]] = None,
                      opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetImagesResult]:
    """
    Provides information about Linode images that match a set of filters.

    ## Example Usage

    Get information about all Linode images with a certain label and visibility:

    ```python
    import pulumi
    import pulumi_linode as linode

    specific_images = linode.get_images(filters=[
        linode.GetImagesFilterArgs(
            name="label",
            values=["Debian 8"],
        ),
        linode.GetImagesFilterArgs(
            name="is_public",
            values=["true"],
        ),
    ])
    ```

    Get information about all Linode images associated with the current token:

    ```python
    import pulumi
    import pulumi_linode as linode

    all_images = linode.get_images()
    ```
    ## Attributes

    Each Linode image will be stored in the `images` attribute and will export the following attributes:

    * `id` - The unique ID of this Image.  The ID of private images begin with `private/` followed by the numeric identifier of the private image, for example `private/12345`.

    * `label` - A short description of the Image.

    * `created` - When this Image was created.

    * `created_by` - The name of the User who created this Image, or "linode" for official Images.

    * `deprecated` - Whether or not this Image is deprecated. Will only be true for deprecated public Images.

    * `description` - A detailed description of this Image.

    * `is_public` - True if the Image is public.

    * `size` - The minimum size this Image needs to deploy. Size is in MB. example: 2500

    * `status` - The current status of this image. (`creating`, `pending_upload`, `available`)

    * `type` - How the Image was created. Manual Images can be created at any time. "Automatic" Images are created automatically from a deleted Linode. (`manual`, `automatic`)

    * `vendor` - The upstream distribution vendor. `None` for private Images.

    ## Filterable Fields

    * `created_by`

    * `deprecated`

    * `description`

    * `id`

    * `is_public`

    * `label`

    * `size`

    * `status`

    * `vendor`


    :param bool latest: If true, only the latest image will be returned. Images without a valid `created` field are not included in the result.
    :param str order: The order in which results should be returned. (`asc`, `desc`; default `asc`)
    :param str order_by: The attribute to order the results by. See the Filterable Fields section for a list of valid fields.
    """
    ...
