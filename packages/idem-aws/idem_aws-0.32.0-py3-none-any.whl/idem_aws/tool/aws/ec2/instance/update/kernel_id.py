from typing import List


# The instance must be stopped to modify this value
__update_state__ = "stopped"


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
    result = True
    # The instance must be stopped to modify its kernel
    was_running = False
    if resource.state["Name"] == "running":
        was_running = True
        comments.append(f"Stopping the instance to prepare for changing kernel")
        ret = await hub.exec.boto3.client.ec2.stop_instances(
            InstanceIds=[resource.id], Hibernate=False, Force=False
        )
        await hub.tool.boto3.resource.exec(resource, "wait_until_stopped")

        if ret.comment:
            comments.append(ret.comment)
        if not ret.result:
            return False

    # Modify the kernel
    if new_value is None:
        ret = await hub.exec.boto3.client.ec2.reset_instance_attribute(
            ctx, InstanceId=resource.id, Attribute="kernel"
        )
        if ret.comment:
            comments.append(ret.comment)
        result &= ret.result
    else:
        ret = await hub.exec.boto3.client.ec2.modfiy_instance_attribute(
            ctx, InstanceId=resource.id, Attribute="kernel", Kernel={"Value": new_value}
        )
        if ret.comment:
            comments.append(ret.comment)
        result &= ret.result

    if was_running:
        # Start the instance up again
        ret = await hub.exec.boto3.client.ec2.start_instances(InstanceIds=[resource.id])
        if ret.comment:
            comments.append(ret.comment)
        if not ret.result:
            return False
        await hub.tool.boto3.resource.exec(resource, "wait_until_running")

    return result
