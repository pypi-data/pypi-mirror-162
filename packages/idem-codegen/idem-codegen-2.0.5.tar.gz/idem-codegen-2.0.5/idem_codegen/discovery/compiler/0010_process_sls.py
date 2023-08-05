"""
    Read the consolidated SLS file from idem_describe_path. Compile/Parse the SLS data as per the
    requirements of idem discovery.
"""

__contracts__ = ["compile"]


def stage(hub):
    sls_data = hub.idem_codegen.tool.utils.parse_sls_data(
        hub.OPT.idem_codegen.idem_describe_path
    )

    # TODO : Implement code to pre-process sls data, if required

    hub.discovery.RUNS["SLS_DATA"] = sls_data.copy()
