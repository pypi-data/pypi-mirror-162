import copy
from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List


async def update_web_acl(
    hub,
    ctx,
    name: str,
    raw_resource: Dict[str, Any],
    resource_parameters: Dict[str, None],
    scope: str,
    resource_id: str,
    lock_token: str,
):
    """

    Args:
        hub:
        ctx:
        name: Name of resource going to update.
        raw_resource: Old state of resource or existing resource details.
        resource_parameters: Parameters from sls file
        scope: Specifies whether this is for an Amazon CloudFront distribution or for a regional application.
        resource_id: The unique identifier for the web ACL.
        lock_token: A token used for optimistic locking.

    Returns:
        {"result": True|False, "comment": ("A tuple",), "ret": {}}
    """

    parameters = OrderedDict(
        {
            "Name": "name",
            "DefaultAction": "default_action",
            "VisibilityConfig": "visibility_config",
            "Description": "description",
            "Rules": "rules",
            "CustomResponseBodies": "custom_response_bodies",
            "CaptchaConfig": "captcha_config",
        }
    )
    parameters_to_update = {}
    result = dict(comment=(), result=True, ret=None)
    resource_parameters.pop("Tags", None)

    for key, value in resource_parameters.items():
        if value is None or value == raw_resource[key]:
            continue
        parameters_to_update[key] = resource_parameters[key]

    if parameters_to_update:
        if not ctx.get("test", False):
            update_ret = await hub.exec.boto3.client.wafv2.update_web_acl(
                ctx,
                Scope=scope,
                Id=resource_id,
                LockToken=lock_token,
                **resource_parameters,
            )
            if not update_ret["result"]:
                result["comment"] = update_ret["comment"]
                result["result"] = False
                return result
            result["comment"] = result["comment"] + (f"Updated '{name}'",)

        result["ret"] = {}
        for parameter_raw, parameter_present in parameters.items():
            if parameter_raw in parameters_to_update:
                result["ret"][parameter_present] = parameters_to_update[parameter_raw]

    return result


async def update_web_acl_tags(
    hub,
    ctx,
    web_acl_arn,
    old_tags: List[Dict[str, Any]] or Dict[str, Any],
    new_tags: List[Dict[str, Any]] or Dict[str, Any],
):
    """
    Update tags of Web ACL resources

    Args:
        hub:
        ctx:
        web_acl_arn: aws resource arn
        old_tags: list of old tags in the format of [{"Key": tag-key, "Value": tag-value}] or dict in the format of
         {tag-key: tag-value}
        new_tags: list of new tags in the format of [{"Key": tag-key, "Value": tag-value}] or dict in the format of
         {tag-key: tag-value}. If this value is None, the function will do no operation on tags.


    Returns:
        {"result": True|False, "comment": "A message", "ret": dict of updated tags}

    """

    tags_to_add = {}
    tags_to_remove = {}
    if isinstance(old_tags, List):
        old_tags = hub.tool.aws.tag_utils.convert_tag_list_to_dict(old_tags)
    if isinstance(new_tags, List):
        new_tags = hub.tool.aws.tag_utils.convert_tag_list_to_dict(new_tags)
    if new_tags is not None:
        tags_to_remove, tags_to_add = hub.tool.aws.tag_utils.diff_tags_dict(
            old_tags=old_tags, new_tags=new_tags
        )
    result = dict(comment=(), result=True, ret={})
    if (not tags_to_remove) and (not tags_to_add):
        result["ret"] = copy.deepcopy(old_tags if old_tags else {})
        return result

    if tags_to_remove:
        if not ctx.get("test", False):
            delete_ret = await hub.exec.boto3.client.wafv2.untag_resource(
                ctx, ResourceARN=web_acl_arn, TagKeys=list(tags_to_remove)
            )
            if not delete_ret["result"]:
                result["comment"] = delete_ret["comment"]
                result["result"] = False
                return result

    if tags_to_add:
        if not ctx.get("test", False):
            add_ret = await hub.exec.boto3.client.wafv2.tag_resource(
                ctx,
                ResourceARN=web_acl_arn,
                Tags=hub.tool.aws.tag_utils.convert_tag_dict_to_list(tags_to_add),
            )
            if not add_ret["result"]:
                result["comment"] = add_ret["comment"]
                result["result"] = False
                return result

    result["ret"] = new_tags
    result["comment"] = hub.tool.aws.comment_utils.update_tags_comment(
        tags_to_remove=tags_to_remove, tags_to_add=tags_to_add
    )
    return result
