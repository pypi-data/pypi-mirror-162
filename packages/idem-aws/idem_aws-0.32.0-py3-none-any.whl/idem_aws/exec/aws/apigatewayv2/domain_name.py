from typing import Dict

"""
Exec functions for AWS API Gateway v2 Domain Name resources.
"""


async def get(hub, ctx, name, resource_id: str) -> Dict:
    """
    Get an API Gateway v2 domain name resource from AWS with the domain name as the resource_id.

    Args:
        name(string): The name of the Idem state.
        resource_id(string): AWS API Gateway v2 domain name.
    """
    result = dict(comment=[], ret=None, result=True)

    ret = await hub.exec.boto3.client.apigatewayv2.get_domain_name(
        ctx, DomainName=resource_id
    )
    if not ret["result"]:
        if "NotFoundException" in str(ret["comment"]):
            result["comment"].append(
                hub.tool.aws.comment_utils.get_empty_comment(
                    resource_type="aws.apigatewayv2.domain_name", name=name
                )
            )
            result["comment"] += list(ret["comment"])
            return result
        result["comment"] += list(ret["comment"])
        result["result"] = False
        return result

    result[
        "ret"
    ] = hub.tool.aws.apigatewayv2.domain_name.convert_raw_domain_name_to_present(
        raw_resource=ret["ret"]
    )
    return result
