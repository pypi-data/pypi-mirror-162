from typing import Dict

"""
Exec functions for AWS API Gateway v2 API resources.
"""


async def get(hub, ctx, name, resource_id: str) -> Dict:
    """
    Get an api resource from AWS with the api id as the resource_id.

    Args:
        name(string): The name of the Idem state.
        resource_id(string): AWS API Gateway v2 API id to identify the resource.
    """
    result = dict(comment=[], ret=None, result=True)

    ret = await hub.exec.boto3.client.apigatewayv2.get_api(ctx, ApiId=resource_id)
    if not ret["result"]:
        if "NotFoundException" in str(ret["comment"]):
            result["comment"].append(
                hub.tool.aws.comment_utils.get_empty_comment(
                    resource_type="aws.apigatewayv2.api", name=name
                )
            )
            result["comment"] += list(ret["comment"])
            return result
        result["comment"] += list(ret["comment"])
        result["result"] = False
        return result

    result["ret"] = hub.tool.aws.apigatewayv2.api.convert_raw_api_to_present(
        raw_resource=ret["ret"]
    )
    return result
