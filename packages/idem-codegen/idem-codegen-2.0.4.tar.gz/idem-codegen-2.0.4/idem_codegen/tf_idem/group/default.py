import os

"""
    Default group mechanism for tf_idem to group based on resources available in TF files
"""
__contracts__ = ["group"]


def segregate(hub, run_name: str):
    # Process all the terraform files in the working directory. TODO : Subdirectories will be ignored.
    input_dir_path = hub.OPT.idem_codegen.terraform_directory_path
    if hub.test and hub.test.idem_codegen.unit_test:
        output_dir_path = f"{hub.test.idem_codegen.current_path}/expected_output"
    else:
        output_dir_path = hub.OPT.idem_codegen.output_directory_path

    for file in os.listdir(input_dir_path):
        if not file.endswith(".tf"):
            continue
        tf_file_data = hub.tf_idem.tool.utils.parse_tf_data(
            os.path.join(input_dir_path, file)
        )

        # Perform tf to sls conversion for each module
        for module in tf_file_data.get("module", {}):
            module_name = list(module.keys())[0]
            absolute_path_of_module_source = os.path.abspath(
                module.get(module_name).get("source")
            )
            count = absolute_path_of_module_source.count("/")
            for root, _, _ in os.walk(absolute_path_of_module_source):
                hub.tf_idem.exec.group.segregate.generate_sls_files_for_tf_files_in_dir(
                    root, count, output_dir_path
                )

        # Perform tf to sls conversion of current file
        count = os.path.abspath(input_dir_path).count("/")
        hub.tf_idem.exec.group.segregate.generate_sls_files_for_tf_files_in_dir(
            os.path.abspath(input_dir_path), count, output_dir_path
        )
