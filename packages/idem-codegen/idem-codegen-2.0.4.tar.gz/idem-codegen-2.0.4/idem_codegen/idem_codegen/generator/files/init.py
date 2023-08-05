import os
from typing import Any
from typing import Dict


sub_dirs_to_ignore = ["params", "sls"]


def generate(hub, module_output_directory_path: str, sls_data: Dict[str, Any]):
    for root, subdirectories, files in os.walk(module_output_directory_path):
        for subdirectory in subdirectories:
            if subdirectory == "params":
                hub.idem_codegen.generator.files["0020_initial"].create(
                    subdirectory, os.path.join(root, subdirectory), sls_data
                )
                continue
            if subdirectory in sub_dirs_to_ignore:
                continue
            sls_data = {}
            hub.idem_codegen.tool.utils.recursively_iterate_sls_files_directory(
                os.path.join(module_output_directory_path, subdirectory, "sls"),
                hub.idem_codegen.exec.generator.generate.collect_sls_data_in_folder,
                sls_data=sls_data,
            )

            for file_generator_plugin in sorted(
                hub.idem_codegen.generator.files._loaded.keys()
            ):
                if file_generator_plugin == "init":
                    continue

                hub.idem_codegen.generator.files[file_generator_plugin].create(
                    subdirectory,
                    os.path.join(module_output_directory_path, subdirectory),
                    sls_data,
                )
