from typing import Any
from typing import Dict
from typing import List

__func_alias__ = {"list_": "list"}


async def get(
    hub,
    ctx,
    name,
    resource_id: str = None,
    availability_zone: str = None,
    availability_zone_id: str = None,
    cidr_block: str = None,
    default_for_az: str = None,
    filters: List = None,
    ipv6_cidr_block: str = None,
    status: str = None,
    vpc_id: str = None,
    tags: List[Dict[str, Any]] or Dict[str, str] = None,
) -> Dict:
    """
    Get a single subnet from AWS. If more than one resource is found, the first resource returned from AWS will be used.
    The function returns None when no resource is found.

    Args:
        name(string): The name of the Idem state.
        resource_id(string, optional): AWS subnet id to identify the resource.
        availability_zone(string, optional): The Availability Zone for the subnet.
        availability_zone_id(string, optional): The ID of the Availability Zone for the subnet.
        cidr_block(string, optional): The IPv4 CIDR block of the subnet. The CIDR block you specify must exactly match
         the subnet's CIDR block for information to be returned for the subnet.
        default_for_az(string, optional): Indicate whether the subnet is the default subnet in the Availability Zone.
        filters(List, optional): One or more filters: for example, tag :<key>, tag-key. A complete list of filters can be found at
         https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_subnets
        ipv6_cidr_block(string, optional): An IPv6 CIDR block associated with the subnet.
        status(string, optional): The state of the subnet (pending | available ).
        vpc_id(string, optional): The ID of the VPC for the subnet.
        tags(List or Dict, optional): The list or dict of tags to filter by. For example, to find all resources that have a tag with the key
            "Owner" and the value "TeamA" , specify "tag:Owner" for the Dict key and "TeamA" for the Dict value.
    """
    result = dict(comment=[], ret=None, result=True)
    if isinstance(tags, Dict):
        tags = hub.tool.aws.tag_utils.convert_tag_dict_to_list(tags)
    ret = await hub.tool.aws.ec2.subnet.search_raw(
        ctx=ctx,
        name=name,
        resource_id=resource_id,
        availability_zone=availability_zone,
        availability_zone_id=availability_zone_id,
        cidr_block=cidr_block,
        default_for_az=default_for_az,
        filters=filters,
        ipv6_cidr_block=ipv6_cidr_block,
        status=status,
        vpc_id=vpc_id,
        tags=tags,
    )
    if not ret["result"]:
        if "InvalidSubnetID.NotFound" in str(ret["comment"]):
            result["comment"].append(
                hub.tool.aws.comment_utils.get_empty_comment(
                    resource_type="aws.ec2.subnet", name=name
                )
            )
            result["comment"] += list(ret["comment"])
            return result
        result["comment"] += list(ret["comment"])
        result["result"] = False
        return result
    if not ret["ret"]["Subnets"]:
        result["comment"].append(
            hub.tool.aws.comment_utils.get_empty_comment(
                resource_type="aws.ec2.subnet", name=name
            )
        )
        return result

    resource = ret["ret"]["Subnets"][0]
    if len(ret["ret"]["Subnets"]) > 1:
        result["comment"].append(
            f"More than one aws.ec2.subnet resource was found. Use resource {resource.get('SubnetId')}"
        )
    result["ret"] = hub.tool.aws.ec2.conversion_utils.convert_raw_subnet_to_present(
        raw_resource=resource, idem_resource_name=name
    )

    return result


async def list_(
    hub,
    ctx,
    name,
    availability_zone: str = None,
    availability_zone_id: str = None,
    cidr_block: str = None,
    default_for_az: str = None,
    filters: List = None,
    ipv6_cidr_block: str = None,
    status: str = None,
    vpc_id: str = None,
    tags: List[Dict[str, Any]] or Dict[str, str] = None,
) -> Dict:
    """
    Fetch a list of subnets AWS. The function returns empty list when no resource is found.

    Args:
        name(string): The name of the Idem state.
        availability_zone(string, optional): The Availability Zone for the subnet.
        availability_zone_id(string, optional): The ID of the Availability Zone for the subnet.
        cidr_block(string, optional): The IPv4 CIDR block of the subnet. The CIDR block you specify must exactly match
         the subnet's CIDR block for information to be returned for the subnet.
        default_for_az(string, optional): Indicate whether the subnet is the default subnet in the Availability Zone.
        filters(List, optional): One or more filters: for example, tag :<key>, tag-key. A complete list of filters can be found at
         https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_subnets
        ipv6_cidr_block(string, optional): An IPv6 CIDR block associated with the subnet.
        status(string, optional): The state of the subnet (pending | available ).
        vpc_id(string, optional): The ID of the VPC for the subnet.
        tags(List, optional): The list of tags to filter by. For example, to find all resources that have a tag with the key
            "Owner" and the value "TeamA" , specify "tag:Owner" for the Dict key and "TeamA" for the Dict value.
    """
    result = dict(comment=[], ret=[], result=True)
    if isinstance(tags, Dict):
        tags = hub.tool.aws.tag_utils.convert_tag_dict_to_list(tags)
    ret = await hub.tool.aws.ec2.subnet.search_raw(
        ctx=ctx,
        name=name,
        availability_zone=availability_zone,
        availability_zone_id=availability_zone_id,
        cidr_block=cidr_block,
        default_for_az=default_for_az,
        filters=filters,
        ipv6_cidr_block=ipv6_cidr_block,
        status=status,
        vpc_id=vpc_id,
        tags=tags,
    )
    if not ret["result"]:
        result["comment"] += list(ret["comment"])
        result["result"] = False
        return result
    if not ret["ret"]["Subnets"]:
        result["comment"].append(
            hub.tool.aws.comment_utils.list_empty_comment(
                resource_type="aws.ec2.subnet", name=name
            )
        )
        return result
    for subnet in ret["ret"]["Subnets"]:
        subnet_id = subnet.get("SubnetId")
        result["ret"].append(
            hub.tool.aws.ec2.conversion_utils.convert_raw_subnet_to_present(
                raw_resource=subnet, idem_resource_name=subnet_id
            )
        )
    return result
