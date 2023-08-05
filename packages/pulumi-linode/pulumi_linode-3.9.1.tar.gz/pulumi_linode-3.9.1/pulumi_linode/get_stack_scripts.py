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
    'GetStackScriptsResult',
    'AwaitableGetStackScriptsResult',
    'get_stack_scripts',
    'get_stack_scripts_output',
]

@pulumi.output_type
class GetStackScriptsResult:
    """
    A collection of values returned by getStackScripts.
    """
    def __init__(__self__, filters=None, id=None, latest=None, order=None, order_by=None, stackscripts=None):
        if filters and not isinstance(filters, list):
            raise TypeError("Expected argument 'filters' to be a list")
        pulumi.set(__self__, "filters", filters)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if latest and not isinstance(latest, bool):
            raise TypeError("Expected argument 'latest' to be a bool")
        pulumi.set(__self__, "latest", latest)
        if order and not isinstance(order, str):
            raise TypeError("Expected argument 'order' to be a str")
        pulumi.set(__self__, "order", order)
        if order_by and not isinstance(order_by, str):
            raise TypeError("Expected argument 'order_by' to be a str")
        pulumi.set(__self__, "order_by", order_by)
        if stackscripts and not isinstance(stackscripts, list):
            raise TypeError("Expected argument 'stackscripts' to be a list")
        pulumi.set(__self__, "stackscripts", stackscripts)

    @property
    @pulumi.getter
    def filters(self) -> Optional[Sequence['outputs.GetStackScriptsFilterResult']]:
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

    @property
    @pulumi.getter
    def stackscripts(self) -> Sequence['outputs.GetStackScriptsStackscriptResult']:
        return pulumi.get(self, "stackscripts")


