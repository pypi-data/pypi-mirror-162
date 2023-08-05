import os

"""
    Grouping mechanism based on resource service
"""


def segregate(hub, run_name: str):
    if hub.test:
        if hub.test.idem_codegen.unit_test:
            output_dir_path = (
                f"{hub.test.idem_codegen.current_path}/unit_test_output_group"
            )
            os.makedirs(os.path.dirname(output_dir_path), exist_ok=True)
        else:
            output_dir_path = f"{hub.test.idem_codegen.current_path}/output"
    else:
        output_dir_path = hub.OPT.idem_codegen.output_directory_path

    grouped_sls_data = {}

    sls_data_with_keys = hub[run_name].RUNS.get("SLS_DATA_WITH_KEYS", {})

    if not sls_data_with_keys:
        hub.log.error("'SLS_DATA_WITH_KEYS' is not present in hub.")
        return

    for idem_resource_key, idem_resource_state in sls_data_with_keys.items():
        for key in list(idem_resource_state):
            if "." in key:
                comps = key.split(".")
                resource_type = ".".join(comps[1:-2])
                if "." in resource_type:
                    resource_type = resource_type.replace(".", "_")
                if resource_type not in grouped_sls_data:
                    grouped_sls_data[resource_type] = {}
                grouped_sls_data[resource_type][idem_resource_key] = idem_resource_state

    hub.idem_codegen.tool.utils.dump_data_to_multiple_files(
        grouped_sls_data, os.path.join(output_dir_path, "output", "sls")
    )
    return output_dir_path
