from typing import Dict
from typing import List


async def search_raw(
    hub,
    ctx,
    filters: List = None,
    resource_id: str = None,
) -> Dict:
    """
    Fetch one or more VPC peering connections from AWS.
    The return will be in the same format as what the boto3 api returns.

    Args:
        resource_id(string, optional): AWS VPC peering connection id to identify the resource.
        filters(list, optional): One or more filters: for example, tag :<key>, tag-key.
            A complete list of filters can be found at
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_vpc_peering_connections

    Returns:
        {"result": True|False, "comment": A message List, "ret": Dict}

    """
    result = dict(comment=[], ret=None, result=True)
    syntax_validation = hub.tool.aws.search_utils.search_filter_syntax_validation(
        filters=filters
    )
    if not syntax_validation["result"]:
        result["comment"] = list(syntax_validation["comment"])
        return result
    boto3_filter = hub.tool.aws.search_utils.convert_search_filter_to_boto3(
        filters=filters
    )
    ret = await hub.exec.boto3.client.ec2.describe_vpc_peering_connections(
        ctx,
        Filters=boto3_filter,
        VpcPeeringConnectionIds=[resource_id] if resource_id else None,
    )
    result["result"] = ret["result"]
    result["comment"] = list(ret["comment"])
    result["ret"] = ret["ret"]

    return result
