import copy
from typing import Any
from typing import Dict

__func_alias__ = {"list_": "list"}


async def get(hub, ctx, name: str, resource_id: str = None):
    """
    Get an IAM role from AWS. Provide role name as input

    Args:
        name(string): An Idem name of the IAM role. Idem will use this as the role name if resource_id is not specified.
        resource_id(string, optional): AWS IAM role name.

    """
    result = dict(comment=[], ret=None, result=True)
    before = await hub.exec.boto3.client.iam.get_role(
        ctx, RoleName=resource_id if resource_id else name
    )
    if not before["result"]:
        if "NoSuchEntity" in str(before["comment"]):
            result["comment"].append(
                hub.tool.aws.comment_utils.get_empty_comment(
                    resource_type="aws.iam.role", name=name
                )
            )
            result["comment"] += list(before["comment"])
            return result
        result["result"] = False
        result["comment"] = before["comment"]
        return result
    before_tag = await hub.exec.boto3.client.iam.list_role_tags(
        ctx, RoleName=resource_id if resource_id else name
    )
    if not before_tag["result"]:
        result["result"] = False
        result["comment"] = before_tag["comment"]
        return result
    if before["ret"].get("Role"):
        before["ret"]["Role"]["Tags"] = before_tag["ret"].get("Tags", [])
        result["ret"] = hub.tool.aws.iam.conversion_utils.convert_raw_role_to_present(
            raw_resource=before["ret"]["Role"]
        )
    return result


async def update_role_tags(
    hub,
    ctx,
    role_name: str,
    old_tags: Dict[str, Any],
    new_tags: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Update tags of AWS IAM Role

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        role_name: AWS IAM role name
        old_tags: dict of old tags
        new_tags: dict of new tags

    Returns:
        {"result": True|False, "comment": Tuple, "ret": Dict of updated tags}
    """
    tags_to_add = {}
    tags_to_remove = {}
    if new_tags is not None:
        tags_to_remove, tags_to_add = hub.tool.aws.tag_utils.diff_tags_dict(
            old_tags=old_tags, new_tags=new_tags
        )
    result = dict(comment=(), result=True, ret=None)
    if (not tags_to_remove) and (not tags_to_add):
        result["ret"] = copy.deepcopy(old_tags if old_tags else {})
        return result
    if tags_to_remove:
        if not ctx.get("test", False):
            delete_ret = await hub.exec.boto3.client.iam.untag_role(
                ctx, RoleName=role_name, TagKeys=list(tags_to_remove.keys())
            )
            if not delete_ret["result"]:
                result["comment"] = delete_ret["comment"]
                result["result"] = False
                return result
    if tags_to_add:
        if not ctx.get("test", False):
            add_ret = await hub.exec.boto3.client.iam.tag_role(
                ctx,
                RoleName=role_name,
                Tags=hub.tool.aws.tag_utils.convert_tag_dict_to_list(tags=tags_to_add),
            )
            if not add_ret["result"]:
                result["comment"] = add_ret["comment"]
                result["result"] = False
                return result
    result["ret"] = new_tags
    if ctx.get("test", False):
        result["comment"] = hub.tool.aws.comment_utils.would_update_tags_comment(
            tags_to_remove=tags_to_remove, tags_to_add=tags_to_add
        )
    else:
        result["comment"] = hub.tool.aws.comment_utils.update_tags_comment(
            tags_to_remove=tags_to_remove, tags_to_add=tags_to_add
        )
    return result


async def update_role(
    hub,
    ctx,
    old_state: Dict[str, Any],
    description: str = None,
    max_session_duration: int = None,
    timeout: Dict = None,
):
    result = dict(comment=(), result=True, ret=None)
    update_payload = {}
    if (description is not None) and old_state.get("description") != description:
        update_payload["Description"] = description
    if (max_session_duration is not None) and old_state.get(
        "max_session_duration"
    ) != max_session_duration:
        update_payload["MaxSessionDuration"] = max_session_duration
    if update_payload:
        if not ctx.get("test", False):
            role_name = old_state.get("name")
            update_ret = await hub.exec.boto3.client.iam.update_role(
                ctx=ctx, RoleName=role_name, **update_payload
            )
            if not update_ret["result"]:
                result["comment"] = update_ret["comment"]
                result["result"] = False
                return result

            waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
                default_delay=1,
                default_max_attempts=40,
                timeout_config=timeout.get("update") if timeout else None,
            )
            hub.log.debug(f"Waiting on updating aws.iam.role '{role_name}'")
            try:
                await hub.tool.boto3.client.wait(
                    ctx,
                    "iam",
                    "role_exists",
                    RoleName=role_name,
                    WaiterConfig=waiter_config,
                )
            except Exception as e:
                result["comment"] = result["comment"] + (str(e),)
                result["result"] = False
        result["ret"] = {}
        if "MaxSessionDuration" in update_payload:
            result["ret"]["max_session_duration"] = update_payload["MaxSessionDuration"]
            result["comment"] = result["comment"] + (
                f"Update max_session_duration: {update_payload['MaxSessionDuration']}",
            )
        if "Description" in update_payload:
            result["ret"]["description"] = update_payload["Description"]
            result["comment"] = result["comment"] + (
                f"Update description: {update_payload['Description']}",
            )
    return result


async def update_policy(
    hub,
    ctx,
    role_name: str,
    policy: str,
):
    # Update role's trust policy (the policy that is embedded within the role)
    result = dict(comment=(), result=True, ret=None)

    if not ctx.get("test", False):
        update_ret = await hub.exec.boto3.client.iam.update_assume_role_policy(
            ctx=ctx, RoleName=role_name, PolicyDocument=policy
        )
        if not update_ret["result"]:
            result["comment"] = update_ret["comment"]
            result["result"] = False
            return result

    result["ret"] = policy
    if ctx.get("test", False):
        result["comment"] = (f"Would update aws.iam.role '{role_name}' policy",)
    else:
        result["comment"] = (f"Updated aws.iam.role '{role_name}' policy",)
    return result
