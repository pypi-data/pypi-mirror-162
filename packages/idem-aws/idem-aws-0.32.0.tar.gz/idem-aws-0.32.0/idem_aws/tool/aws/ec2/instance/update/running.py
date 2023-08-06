from typing import List

# Modify this attribute last
__update_order__ = -1


async def apply(
    hub, ctx, resource, *, old_value, new_value, comments: List[str]
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
    if new_value is True:
        # Start the instance up again
        ret = await hub.exec.boto3.client.ec2.start_instances(InstanceIds=[resource.id])
        if ret.comment:
            comments.append(ret.comment)
        if not ret.result:
            return False
        await hub.tool.boto3.resource.exec(resource, "wait_until_running")
    elif new_value is False:
        # Stopping the instance
        ret = await hub.exec.boto3.client.ec2.stop_instances(
            InstanceIds=[resource.id], Hibernate=False, Force=False
        )
        await hub.tool.boto3.resource.exec(resource, "wait_until_stopped")

        if ret.comment:
            comments.append(ret.comment)
        if not ret.result:
            return False

    return True