class AwaitableGetStackScriptsResult(GetStackScriptsResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetStackScriptsResult(
            filters=self.filters,
            id=self.id,
            latest=self.latest,
            order=self.order,
            order_by=self.order_by,
            stackscripts=self.stackscripts)


def get_stack_scripts(filters: Optional[Sequence[pulumi.InputType['GetStackScriptsFilterArgs']]] = None,
                      latest: Optional[bool] = None,
                      order: Optional[str] = None,
                      order_by: Optional[str] = None,
                      opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetStackScriptsResult:
    """
    Provides information about Linode StackScripts that match a set of filters.

    **NOTICE:** Due to the large number of public StackScripts, this data source may time out if `is_public` is not filtered on.

    ## Example Usage

    The following example shows how one might use this data source to access information about a Linode StackScript.

    ```python
    import pulumi
    import pulumi_linode as linode

    specific_stackscripts = linode.get_stack_scripts(filters=[
        linode.GetStackScriptsFilterArgs(
            name="label",
            values=["my-cool-stackscript"],
        ),
        linode.GetStackScriptsFilterArgs(
            name="is_public",
            values=["false"],
        ),
    ])
    ```
    ## Attributes

    Each Linode StackScript will be stored in the `stackscripts` attribute and will export the following attributes:

    * `id` - The unique ID of the StackScript.

    * `label` - The StackScript's label is for display purposes only.

    * `script` - The script to execute when provisioning a new Linode with this StackScript.

    * `description` - A description for the StackScript.

    * `rev_note` - This field allows you to add notes for the set of revisions made to this StackScript.

    * `is_public` - This determines whether other users can use your StackScript. Once a StackScript is made public, it cannot be made private.

    * `images` - An array of Image IDs representing the Images that this StackScript is compatible for deploying with.

    * `deployments_active` - Count of currently active, deployed Linodes created from this StackScript.

    * `user_gravatar_id` - The Gravatar ID for the User who created the StackScript.

    * `deployments_total` - The total number of times this StackScript has been deployed.

    * `username` - The User who created the StackScript.

    * `created` - The date this StackScript was created.

    * `updated` - The date this StackScript was updated.

    * `user_defined_fields` - This is a list of fields defined with a special syntax inside this StackScript that allow for supplying customized parameters during deployment.
      
      * `label` - A human-readable label for the field that will serve as the input prompt for entering the value during deployment.
      
      * `name` - The name of the field.
      
      * `example` - An example value for the field.
      
      * `one_of` - A list of acceptable single values for the field.
      
      * `many_of` - A list of acceptable values for the field in any quantity, combination or order.
      
      * `default` - The default value. If not specified, this value will be used.

    ## Filterable Fields

    * `deployments_active`

    * `deployments_total`

    * `description`

    * `images`

    * `is_public`

    * `label`

    * `mine`

    * `rev_note`

    * `username`


    :param bool latest: If true, only the latest StackScript will be returned. StackScripts without a valid `created` field are not included in the result.
    :param str order: The order in which results should be returned. (`asc`, `desc`; default `asc`)
    :param str order_by: The attribute to order the results by. See the Filterable Fields section for a list of valid fields.
    """
    __args__ = dict()
    __args__['filters'] = filters
    __args__['latest'] = latest
    __args__['order'] = order
    __args__['orderBy'] = order_by
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('linode:index/getStackScripts:getStackScripts', __args__, opts=opts, typ=GetStackScriptsResult).value

    return AwaitableGetStackScriptsResult(
        filters=__ret__.filters,
        id=__ret__.id,
        latest=__ret__.latest,
        order=__ret__.order,
        order_by=__ret__.order_by,
        stackscripts=__ret__.stackscripts)


@_utilities.lift_output_func(get_stack_scripts)
def get_stack_scripts_output(filters: Optional[pulumi.Input[Optional[Sequence[pulumi.InputType['GetStackScriptsFilterArgs']]]]] = None,
                             latest: Optional[pulumi.Input[Optional[bool]]] = None,
                             order: Optional[pulumi.Input[Optional[str]]] = None,
                             order_by: Optional[pulumi.Input[Optional[str]]] = None,
                             opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetStackScriptsResult]:
    """
    Provides information about Linode StackScripts that match a set of filters.

    **NOTICE:** Due to the large number of public StackScripts, this data source may time out if `is_public` is not filtered on.

    ## Example Usage

    The following example shows how one might use this data source to access information about a Linode StackScript.

    ```python
    import pulumi
    import pulumi_linode as linode

    specific_stackscripts = linode.get_stack_scripts(filters=[
        linode.GetStackScriptsFilterArgs(
            name="label",
            values=["my-cool-stackscript"],
        ),
        linode.GetStackScriptsFilterArgs(
            name="is_public",
            values=["false"],
        ),
    ])
    ```
    ## Attributes

    Each Linode StackScript will be stored in the `stackscripts` attribute and will export the following attributes:

    * `id` - The unique ID of the StackScript.

    * `label` - The StackScript's label is for display purposes only.

    * `script` - The script to execute when provisioning a new Linode with this StackScript.

    * `description` - A description for the StackScript.

    * `rev_note` - This field allows you to add notes for the set of revisions made to this StackScript.

    * `is_public` - This determines whether other users can use your StackScript. Once a StackScript is made public, it cannot be made private.

    * `images` - An array of Image IDs representing the Images that this StackScript is compatible for deploying with.

    * `deployments_active` - Count of currently active, deployed Linodes created from this StackScript.

    * `user_gravatar_id` - The Gravatar ID for the User who created the StackScript.

    * `deployments_total` - The total number of times this StackScript has been deployed.

    * `username` - The User who created the StackScript.

    * `created` - The date this StackScript was created.

    * `updated` - The date this StackScript was updated.

    * `user_defined_fields` - This is a list of fields defined with a special syntax inside this StackScript that allow for supplying customized parameters during deployment.
      
      * `label` - A human-readable label for the field that will serve as the input prompt for entering the value during deployment.
      
      * `name` - The name of the field.
      
      * `example` - An example value for the field.
      
      * `one_of` - A list of acceptable single values for the field.
      
      * `many_of` - A list of acceptable values for the field in any quantity, combination or order.
      
      * `default` - The default value. If not specified, this value will be used.

    ## Filterable Fields

    * `deployments_active`

    * `deployments_total`

    * `description`

    * `images`

    * `is_public`

    * `label`

    * `mine`

    * `rev_note`

    * `username`


    :param bool latest: If true, only the latest StackScript will be returned. StackScripts without a valid `created` field are not included in the result.
    :param str order: The order in which results should be returned. (`asc`, `desc`; default `asc`)
    :param str order_by: The attribute to order the results by. See the Filterable Fields section for a list of valid fields.
    """
    ...
