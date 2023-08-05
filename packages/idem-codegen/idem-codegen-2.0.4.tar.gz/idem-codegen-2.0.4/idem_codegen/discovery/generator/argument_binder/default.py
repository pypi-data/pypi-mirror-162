from typing import Any
from typing import Dict

attributes_to_ignore = ["resource_id", "name", "tags", "arn"]


def arg_bind(hub, sls_data: Dict[str, Any], idem_resource_id_map) -> Dict[str, Any]:
    return hub.idem_codegen.generator.argument_binder.default.arg_bind(
        sls_data, idem_resource_id_map
    )
