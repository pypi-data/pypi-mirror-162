"""
    This stage takes sls data and constructs unique keys for each entity.
"""

__contracts__ = ["compile"]


def stage(hub):
    sls_data = hub.tf_idem.RUNS["SLS_DATA"]
    sls_data_with_keys = {}
    for sls_resource in sls_data:
        sls_data_with_keys[sls_data[sls_resource]["resource_path"]] = sls_data[
            sls_resource
        ]["resource"]
    hub.tf_idem.RUNS["SLS_DATA_WITH_KEYS"] = sls_data_with_keys
    return sls_data_with_keys
