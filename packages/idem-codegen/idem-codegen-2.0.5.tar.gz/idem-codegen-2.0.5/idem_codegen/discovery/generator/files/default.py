from typing import Any
from typing import Dict

__contracts__ = ["generate_file"]


def create(
    hub, module_name: str, module_output_directory_path: str, sls_data: Dict[str, Any]
):
    hub.idem_codegen.generator.files.init.generate(
        module_output_directory_path, sls_data
    )
