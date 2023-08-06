from typing import Dict

"""
Exec functions for AWS API Gateway v2 Authorizer resources.
"""


async def get(hub, ctx, name, resource_id: str, api_id: str) -> Dict:
    """
    Get a single ApiGatewayV2 Authorizer resource from AWS.

    Args:
        name(string): The name of the Idem state.
        resource_id(string): The AWS api gateway v2 Authorizer id.
        api_id(string): The AWS api gateway v2 API id.
    """
    result = dict(comment=[], ret=None, result=True)
    ret = await hub.exec.boto3.client.apigatewayv2.get_authorizer(
        ctx, ApiId=api_id, AuthorizerId=resource_id
    )
    if not ret["result"]:
        if "NotFoundException" in str(ret["comment"]):
            result["comment"].append(
                hub.tool.aws.comment_utils.get_empty_comment(
                    resource_type="aws.apigatewayv2.authorizer", name=name
                )
            )
            result["comment"] += list(ret["comment"])
            return result
        result["comment"] += list(ret["comment"])
        result["result"] = False
        return result
    result[
        "ret"
    ] = hub.tool.aws.apigatewayv2.authorizer.convert_raw_authorizer_to_present(
        api_id=api_id, raw_resource=ret["ret"]
    )
    return result
