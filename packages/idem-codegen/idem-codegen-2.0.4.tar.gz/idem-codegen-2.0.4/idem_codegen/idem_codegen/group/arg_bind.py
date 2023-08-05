"""
    Grouping mechanism for discovery to group all co-related resources
"""


def segregate(hub, run_name: str):
    if hub.test:
        if hub.test.idem_codegen.unit_test:
            output_dir_path = f"{hub.test.idem_codegen.current_path}/expected_output"
        else:
            output_dir_path = f"{hub.test.idem_codegen.current_path}/output"
    else:
        output_dir_path = hub.OPT.idem_codegen.output_directory_path

    # TODO: Add the logic to group co-related resource

    return output_dir_path
