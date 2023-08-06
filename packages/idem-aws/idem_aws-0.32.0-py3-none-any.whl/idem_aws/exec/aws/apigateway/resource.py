import copy
from typing import Any
from typing import Dict


async def get(hub, ctx, name: str, resource_id: str, rest_api_id: str):
    """
    Get an API Gateway Resource from AWS.
    Args:
        hub:
        ctx:
        name(string): An Idem name of the API Gateway Resource.
        resource_id(string): AWS Resource id. Defaults to None.
        rest_api_id(string): AWS rest_api id of the associated RestApi.

    """

    result = dict(comment=[], ret=None, result=True)
    before = await hub.exec.boto3.client.apigateway.get_resource(
        ctx, resourceId=resource_id, restApiId=rest_api_id
    )

    if not before["result"]:
        if "NotFoundException" in str(before["comment"]):
            result["comment"].append(
                hub.tool.aws.comment_utils.get_empty_comment(
                    resource_type="aws.api.gateway", name=name
                )
            )
            result["comment"] += list(before["comment"])
            return result
        result["result"] = False
        result["comment"] = before["comment"]
        return result

    if before["ret"]:
        result["ret"] = before["ret"]

    return result


async def update_resource(
    hub, ctx, old_state: Dict[str, Any], update_parameters: Dict[str, any]
):
    r"""

    Updates an API Gateway Resource

    Args:
        hub:
        ctx:
        old_state(Dict): Previous state of resource
        update_parameters(Dict): Parameters from SLS File

    Returns:
        Dict[str, Any]

    """

    result = dict(comment=(), result=True, ret=None)
    patch_ops = []

    new_state = copy.deepcopy(old_state)
    updated = False

    for key, value in update_parameters.items():
        if key == "parent_id":
            key_final = "parentId"
        else:
            key_final = "pathPart"

        if old_state.get(key) and value != old_state.get(key):
            patch_ops.append(
                {
                    "op": "replace",
                    "path": f"/{key_final}",
                    "value": str(value)
                    if not isinstance(value, list)
                    else ",".join(value),
                }
            )
            updated = True

        elif old_state.get(key) is None:
            patch_ops.append(
                {
                    "op": "add",
                    "path": f"/{key_final}",
                    "value": str(value)
                    if not isinstance(value, list)
                    else ",".join(value),
                }
            )

            new_state[key] = value
            updated = True

    if ctx.get("test", False):
        if updated:
            result["comment"] = hub.tool.aws.comment_utils.would_update_comment(
                resource_type="aws.apigateway.resource", name=old_state["name"]
            )
            result["ret"] = new_state
        else:
            result["comment"] = hub.tool.aws.comment_utils.already_exists_comment(
                resource_type="aws.apigateway.resource", name=old_state["name"]
            )
        return result

    if updated:
        update_ret = await hub.exec.boto3.client.apigateway.update_resource(
            ctx,
            restApiId=old_state["rest_api_id"],
            resourceId=old_state["resource_id"],
            patchOperations=patch_ops,
        )
        if not update_ret["result"]:
            result["result"] = False
            result["comment"] = update_ret["comment"]
            return result
        else:
            result["comment"] = hub.tool.aws.comment_utils.update_comment(
                resource_type="aws.apigateway.resource", name=old_state["name"]
            )
            result["ret"] = new_state
    else:
        result["comment"] = hub.tool.aws.comment_utils.already_exists_comment(
            resource_type="aws.apigateway.resource", name=old_state["name"]
        )

    return result
