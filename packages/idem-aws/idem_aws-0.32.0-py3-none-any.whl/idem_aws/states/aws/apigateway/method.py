import copy
from typing import Any
from typing import Dict

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    rest_api_id: str,
    http_method: str,
    parent_resource_id: str,
    resource_id: str = None,
    api_key_required: bool = False,
    authorization_type: str = None,
) -> Dict[str, Any]:
    r"""
    Creates an API Gateway Method resource

    Args:
        name(string): Idem name of the resource.
        rest_api_id(string): The string identifier of the associated Rest API.
        http_method(string): String that specifies the method request's HTTP method type.
        parent_resource_id(string): AWS Parent Resource ID.
        authorization_type(string, optional): The method's authorization type. Valid values are NONE for open access,
            AWS_IAM for using AWS IAM permissions, CUSTOM for using a custom authorizer, or
            COGNITO_USER_POOLS for using a Cognito user pool. Necessary for creation but not for updating.
        resource_id(string, optional): Idem Resource ID that is generated once the resource is created.
        api_key_required(bool, optional): A boolean flag specifying whether a valid ApiKey is required to invoke this method.

        Parameters not yet supported by Idem:
        authorization_scopes(list, optional): A list of authorization scopes configured on the method. The scopes are
            used with a COGNITO_USER_POOLS authorizer to authorize the method invocation. The authorization works by
            matching the method scopes against the scopes parsed from the access token in the incoming request.
            The method invocation is authorized if any method scopes matches a claimed scope in the access token.
            Otherwise, the invocation is not authorized. When the method scope is configured, the client must provide
            an access token instead of an identity token for authorization purposes.
        authorizer_id(string, optional): The identifier of an Authorizer to use on this method. The authorizationType must be CUSTOM .
        operation_name(string, optional): A human-friendly operation identifier for the method.
        request_parameters(dict, optional): A key-value map defining required or optional method request parameters that
            can be accepted by API Gateway. A key is a method request parameter name matching the pattern of
            method.request.{location}.{name} , where location is querystring , path , or header and name is a valid and
            unique parameter name. The value associated with the key is a Boolean flag indicating whether the parameter
            is required (true ) or optional (false ). The method request parameter names defined here are available in
            Integration to be mapped to integration request parameters or templates.
        request_models(dict, optional): A key-value map specifying data schemas, represented by Model resources,
            (as the mapped value) of the request payloads of given content types (as the mapping key).
        request_validator_id(string, optional): The identifier of a RequestValidator for request validation.



    Request Syntax:
        [idem_test_aws_apigateway_method]:
          aws.apigateway.method.present:
            - name: 'string'
            - rest_api_id: 'string'
            - parent_resource_id: 'string'
            - http_method: 'string'
            - authorization_type: 'string'

    Returns:
        Dict[str, Any]

    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    before = None
    resource_updated = False

    if resource_id:
        before = await hub.exec.aws.apigateway.method.get(
            ctx,
            name=name,
            resource_id=resource_id,
        )
        if not before["result"] or not before["ret"]:
            result["comment"] = before["comment"]
            result["result"] = False
            return result
        result["old_state"] = before["ret"]
        result["new_state"] = copy.deepcopy(result["old_state"])

        update_parameters = {
            "http_method": http_method,
            "authorization_type": authorization_type,
            "api_key_required": api_key_required,
        }

        update_ret = await hub.exec.aws.apigateway.method.update(
            ctx,
            old_state=result["old_state"],
            update_parameters=update_parameters,
        )
        if not update_ret["result"]:
            result["result"] = False
            result["comment"] = update_ret["comment"]
            return result
        result["comment"] = result["comment"] + update_ret["comment"]
        resource_updated = bool(update_ret["ret"])

        if resource_updated and ctx.get("test", False):
            result["new_state"].update(update_ret["ret"])

        if resource_updated:
            if ctx.get("test", False):
                result["comment"] = result[
                    "comment"
                ] + hub.tool.aws.comment_utils.would_update_comment(
                    resource_type="aws.apigateway.resource", name=name
                )
                return result
    else:
        resource_id = f"{rest_api_id}-{parent_resource_id}-{http_method}"

        if ctx.get("test", False):
            result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "resource_id": resource_id,
                    "rest_api_id": rest_api_id,
                    "parent_resource_id": parent_resource_id,
                    "http_method": http_method,
                    "authorization_type": authorization_type,
                },
            )

            result["comment"] = hub.tool.aws.comment_utils.would_create_comment(
                resource_type="aws.apigateway.method", name=name
            )
            return result

        ret = await hub.exec.boto3.client.apigateway.put_method(
            ctx,
            restApiId=rest_api_id,
            resourceId=parent_resource_id,
            httpMethod=http_method,
            authorizationType=authorization_type,
        )
        result["result"] = ret["result"]
        if not result["result"]:
            result["comment"] = ret["comment"]
            return result

        result["comment"] = hub.tool.aws.comment_utils.create_comment(
            resource_type="aws.apigateway.method", name=name
        )

    if (not before) or resource_updated:
        after = await hub.exec.aws.apigateway.method.get(
            ctx,
            name=name,
            resource_id=resource_id,
        )

        resource_translated = after["ret"]
        result["new_state"] = resource_translated
    else:
        result["new_state"] = copy.deepcopy(result["old_state"])
    return result


async def absent(
    hub,
    ctx,
    name: str,
    rest_api_id: str,
    http_method: str,
    parent_resource_id: str,
    resource_id: str = None,
) -> Dict[str, Any]:

    r"""
    Deletes an API Gateway Method resource

    Args:
        name(string): An Idem name of the resource.
        parent_resource_id(string): AWS Parent Resource ID.
        rest_api_id(string): The string identifier of the associated RestApi.
        http_method(string): The HTTP verb of the Method resource.
        resource_id(string, optional): The resource identifier for the Method resource. Idem automatically considers
            this resource being absent if this field is not specified.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            idem_test_aws_apigateway_method:
              aws.apigateway.method.absent:
                - name: value
                - parent_resource_id: value
                - rest_api_id: value
                - resource_id: value
                - http_method: value
    """
    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)

    if not resource_id:
        # if resource_id isn't specified, the resource is considered to be absent.
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.apigateway.method", name=name
        )
        return result

    before_ret = await hub.exec.aws.apigateway.method.get(
        ctx,
        name=name,
        resource_id=resource_id,
    )

    if not before_ret["result"]:
        result["result"] = False
        result["comment"] = before_ret["comment"]
        return result

    if not before_ret["ret"]:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.apigateway.method", name=name
        )

    result["old_state"] = before_ret["ret"]

    if ctx.get("test", False):
        result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
            resource_type="aws.apigateway.method", name=name
        )
        return result

    delete_ret = await hub.exec.boto3.client.apigateway.delete_method(
        ctx,
        restApiId=rest_api_id,
        resourceId=parent_resource_id,
        httpMethod=http_method,
    )
    if not delete_ret["result"]:
        result["result"] = False
        result["comment"] = delete_ret["comment"]
        return result

    result["comment"] = hub.tool.aws.comment_utils.delete_comment(
        resource_type="aws.apigateway.method", name=name
    )
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""

    Describe the API Gateway Methods associated with a specific Rest API.

    Returns a list of apigateway.method descriptions

    Returns:
        Dict[str, Any]


    Examples:

        .. code-block:: bash

            $ idem describe aws.apigateway.method

    """

    result = {}

    get_rest_apis_ret = await hub.exec.boto3.client.apigateway.get_rest_apis(ctx)
    if not get_rest_apis_ret["result"]:
        hub.log.debug(f"Could not get Rest Apis {get_rest_apis_ret['comment']}")
        return result

    for rest_api in get_rest_apis_ret["ret"]["items"]:
        rest_api_id = rest_api.get("id")
        get_resources_ret = await hub.exec.boto3.client.apigateway.get_resources(
            ctx, restApiId=rest_api_id
        )
        if not get_resources_ret["result"]:
            hub.log.debug(f"Could not describe resource {get_resources_ret['comment']}")
            return result

        if get_resources_ret["ret"]["items"] is not None:
            for resource in get_resources_ret["ret"]["items"]:
                parent_resource_id = resource.get("id")
                if resource.get("resourceMethods") is not None:
                    for resource_method in resource.get("resourceMethods"):
                        resource_id = (
                            f"{rest_api_id}-{parent_resource_id}-{resource_method}"
                        )

                        ret = await hub.exec.aws.apigateway.method.get(
                            ctx, resource_id=resource_id
                        )

                        resource_translated = ret["ret"]

                        result[resource_translated["resource_id"]] = {
                            "aws.apigateway.method.present": [
                                {parameter_key: parameter_value}
                                for parameter_key, parameter_value in resource_translated.items()
                            ]
                        }

    return result
