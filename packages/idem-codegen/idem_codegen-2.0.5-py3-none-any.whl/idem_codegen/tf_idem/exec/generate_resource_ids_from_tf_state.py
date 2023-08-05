import json
import os

import yaml

from idem_codegen.idem_codegen.tool.utils import MyDumperNoBlankLines
from idem_codegen.tf_idem.tool.utils import tf_resource_type_uuid


def read_json(path):
    _file = open(path)  # Open the json file
    json_data = json.loads(_file.read())  # Read the data from json file
    _file.close()
    return json_data


def get_idem_resource_id(hub, tf_instance, tf_resource_type):
    tf_uuid = (
        "id"
        if tf_resource_type not in tf_resource_type_uuid
        else tf_resource_type_uuid[tf_resource_type]
    )
    (
        tf_unique_key_value_found_successfully,
        tf_unique_value,
        idem_unique_value,
    ) = hub.tf_idem.tool.utils.generate_tf_unique_value(
        tf_uuid, tf_instance["attributes"], tf_resource_type
    )
    return (
        idem_unique_value
        if tf_unique_key_value_found_successfully
        else tf_instance["attributes"]["id"]
    )


def init(hub):
    tf_state_file_path = hub.OPT.idem_codegen.tf_state_file_path
    output_file_path = hub.OPT.idem_codegen.output_directory_path
    tf_state_data = read_json(tf_state_file_path)
    resource_ids_map = {}
    for tf_state_resource in tf_state_data["resources"]:
        count = 0
        if tf_state_resource.get("module"):
            module = tf_state_resource.get("module").replace("module.", "")
        else:
            module = "no-module"
        tf_resource_type = tf_state_resource.get("type")
        if module not in resource_ids_map:
            resource_ids_map[module] = {}
        tf_instances = tf_state_resource.get("instances", [])

        for tf_instance in tf_instances:
            resource_id_value = (
                ""
                if tf_resource_type == "aws_security_group_rule"
                else get_idem_resource_id(hub, tf_instance, tf_resource_type)
            )
            if len(tf_instances) > 1:
                resource_ids_map[module][
                    f"{tf_resource_type}.{tf_state_resource.get('name')}-{count}"
                ] = resource_id_value
            else:
                resource_ids_map[module][
                    f"{tf_resource_type}.{tf_state_resource.get('name')}"
                ] = resource_id_value
            count = count + 1

    for module, module_resource_map in resource_ids_map.items():
        output_file_name = os.path.join(
            output_file_path, "resource_ids_" + module + ".sls"
        )
        os.makedirs(os.path.dirname(output_file_name), exist_ok=True)
        with open(output_file_name, "w") as file:
            file.truncate(0)
            yaml.dump(module_resource_map, file, Dumper=MyDumperNoBlankLines)
