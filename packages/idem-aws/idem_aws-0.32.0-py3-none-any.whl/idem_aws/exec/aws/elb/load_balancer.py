from typing import Dict


async def get(
    hub,
    ctx,
    resource_id: str,
) -> Dict:
    """
    Pass required params to get a ElasticLoadBalancing Load Balancer resource.

    Args:
        resource_id(Text): The name of the ElasticLoadBalancing Load Balancer. This name must be unique
            within your set of load balancers for the region, must have a maximum of 32 characters,

    Returns:
        {"result": True|False, "comment": A message List, "ret": None}

    """
    result = dict(comment=[], ret=None, result=True)
    ret = await hub.tool.aws.elb.load_balancer.search_raw(
        ctx=ctx, resource_id=resource_id
    )
    if not ret["result"]:
        if "LoadBalancerNotFound" in str(ret["comment"]):
            result["comment"].append(
                hub.tool.aws.comment_utils.get_empty_comment(
                    resource_type="aws.elb.load_balancer", name=resource_id
                )
            )
            result["comment"] += ret["comment"]
            return result
        result["comment"] += ret["comment"]
        result["result"] = False
        return result
    if not ret["ret"]["LoadBalancerDescriptions"]:
        result["comment"].append(
            hub.tool.aws.comment_utils.get_empty_comment(
                resource_type="aws.elb.load_balancer", name=resource_id
            )
        )
        return result

    tags = attributes = []
    tags_ret = await hub.exec.boto3.client.elb.describe_tags(
        ctx, LoadBalancerNames=[resource_id]
    )
    if not tags_ret["result"]:
        result["comment"] = list(tags_ret["comment"])
        result["result"] = False
        return result
    else:
        if tags_ret.get("ret") and tags_ret.get("ret")["TagDescriptions"]:
            tags = (tags_ret["ret"]["TagDescriptions"][0]).get("Tags")

    attributes_ret = await hub.exec.boto3.client.elb.describe_load_balancer_attributes(
        ctx, LoadBalancerName=resource_id
    )
    if not attributes_ret["result"]:
        result["comment"] = list(attributes_ret["comment"])
        result["result"] = False
        return result
    else:
        if attributes_ret.get("ret") and attributes_ret.get("ret").get(
            "LoadBalancerAttributes"
        ):
            attributes = attributes_ret["ret"].get("LoadBalancerAttributes")

    result[
        "ret"
    ] = hub.tool.aws.elb.conversion_utils.convert_raw_load_balancer_to_present(
        raw_resource=ret["ret"]["LoadBalancerDescriptions"][0],
        idem_resource_name=resource_id,
        tags=hub.tool.aws.tag_utils.convert_tag_list_to_dict(tags),
        attributes=attributes,
    )
    return result
