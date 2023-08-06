from typing import Dict
from typing import List


async def get(
    hub,
    ctx,
    name: str,
    resource_id: str = None,
    filters: List = None,
) -> Dict:
    """
    Use an un-managed VPC peering connection as a data-source. Supply one of the inputs as the filter.

    Args:
        name(string): The name of the Idem state.
        resource_id(string, optional): AWS VPC peering connection id to identify the resource.
        filters(list, optional): One or more filters: for example, tag :<key>, tag-key.
            A complete list of filters can be found at
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_vpc_peering_connections

    """
    result = dict(comment=[], ret=None, result=True)
    ret = await hub.tool.aws.ec2.vpc_peering_connection_utils.search_raw(
        ctx=ctx,
        resource_id=resource_id,
        filters=filters,
    )
    if not ret["result"]:
        if "InvalidVpcPeeringConnectionID.NotFound" in str(ret["comment"]):
            result["comment"].append(
                hub.tool.aws.comment_utils.get_empty_comment(
                    resource_type="aws.ec2.vpc_peering_connection", name=name
                )
            )
            result["comment"] += list(ret["comment"])
            return result
        result["comment"] += list(ret["comment"])
        result["result"] = False
        return result
    if not ret["ret"]["VpcPeeringConnections"]:
        result["comment"].append(
            hub.tool.aws.comment_utils.get_empty_comment(
                resource_type="aws.ec2.vpc_peering_connection", name=name
            )
        )
        return result

    resource = ret["ret"]["VpcPeeringConnections"][0]
    if len(ret["ret"]["VpcPeeringConnections"]) > 1:
        result["comment"].append(
            f"More than one aws.ec2.vpc_peering_connection resource was found. "
            f"Use resource {resource.get('VpcPeeringConnectionId')}"
        )

    result[
        "ret"
    ] = hub.tool.aws.ec2.conversion_utils.convert_raw_vpc_peering_connection_to_present(
        raw_resource=resource, idem_resource_name=name
    )

    return result
