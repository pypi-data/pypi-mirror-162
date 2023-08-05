from typing import Any
from typing import Dict

from idem_codegen.idem_codegen.tool.utils import MyDumperNoBlankLines


def create(
    hub, module_name: str, module_output_directory_path: str, sls_data: Dict[str, Any]
):
    resource_ids = {}
    for resource_path in sls_data:
        for resource_state in sls_data[resource_path]:
            resource_attributes = sls_data[resource_path].get(resource_state)
            if len(resource_attributes) == 1 and len(resource_attributes[0]) > 1:
                for attribute in resource_attributes[0]:
                    if attribute == "resource_id":
                        resource_ids[resource_path] = resource_attributes[0][attribute]
                        break
            else:
                for attribute in resource_attributes:
                    if list(attribute.keys())[0] == "resource_id":
                        resource_ids[resource_path] = attribute.get("resource_id")
                        break

    hub.idem_codegen.tool.utils.dump_sls_data_to_file(
        f"{module_output_directory_path}/params/resource_ids.sls",
        resource_ids,
        dumper=MyDumperNoBlankLines,
    )
