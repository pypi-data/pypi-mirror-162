from collections import OrderedDict
from typing import Any
from typing import Dict


def convert_raw_resource_to_present(
    hub,
    raw_resource: Dict[str, Any],
    idem_resource_name: str = None,
    rest_api_id: str = None,
) -> Dict[str, Any]:
    r"""
    Convert AWS API Gateway Resource to a common idem present state.

    Args:
        hub: required for functions in hub.
        raw_resource(Dict[str, Any]): The AWS response to convert.
        idem_resource_name(str): Optional parameter -- will be the resource name if applicable,
            otherwise resource name will be taken from raw_resource.
        rest_api_id(str): Rest Api Id associated with the Rest Api to which the Resource belongs.

    Returns:
        Dict[str, Any]: Common idem present state
    """

    resource_id = raw_resource.get("id")

    if idem_resource_name:
        name = idem_resource_name
    else:
        name = raw_resource.get("pathPart")

    resource_parameters = OrderedDict(
        {
            "parentId": "parent_id",
            "pathPart": "path_part",
        }
    )

    resource_translated = {
        "name": name,
        "resource_id": resource_id,
        "rest_api_id": rest_api_id,
    }
    for parameter_raw, parameter_present in resource_parameters.items():
        resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated
