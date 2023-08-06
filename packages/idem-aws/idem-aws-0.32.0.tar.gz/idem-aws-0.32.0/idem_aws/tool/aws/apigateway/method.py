from collections import OrderedDict
from typing import Any
from typing import Dict


def convert_raw_method_to_present(
    hub,
    raw_resource: Any,
    resource_id: str,
    idem_resource_name: str = None,
) -> Dict[str, Any]:
    r"""
    Convert AWS API Gateway Method to a common idem present state.

    Args:
        resource_id(string): Idem Resource ID that is generated once the resource is created.
        raw_resource(Dict[str, Any]): The AWS response to convert.
        idem_resource_name(str, optional): The idem name of the resource.

    Returns:
        Dict[str, Any]: Common idem present state
    """

    resource_parameters = OrderedDict(
        {
            "httpMethod": "http_method",
            "authorizationType": "authorization_type",
            "apiKeyRequired": "api_key_required",
        }
    )

    resource_translated = {
        "resource_id": resource_id,
        "rest_api_id": resource_id.split("-")[0],
        "parent_resource_id": resource_id.split("-")[1],
    }
    for parameter_raw, parameter_present in resource_parameters.items():
        if idem_resource_name:
            resource_translated["name"] = idem_resource_name
        if raw_resource.get(parameter_raw) is not None:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated
