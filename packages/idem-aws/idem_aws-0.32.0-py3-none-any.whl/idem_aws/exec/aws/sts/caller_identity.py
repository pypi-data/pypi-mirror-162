from typing import Any
from typing import Dict


async def get_caller_identity(hub, ctx) -> Dict[str, Any]:
    """
    Return the caller identity details of IAM user whose credential are used invoke the operation.
    """
    ret = dict(result=True, ret={}, comment="")
    caller_identity = await hub.exec.boto3.client.sts.get_caller_identity(ctx)

    ret["result"] = caller_identity.result
    ret["comment"] = caller_identity.comment
    if caller_identity.result:
        ret["ret"]["UserId"] = caller_identity.ret["UserId"]
        ret["ret"]["Account"] = caller_identity.ret["Account"]
        ret["ret"]["Arn"] = caller_identity.ret["Arn"]
    return ret
