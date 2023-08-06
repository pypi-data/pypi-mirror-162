from typing import Any
from typing import Dict
from typing import List


async def apply(
    hub,
    ctx,
    resource,
    *,
    old_value: Dict[str, Any],
    new_value: Dict[str, Any],
    comments: List[str],
) -> bool:
    """
    Compare the kwargs of the present function to the presentized attributes of the instance
    """
    current_state = old_value
    desired_state = new_value

    # Get the current_state/desired state for running
    update_start_state = current_state.get("running")
    update_current_run_state = current_state.get("running")

    update_needs_stopped = []
    update_needs_running = []
    update_group: Dict[str, List[str]] = {}
    update_remainder = []

    # Group attributes together to determine how to do the update
    for attribute, new_attr_value in desired_state.items():
        if desired_state[attribute] is None:
            # There is no new value for the attribute
            continue
        if desired_state[attribute] == current_state.get(attribute):
            # This specific attribute is in the proper state
            continue

        mod = hub.tool.aws.ec2.instance.update[attribute]
        if getattr(mod, "__update_state__", None) == "stopped":
            # This attribute can only be modified while stopped
            update_needs_stopped.append(mod)
        elif getattr(mod, "__update_state__", None) == "running":
            # This attribute can only be modified while running
            update_needs_running.append(mod)
        elif getattr(mod, "__update_group__", None):
            # Some attributes need to be modified together, send their data to a single mod
            group = getattr(mod, "__update_group__")
            if group not in update_group:
                update_group[group] = []
            update_group[group].append(mod)
        else:
            # This attribute has no extra needs
            update_remainder.append(mod)

    # Start with the attributes that work with the instance in the current running state
    # This will minimize number of shutdown/restarts as we update the instance
    if resource.state.name == "running" and update_needs_running:
        ...
        # first_update_group = update_needs_running
        # second_update_group = update_needs_stopped

    try:
        if update_needs_stopped and update_current_run_state is True:
            await hub.exec.aws.ec2.instance.stop(ctx, instance_id="TODO")

            update_current_run_state = False

        # TODO Modify all the attributes that require the instance to be stopped first, stop if needed
        # TODO Group attributes that need to be modified together (like for placement)
        # TODO run all other attribute modifications

        if update_needs_running and current_state.get("running") is False:
            await hub.exec.aws.ec2.instance.start(ctx, instance_id="TODO")
            update_current_run_state = True

        # TODO Modify all the attributes that require the instance to be running first, start if needed
        return True
    finally:
        # Put the state back in the desired/previous state for running
        desired_run_state = desired_state.get("running", update_start_state)
        if desired_run_state != update_current_run_state:
            if desired_run_state is True:
                await hub.exec.aws.ec2.instance.start(ctx, instance_id="TODO")
            else:
                await hub.exec.aws.ec2.instance.stop(ctx, instance_id="TODO")


async def old_update(
    hub, ctx, name, resource, current_state, desired_state, comments, result
):
    # TODO delete this function when the main apply function is done
    for attribute, new_value in desired_state.items():
        if new_value is None:
            # No value has been explicitly given, leave this parameter alone
            continue

        # TODO desired state from ESM is showing changes when it shouldn't...
        old_value = current_state.get(attribute)

        if old_value != new_value:
            # There is a single file dedicated to updating each attribute of an ec2 instance.
            # Organization is key for managing such a large resource.
            # This "present" function should remain mostly the same, don't bloat it!
            # Add an attribute-specific file in idem_aws/tool/aws/ec2/instance/update to manage specific parameters.
            # Be sure to follow the contracts in idem_aws/tool/aws/ec2/instance/update/contracts
            if attribute not in hub.tool.aws.ec2.instance.update._loaded:
                comments += [
                    f"Modifying aws.ec2.instance attribute '{attribute}' is not yet supported"
                ]
                continue

            if ctx.test:
                comments += [f"Would update aws.ec2.instance '{name}': {attribute}"]
                continue

            # Call the appropriate tool to update each parameter that needs updating
            result["result"] &= await hub.tool.aws.ec2.instance.update[attribute].apply(
                ctx,
                resource,
                old_value=old_value,
                new_value=new_value,
                # This list is stored in memory
                # modifying this value in "update.apply" functions will update it in the "result" dictionary
                comments=result["comment"],
            )
            if not result["result"]:
                result["comment"] += [
                    f"Unable to update aws.ec2.instance attribute: {attribute}"
                ]
                break
