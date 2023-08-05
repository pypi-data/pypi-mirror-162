"""
    This stage takes sls data and constructs unique keys for each entity.
"""

__contracts__ = ["compile"]


def stage(hub):
    sls_data = hub.discovery.RUNS["SLS_DATA"]

    # TODO : Implement code to format keys as per the requirement

    hub.discovery.RUNS["SLS_DATA_WITH_KEYS"] = sls_data
    return sls_data
