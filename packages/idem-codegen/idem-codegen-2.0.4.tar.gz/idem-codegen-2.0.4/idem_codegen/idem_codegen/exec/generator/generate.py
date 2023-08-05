from collections import ChainMap


def resource_id_map(hub, sls_data):
    idem_resource_id_map = {}

    for item in sls_data:
        resource_state = sls_data[item]
        resource_attributes = list(resource_state.values())[0]
        resource_type = list(resource_state.keys())[0].replace(".present", "")
        try:
            resource_map = dict(ChainMap(*resource_attributes))

            if resource_map.get("arn"):
                if resource_map.get("arn") not in idem_resource_id_map:
                    idem_resource_id_map[resource_map.get("arn")] = []
                idem_resource_id_map[resource_map.get("arn")].append(
                    {
                        "resource_type": resource_type,
                        "resource_path": item,
                        "resource_id": resource_map.get("resource_id"),
                        "type": "arn",
                    }
                )
            if resource_map.get("resource_id"):
                if resource_map.get("resource_id") not in idem_resource_id_map:
                    idem_resource_id_map[resource_map.get("resource_id")] = []
                idem_resource_id_map[resource_map.get("resource_id")].append(
                    {
                        "resource_type": resource_type,
                        "resource_path": item,
                        "resource_id": resource_map.get("resource_id"),
                        "type": "resource_id",
                    }
                )
        except Exception as e:
            print(item)
            hub.log.warning(e)

    return idem_resource_id_map


def convert_resource_attribute_value_to_arg_bind(
    hub, resource_attribute_value, resource_id, idem_resource_id_map
):
    """
    This function checks if resource_attribute_value is present in the idem_resource_id_map
    if its present it converts the resource_attribute_value to corresponding
    argument binded format

    :param resource_id:
    :param hub:
    :param resource_attribute_value:
    :param idem_resource_id_map:
    :return:
    """
    resource_in_id_map = idem_resource_id_map.get(resource_attribute_value)
    if resource_in_id_map and len(resource_in_id_map) > 1:
        hub.log.warning(
            "Multiple resources found with same unique id. not able to do argument binding."
        )
        hub.log.warning(resource_in_id_map)
        return resource_attribute_value

    # check if the attribute value is present in map and make sure it's not same resource that we are trying to modify
    # The second condition avoids argument binding with in same resource state which is not possible.
    if resource_in_id_map and resource_in_id_map[0].get("resource_id") != resource_id:
        return f"${{{resource_in_id_map[0]['resource_type']}:{resource_in_id_map[0]['resource_path']}:{resource_in_id_map[0]['type']}}}"

    # if we do not found any match in idem_resource_map then return the value sent.
    return resource_attribute_value


def collect_sls_data_in_folder(hub, sls_file_path, sls_data):
    sls_data.update(hub.idem_codegen.tool.utils.parse_sls_data(sls_file_path))
    return sls_data
