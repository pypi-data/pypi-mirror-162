from collections import ChainMap
from typing import Any
from typing import Dict

# This is the main function that loops through sls_data input


def arg_bind(
    hub,
    sls_data: Dict[str, Any],
    idem_resource_id_map,
) -> Dict[str, Any]:
    """
    This function will take inputs sls_data (input data on which we need to do argument binding) and idem resource_id map
    which contains resource_ids of all resources provided in input.
    This function will loop through each resource state in sls_data (input) and inside each resource state it loops
    through all the attributes in a recursive manner to scan all the inner data and then check if the attribute value
    is present in idem_resource_id_map, if its present replace the attribute value with the
    corresponding argument binding syntax.

    hub:
    sls_data: idem describe data on which we need to do argument binding
    idem_resource_id_map: map of all resource_ids in idem describe response input

    :return:
    sls_data: argument binded sls_data
    """

    # loop though sls_data
    for item in sls_data:
        resource_attributes = list(sls_data[item].values())[0]
        resource_map = dict(ChainMap(*resource_attributes))
        # loop through attributes
        for resource_attribute in resource_attributes:
            for (
                resource_attribute_key,
                resource_attribute_value,
            ) in resource_attribute.items():
                # call the recursive function on the attribute value
                if (
                    resource_attribute_key
                    not in hub.idem_codegen.tool.utils.attributes_to_ignore_for_arg_bind
                ):
                    resource_attribute[
                        resource_attribute_key
                    ] = hub.idem_codegen.tool.nested_iterator.recursively_iterate_over_resource_attribute(
                        resource_attribute_value,
                        hub.idem_codegen.exec.generator.generate.convert_resource_attribute_value_to_arg_bind,
                        resource_id=resource_map.get("resource_id"),
                        idem_resource_id_map=idem_resource_id_map,
                    )
    return sls_data
