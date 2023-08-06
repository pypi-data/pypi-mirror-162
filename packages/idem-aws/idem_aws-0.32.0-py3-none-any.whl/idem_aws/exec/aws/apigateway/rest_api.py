import copy
from typing import Any
from typing import Dict


async def update_rest_api(
    hub, ctx, old_state: Dict[str, Any], updateable_resource_parameters: Dict[str, Any]
):
    """
    Updates an AWS API Gateway API resource.

    Args:
        hub: required for functions in hub.
        ctx: context.
        old_state(Dict): Previous state of the rest_api resource
        raw_resource(Dict): Existing resource parameters in Amazon Web Services.
        updateable_resource_parameters(Dict): Parameters from SLS file.

    Returns:
        Dict[str, Any]
    """
    result = dict(comment=(), result=True, ret=None)
    patch_operations = []

    new_state = copy.deepcopy(old_state)
    resource_updated = False
    for key, value in updateable_resource_parameters.items():
        if value is not None:
            if key == "endpoint_configuration":
                if value["types"][0] != old_state["endpoint_configuration"]["types"][0]:
                    patch_operations.append(
                        {
                            "op": "replace",
                            "path": f"/endpointConfiguration/types/{old_state['endpoint_configuration']['types'][0]}",
                            "value": value["types"][0],
                        }
                    )
                    new_state["endpoint_configuration"]["types"][0] = value["types"][0]
                    resource_updated = True

                old_vpc_endpoint_ids = old_state["endpoint_configuration"].get(
                    "vpcEndpointIds", []
                )
                new_vpc_endpoint_ids = value.get("vpcEndpointIds", [])
                if not (
                    hub.tool.aws.state_comparison_utils.are_lists_identical(
                        old_vpc_endpoint_ids,
                        new_vpc_endpoint_ids,
                    )
                ):
                    endpoints_to_remove = list(
                        set(old_vpc_endpoint_ids).difference(set(new_vpc_endpoint_ids))
                    )
                    endpoints_to_add = list(
                        set(new_vpc_endpoint_ids).difference(set(old_vpc_endpoint_ids))
                    )
                    if endpoints_to_remove:
                        patch_operations.append(
                            {
                                "op": "remove",
                                "path": f"/endpointConfiguration/vpcEndpointIds",
                                "value": ",".join(endpoints_to_remove),
                            }
                        )
                    if endpoints_to_add:
                        patch_operations.append(
                            {
                                "op": "add",
                                "path": f"/endpointConfiguration/vpcEndpointIds",
                                "value": ",".join(endpoints_to_add),
                            }
                        )

                    new_state["endpoint_configuration"][
                        "vpcEndpointIds"
                    ] = new_vpc_endpoint_ids
                    resource_updated = True
            elif (
                isinstance(value, list)
                and not hub.tool.aws.state_comparison_utils.are_lists_identical(
                    value,
                    old_state.get(key, []),
                )
                or value != old_state[key]
            ):
                if old_state.get(key):
                    patch_operations.append(
                        {
                            "op": "replace",
                            "path": f"/{key}",
                            "value": str(value)
                            if not isinstance(value, list)
                            else ",".join(value),
                        }
                    )
                else:
                    patch_operations.append(
                        {
                            "op": "add",
                            "path": f"/{key}",
                            "value": str(value)
                            if not isinstance(value, list)
                            else ",".join(value),
                        }
                    )
                new_state[key] = value
                resource_updated = True
    if ctx.get("test", False):
        if resource_updated:
            result["comment"] = hub.tool.aws.comment_utils.would_update_comment(
                resource_type="aws.apigateway.rest_api", name=old_state["name"]
            )
            result["ret"] = new_state
        else:
            result["comment"] = hub.tool.aws.comment_utils.already_exists_comment(
                resource_type="aws.apigateway.rest_api", name=old_state["name"]
            )
        return result

    if resource_updated:
        update_ret = await hub.exec.boto3.client.apigateway.update_rest_api(
            ctx, restApiId=old_state["resource_id"], patchOperations=patch_operations
        )
        if not update_ret["result"]:
            result["result"] = False
            result["comment"] = update_ret["comment"]
            return result
        else:
            result["comment"] = hub.tool.aws.comment_utils.update_comment(
                resource_type="aws.apigateway.rest_api", name=old_state["name"]
            )
            result["ret"] = new_state

    else:
        result["comment"] = hub.tool.aws.comment_utils.already_exists_comment(
            resource_type="aws.apigateway.rest_api", name=old_state["name"]
        )

    return result
