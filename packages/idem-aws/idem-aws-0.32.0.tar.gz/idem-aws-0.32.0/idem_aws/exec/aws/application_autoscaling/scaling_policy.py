from typing import Dict
from typing import List


async def get(
    hub,
    ctx,
    name,
    service_namespace: str,
    scaling_resource_id: str = None,
    policy_names: List[str] = None,
    scalable_dimension: str = None,
) -> Dict:
    """
    Use an un-managed scaling policy as a data-source. Supply one of the inputs as the filter.

    Args:
        name(Text): The name of the Idem state.
        service_namespace(Text): The namespace of the Amazon Web Services service that provides the resource. For a resource
            provided by your own application or service, use custom-resource instead.
        scaling_resource_id(Text, optional): The identifier of the resource associated with the scaling policy. This string
            consists of the resource type and unique identifier.
        policy_names(List, optional): The names of the scaling policies
        scalable_dimension(Text): The scalable dimension. This string consists of the service namespace, resource type,
            and scaling property. ecs:service:DesiredCount
    """
    result = dict(comment=[], ret=None, result=True)
    ret = await hub.exec.boto3.client[
        "application-autoscaling"
    ].describe_scaling_policies(
        ctx=ctx,
        PolicyNames=policy_names,
        ServiceNamespace=service_namespace,
        ResourceId=scaling_resource_id,
        ScalableDimension=scalable_dimension,
    )
    if not ret["result"]:
        result["comment"] = ret["comment"]
        result["result"] = False
        return result
    if not ret["ret"]["ScalingPolicies"]:
        result["comment"].append(
            hub.tool.aws.comment_utils.get_empty_comment(
                resource_type="aws.application_autoscaling.scaling_policy", name=name
            )
        )
        return result

    resource = ret["ret"]["ScalingPolicies"][0]
    if len(ret["ret"]["ScalingPolicies"]) > 1:
        result["comment"].append(
            f"More than one aws.application_autoscaling.scaling_policy resource was found. Use resource {resource.get('PolicyName')}"
        )
    result[
        "ret"
    ] = hub.tool.aws.application_autoscaling.conversion_utils.convert_raw_scaling_policy_to_present(
        ctx, raw_resource=resource, idem_resource_name=name
    )
    return result
