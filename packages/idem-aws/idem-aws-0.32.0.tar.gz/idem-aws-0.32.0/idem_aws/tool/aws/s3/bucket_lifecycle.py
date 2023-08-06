import asyncio
from typing import Any
from typing import Dict
from typing import List


"""
Util functions for AWS S3 bucket lifecycle resources.
"""


def convert_raw_bucket_lifecycle_to_present(
    hub, bucket: str, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    r"""
    Convert an AWS S3 bucket lifecycle resource to a common idem present state.

    Args:
        hub: required for functions in hub.
        bucket(string): The S3 bucket name in Amazon Web Services.
        raw_resource(Dict[str, Any]): The AWS response to convert.
        idem_resource_name(string, optional): An Idem name of the resource.

    Returns:
        Dict[str, Any]: Common idem present state.
    """

    raw_resource.pop("ResponseMetadata", None)

    resource_translated = {
        "name": idem_resource_name if idem_resource_name else f"{bucket}-lifecycle",
        "resource_id": bucket,
        "bucket": bucket,
        "lifecycle_configuration": {"Rules": raw_resource.get("Rules")},
    }

    return resource_translated


def is_bucket_lifecycle_configuration_identical(
    hub,
    new_configuration: Dict[str, List],
    old_configuration: Dict[str, List],
) -> bool:
    r"""
    Compares the new and old bucket lifecycle configurations.

    Args:
        hub: required for functions in hub.
        new_configuration(Dict[str, Any]): The new bucket lifecycle configuration parameters.
        old_configuration(Dict[str, Any]): The old bucket lifecycle configuration parameters.

    Returns:
        bool: true if there are no differences between the new and old bucket lifecycle configurations.
    """

    new_lifecycle_configuration = new_configuration.get("lifecycle_configuration", {})
    old_lifecycle_configuration = old_configuration.get("lifecycle_configuration", {})

    new_rules_configuration = new_lifecycle_configuration.get("Rules", [])
    old_rules_configuration = old_lifecycle_configuration.get("Rules", [])
    if not hub.tool.aws.s3.bucket_lifecycle.are_bucket_lifecycle_rules_identical(
        new_rules_configuration, old_rules_configuration
    ):
        return False

    return True


def are_bucket_lifecycle_rules_identical(
    hub,
    new_rules: List,
    old_rules: List,
) -> bool:
    r"""
    Compares the new and old bucket lifecycle rules.

    Args:
        hub: required for functions in hub.
        new_rules(List): The new bucket lifecycle rules.
        old_rules(List): The old dbucket lifecycle rules.

    Returns:
        bool: true if there are no differences between the new and old bucket lifecycle rules.
    """
    if (new_rules is None or len(new_rules) == 0) and (
        old_rules is None or len(old_rules) == 0
    ):
        return True
    if (
        new_rules is None
        or len(new_rules) == 0
        or old_rules is None
        or len(old_rules) == 0
    ):
        return False

    diff = [
        i for i in new_rules + old_rules if i not in new_rules or i not in old_rules
    ]

    return len(diff) == 0


async def wait_for_updates(
    hub,
    ctx,
    bucket: str,
    lifecycle_configuration: Dict[str, List],
    timeout: Dict = None,
) -> Dict[str, Any]:
    r"""
    Waits for an AWS S3 bucket lifecycle configuration to be updated.

    Args:
        hub: required for functions in hub.
        ctx: context.
        bucket(string): The name of the S3 bucket in Amazon Web Services.
        lifecycle_configuration(Dict): The expected lifecycle configuration for the S3 bucket.
        timeout(Dict, optional): Timeout configuration for updating the S3 bucket lifecycle configuration.
            * delay (int, optional): The amount of time in seconds to wait between attempts. Defaults to 4 seconds.
            * max_attempts (int, optional): Maximum attempts of waiting for the update. Defaults to 30 attempts.

    Returns:
        Dict[str, Any]: Common idem present state.
    """

    result = dict(comment=(), result=True, ret=None)

    delay = timeout.get("delay", 4) if timeout else 4
    max_attempts = timeout.get("max_attempts", 30) if timeout else 30

    count = 1
    while count <= max_attempts:
        hub.log.info(
            f"Waiting for S3 bucket '{bucket}' lifecycle configuration to be updated for the {count} time."
        )
        await asyncio.sleep(delay)

        get_bucket_lifecycle_ret = (
            await hub.exec.boto3.client.s3.get_bucket_lifecycle_configuration(
                ctx, Bucket=bucket
            )
        )
        if not get_bucket_lifecycle_ret["result"]:
            result["result"] = False
            result["comment"] = get_bucket_lifecycle_ret["comment"]
            return result

        actual_lifecycle_configuration = {
            "lifecycle_configuration": {
                "Rules": get_bucket_lifecycle_ret.get("ret").get("Rules")
            },
        }
        expected_lifecycle_configuration = {
            "lifecycle_configuration": lifecycle_configuration,
        }

        if hub.tool.aws.s3.bucket_lifecycle.is_bucket_lifecycle_configuration_identical(
            expected_lifecycle_configuration, actual_lifecycle_configuration
        ):
            result["ret"] = get_bucket_lifecycle_ret["ret"]
            return result

        count = count + 1

    result["result"] = False
    result["comment"] = (
        f"Timed out waiting for S3 bucket '{bucket}' lifecycle configuration to be updated.",
    )
    return result


async def wait_for_delete(
    hub,
    ctx,
    bucket: str,
    timeout: Dict = None,
) -> Dict[str, Any]:
    r"""
    Waits for an AWS S3 bucket lifecycle configuration to be deleted.

    Args:
        hub: required for functions in hub.
        ctx: context.
        bucket(string): The name of the S3 bucket in Amazon Web Services.
        timeout(Dict, optional): Timeout configuration for deleting the S3 bucket lifecycle configuration.
            * delay (int, optional): The amount of time in seconds to wait between attempts. Defaults to 4 seconds.
            * max_attempts (int, optional): Maximum attempts of waiting for the deletion. Defaults to 30 attempts.

    Returns:
        Dict[str, Any]: Common idem present state.
    """

    result = dict(comment=(), result=True, ret=None)

    waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
        default_delay=4,
        default_max_attempts=30,
        timeout_config=timeout.get("delete") if timeout else None,
    )

    bucket_lifecycle_waiter = hub.tool.boto3.custom_waiter.waiter_wrapper(
        name="BucketLifeCycleDeleted",
        operation="GetBucketLifecycleConfiguration",
        argument=["Error.Code", "Rules"],
        acceptors=[
            {
                "matcher": "error",
                "expected": "NoSuchLifecycleConfiguration",
                "state": "success",
                "argument": "Error.Code",
            },
            {
                "matcher": "path",
                "expected": True,
                "state": "retry",
                "argument": "length(Rules) >= `0`",
            },
        ],
        client=hub.tool.boto3.client.get_client(ctx, "s3"),
    )

    try:
        await hub.tool.boto3.client.wait(
            ctx,
            "s3",
            "BucketLifeCycleDeleted",
            bucket_lifecycle_waiter,
            Bucket=bucket,
            WaiterConfig=waiter_config,
        )
    except Exception as e:
        result["result"] = False
        result["comment"] = (str(e),)
        return result

    return result
