from typing import Dict
from typing import List


async def apply(
    hub,
    ctx,
    resource,
    *,
    old_value: Dict[str, str],
    new_value: Dict[str, str],
    comments: List[str],
) -> bool:
    """
    Modify an ec2 instance based on a single parameter in it's "present" state

    Args:
        hub:
        ctx: The ctx from a state module call
        resource: An ec2 instance resource object
        old_value: The previous value from the attributes of an existing instance
        new_value: The desired value from the ec2 instance present state parameters
        comments: A running list of comments abound the update process
    """
    result = True
    tags_to_create = set(new_value.keys()) - set(old_value.keys())
    tags_to_delete = set(old_value.keys()) - set(new_value.keys())

    tags_to_modify = set(old_value.keys()).intersection(set(new_value.keys()))
    for key in tags_to_modify:
        if old_value[key] != new_value[key]:
            # Add the tag to the delete operation then to the create operation with tth new value
            tags_to_delete.add(key)
            tags_to_create.add(key)

    # Delete old tags
    ret = await hub.exec.boto3.client.ec2.delete_tags(
        ctx,
        Resources=[resource.id],
        Tags=[{"Key": key, "Value": old_value[key]} for key in tags_to_delete],
    )
    result &= ret.result
    if ret.comment:
        comments.append(ret.comment)

    # Create new tags
    ret = await hub.exec.boto3.client.ec2.create_tags(
        ctx,
        Resources=[resource.id],
        Tags=[{"Key": key, "Value": new_value[key]} for key in tags_to_create],
    )
    result &= ret.result
    if ret.comment:
        comments.append(ret.comment)

    return result
