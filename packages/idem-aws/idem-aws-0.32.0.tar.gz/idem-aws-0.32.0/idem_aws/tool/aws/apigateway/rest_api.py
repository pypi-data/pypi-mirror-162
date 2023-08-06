from collections import OrderedDict
from typing import Any
from typing import Dict


def convert_raw_rest_api_to_present(
    hub,
    raw_resource: Dict[str, Any],
    idem_resource_name: str = None,
) -> Dict[str, Any]:
    """
    Convert AWS returned data structure to correct idem apigateway.rest_api present state

     Args:
        hub: required for functions in hub
        raw_resource: The aws response to convert
        idem_resource_name (Text, Optional): An idem name of the resource

    Returns: Valid idem state for apigateway.rest_api of type Dict['string', Any]
    """
    resource_id = raw_resource.get("id")
    resource_parameters = OrderedDict(
        {
            "description": "description",
            "version": "version",
            "binaryMediaTypes": "binary_media_types",
            "minimumCompressionSize": "minimum_compression_size",
            "apiKeySource": "api_key_source",
            "endpointConfiguration": "endpoint_configuration",
            "policy": "policy",
            "tags": "tags",
            "disableExecuteApiEndpoint": "disable_execute_api_endpoint",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if raw_resource.get(parameter_raw) is not None:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated
