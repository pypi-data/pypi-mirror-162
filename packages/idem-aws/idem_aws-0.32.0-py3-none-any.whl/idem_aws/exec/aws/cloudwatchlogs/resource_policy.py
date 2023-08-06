from typing import Any
from typing import Dict


async def get_resource_policy(
    hub,
    ctx,
    name: str,
) -> Dict[str, Any]:
    r"""
    Returns resource policy object for the given resource policy name
    Args:
        hub:
        ctx:
        name(Text): Name of the new policy. An Idem name of the resource

    Returns:
        Dict[str, Any]
    """
    result = dict(comment=(), result=True, ret=None)
    ret = await hub.exec.boto3.client.logs.describe_resource_policies(ctx)
    result["result"] = ret["result"]
    if not result["result"]:
        result["comment"] = result["comment"] + ret["comment"]
        return result
    if ret["ret"]:
        resource_policies = ret["ret"]["resourcePolicies"]
        for resource_policy in resource_policies:
            if resource_policy.get("policyName") == name:
                result["ret"] = resource_policy
                break
    return result
