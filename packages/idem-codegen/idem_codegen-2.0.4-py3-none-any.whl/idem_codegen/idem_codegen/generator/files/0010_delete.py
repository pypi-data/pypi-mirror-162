from typing import Any
from typing import Dict

from idem_codegen.idem_codegen.tool.utils import MyDumperNoBlankLines

attributes_to_include = ["name", "role_name", "policy_arn", "user_name"]


def create(
    hub, module_name: str, module_output_directory_path: str, sls_data: Dict[str, Any]
):
    delete_resource_map = {}
    for resource_path in sls_data:
        resource_data = {}
        if resource_path.startswith("data."):
            continue
        # truncating '.present' from end and append '.absent'
        for resource_state in sls_data[resource_path]:
            resource_absent_key = resource_state.replace(".present", ".absent")
            resource_data[resource_absent_key] = []
            resource_attributes = sls_data[resource_path].get(resource_state)
            # Since some resources have all attributes under one big dictionary and some have one attribute as one dict.
            if len(resource_attributes) == 1 and len(resource_attributes[0]) > 1:
                for attribute in resource_attributes[0]:
                    if attribute in attributes_to_include:
                        resource_data[resource_absent_key].append(
                            {attribute: resource_attributes[0][attribute]}
                        )
            else:
                for attribute in resource_attributes:
                    if list(attribute.keys())[0] in attributes_to_include:
                        resource_data[resource_absent_key].append(attribute)
            # If resource doesn't have any of the attributes to be included, then add resource_path as 'name'
            if len(resource_data[resource_absent_key]) == 0:
                resource_data[resource_absent_key].append({"name": resource_path})
            delete_resource_map[resource_path] = resource_data
    hub.idem_codegen.tool.utils.dump_sls_data_to_file(
        f"{module_output_directory_path}/delete-{module_name}.sls",
        delete_resource_map,
        dumper=MyDumperNoBlankLines,
    )
