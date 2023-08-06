import copy
from typing import Any
from typing import Dict
from typing import List


async def get(
    hub,
    ctx,
    resource_id: str,
    name: str = None,
):
    # TODO: will revisit this part later to improve building the get() call when multiple params are used to fetch a resource from AWS
    """
    Get an API Gateway Method from AWS.
    Args:
        hub:
        ctx:
        resource_id(string): Idem Resource ID that is generated once the resource is created.
        name(string, optional): An Idem name of the API Gateway Method.

    """

    result = dict(comment=[], ret=None, result=True)
    get_method = await hub.exec.boto3.client.apigateway.get_method(
        ctx,
        restApiId=resource_id.split("-")[0],
        resourceId=resource_id.split("-")[1],
        httpMethod=resource_id.split("-")[2],
    )

    if not get_method["result"]:
        if "NotFoundException" in str(get_method["comment"]):
            result["comment"].append(
                hub.tool.aws.comment_utils.get_empty_comment(
                    resource_type="aws.apigateway.method", name=name
                )
            )
            result["comment"] += list(get_method["comment"])
            return result
        result["comment"] += list(get_method["comment"])
        result["result"] = False
        return result
    if not get_method["ret"]:
        result["comment"].append(
            hub.tool.aws.comment_utils.get_empty_comment(
                resource_type="aws.apigateway.method", name=name
            )
        )
        return result

    if get_method["ret"]:
        result["ret"] = hub.tool.aws.apigateway.method.convert_raw_method_to_present(
            raw_resource=get_method["ret"],
            idem_resource_name=name,
            resource_id=resource_id,
        )

    return result


async def update(
    hub,
    ctx,
    old_state: Dict[str, Any],
    update_parameters: Dict[str, Any],
):
    r"""

    Updates an API Gateway Method

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
        if key == "api_key_required":
            key_final = "apiKeyRequired"
        elif key == "authorization_type":
            key_final = "authorizationType"
        elif key == "http_method":
            key_final = "httpMethod"

        if value != old_state.get(key):
            patch_ops.append(
                {
                    "op": "replace",
                    "path": f"/{key_final}",
                    "value": str(value)
                    if not isinstance(value, List)
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
                    if not isinstance(value, List)
                    else ",".join(value),
                }
            )
            new_state[key] = value
            updated = True

    if ctx.get("test", False):
        if updated:
            result["comment"] = hub.tool.aws.comment_utils.would_update_comment(
                resource_type="aws.apigateway.method", name=old_state["name"]
            )
            result["ret"] = new_state
        else:
            result["comment"] = hub.tool.aws.comment_utils.already_exists_comment(
                resource_type="aws.apigateway.method", name=old_state["name"]
            )
        return result

    if updated:
        update_ret = await hub.exec.boto3.client.apigateway.update_method(
            ctx,
            restApiId=old_state["rest_api_id"],
            resourceId=old_state["parent_resource_id"],
            httpMethod=old_state["http_method"],
            patchOperations=patch_ops,
        )
        if not update_ret["result"]:
            result["result"] = False
            result["comment"] = update_ret["comment"]
            return result
        else:
            result["comment"] = hub.tool.aws.comment_utils.update_comment(
                resource_type="aws.apigateway.method", name=old_state["name"]
            )
            result["ret"] = new_state
    else:
        result["comment"] = hub.tool.aws.comment_utils.already_exists_comment(
            resource_type="aws.apigateway.method", name=old_state["name"]
        )

    return result
