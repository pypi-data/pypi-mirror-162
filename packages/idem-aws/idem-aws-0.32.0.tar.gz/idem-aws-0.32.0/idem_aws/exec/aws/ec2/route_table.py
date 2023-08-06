from typing import Dict
from typing import List

__func_alias__ = {"list_": "list"}


async def get(hub, ctx, name, resource_id: str = None, filters: List = None):
    """
    Get a single route table from AWS. If more than one resource is found, the first resource returned from AWS will be used.
    The function returns None when no resource is found.

    Args:
        name(Text): An Idem state name.
        resource_id(Text, optional): AWS route table ID to identify the resource.
        filters(list, optional): One or more filters: for example, tag :<key>, tag-key. A complete list of filters can be found at
         https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_route_tables
    """
    result = dict(comment=[], ret=None, result=True)
    ret = await hub.tool.aws.ec2.route_table.search_raw(
        ctx=ctx, resource_id=resource_id, filters=filters
    )
    if not ret["result"]:
        if "InvalidRouteTableID.NotFound" in str(ret["comment"]):
            result["comment"].append(
                hub.tool.aws.comment_utils.get_empty_comment(
                    resource_type="aws.ec2.route_table", name=name
                )
            )
            result["comment"] += list(ret["comment"])
            return result
        result["comment"] += list(ret["comment"])
        result["result"] = False
        return result
    if not ret["ret"]["RouteTables"]:
        result["comment"].append(
            hub.tool.aws.comment_utils.get_empty_comment(
                resource_type="aws.ec2.route_table", name=name
            )
        )
        return result

    resource = ret["ret"]["RouteTables"][0]
    if len(ret["ret"]["RouteTables"]) > 1:
        result["comment"].append(
            hub.tool.aws.comment_utils.find_more_than_one(
                resource_type="aws.ec2.route_table",
                resource_id=resource.get("RouteTableId"),
            )
        )
    result[
        "ret"
    ] = hub.tool.aws.ec2.conversion_utils.convert_raw_route_table_to_present(
        raw_resource=resource, idem_resource_name=name
    )

    return result


async def list_(hub, ctx, name, filters: List = None) -> Dict:
    """
    Fetch a list of route table from AWS. The function returns empty list when no resource is found.

    Args:
        name(Text): An Idem state name.
        filters(list, optional): One or more filters: for example, tag :<key>, tag-key. A complete list of filters can be found at
         https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_route_tables
    """
    result = dict(comment=[], ret=[], result=True)
    ret = await hub.tool.aws.ec2.route_table.search_raw(ctx=ctx, filters=filters)
    if not ret["result"]:
        result["comment"] += list(ret["comment"])
        result["result"] = False
        return result
    if not ret["ret"]["RouteTables"]:
        result["comment"].append(
            hub.tool.aws.comment_utils.list_empty_comment(
                resource_type="aws.ec2.route_table", name=name
            )
        )
        return result
    for resource in ret["ret"]["RouteTables"]:
        resource_id = resource.get("RouteTableId")
        result["ret"].append(
            hub.tool.aws.ec2.conversion_utils.convert_raw_route_table_to_present(
                raw_resource=resource, idem_resource_name=resource_id
            )
        )
    return result


async def update_routes(
    hub,
    ctx,
    route_table_id: str,
    old_routes: List = None,
    new_routes: List = None,
):
    """
    Update routes of a route table. This function compares the existing(old) routes of route table with new routes.
    routes that are in the new route table but not in the old
    route table will be associated to route table. routes that are in the
    old route table  but not in the new route table will be disassociated from transit route table.

    Args:
        route_table_id(Text): The AWS resource id of the existing route table
        old_routes(List):  routes of existing route table
        new_routes(List): new routes to update

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """
    result = dict(comment=[], result=True, ret=None)

    # compare old_routes if routes are modified
    if new_routes is []:
        result["result"] = False
        result["comment"].append(
            "Route Table routes cannot be None. There should be at least one route in Route Table"
        )
        return result
    elif new_routes is not None:
        routes_to_modify = (
            hub.tool.aws.ec2.route_table.get_route_table_routes_modifications(
                old_routes, new_routes
            )
        )
        if not routes_to_modify["result"]:
            result["comment"] = routes_to_modify["comment"]
            result["result"] = False
            return result
        routes_to_add = routes_to_modify["routes_to_add"]
        routes_to_delete = routes_to_modify["routes_to_delete"]
        routes_to_replace = routes_to_modify["routes_to_replace"]

        if not ctx.get("test", False):
            if routes_to_delete:
                for route_to_delete in routes_to_delete:
                    ret = await hub.exec.boto3.client.ec2.delete_route(
                        ctx, RouteTableId=route_table_id, **route_to_delete
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + list(ret["comment"])
                        result["result"] = False
                        return result
                result["comment"].append(f"Deleted Routes: {routes_to_delete}")
            if routes_to_replace:
                for route_to_replace in routes_to_replace:
                    ret = await hub.exec.boto3.client.ec2.replace_route(
                        ctx, RouteTableId=route_table_id, **route_to_replace
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + list(ret["comment"])
                        result["result"] = False
                        return result
                result["comment"].append(f"Replace Routes: {routes_to_replace}")
            if routes_to_add:
                for route_to_add in routes_to_add:
                    ret = await hub.exec.boto3.client.ec2.create_route(
                        ctx, RouteTableId=route_table_id, **route_to_add
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + list(ret["comment"])
                        result["result"] = False
                        return result
                result["comment"].append(f"Added Routes: {routes_to_add}")
        if routes_to_add or routes_to_replace or routes_to_delete:
            result["comment"].append(f"Updated route table {route_table_id}")
    result["ret"] = {"routes": new_routes}
    return result
