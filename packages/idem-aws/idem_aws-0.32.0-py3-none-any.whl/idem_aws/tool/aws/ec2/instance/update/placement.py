from typing import List

# Update all these attributes together
__update_group__ = ["affinity", "availability_zone", "tenancy"]


async def apply(
    hub, ctx, resource, *, old_value: str, new_value: str, comments: List[str]
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
    return True
