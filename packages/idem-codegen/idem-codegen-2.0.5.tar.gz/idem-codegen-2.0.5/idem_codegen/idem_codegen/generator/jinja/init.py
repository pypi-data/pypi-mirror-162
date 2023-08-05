__func_alias__ = {"execute_": "execute"}

from typing import Dict, Any


def execute_(
    hub,
    run_name,
    sls_data: Dict[str, Any],
    sls_original_data: Dict[str, Any],
):
    """
    Execute the jinja code generation steps defined in the given run name
    """
    for generate_jinja_step in sorted(hub[run_name].generator.jinja._loaded.keys()):
        sls_data = (
            hub[run_name]
            .generator.jinja[generate_jinja_step]
            .add_jinja(sls_data, sls_original_data)
        )

    return sls_data
