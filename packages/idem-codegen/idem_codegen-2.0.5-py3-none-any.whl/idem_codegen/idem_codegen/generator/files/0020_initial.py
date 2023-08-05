import os
from typing import Any
from typing import Dict


def create(
    hub, module_name: str, module_output_directory_path: str, sls_data: Dict[str, Any]
):
    if "/params" not in module_output_directory_path:
        return
    param_list = []
    for file in os.listdir(f"{module_output_directory_path}"):
        if file == "init.sls":
            continue
        param_list.append(file[:-4])
    init_dict = {"include": sorted(param_list)}
    hub.idem_codegen.tool.utils.dump_sls_data_to_file(
        f"{module_output_directory_path}/init.sls", init_dict
    )
