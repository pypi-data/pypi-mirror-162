"""
    Read the consolidated SLS file from idem_describe_path. Filter the SLS data with
    resources that are managed by Terraform only in all modules of cluster.
"""

__contracts__ = ["compile"]


def stage(hub):
    tf_data = hub.tf_idem.RUNS["TF_STATE_DATA"]
    sls_data = hub.idem_codegen.tool.utils.parse_sls_data(
        hub.OPT.idem_codegen.idem_describe_path
    )
    (
        tf_reseource_type_name_and_resource_map,
        filtered_sls_data,
    ) = hub.tf_idem.exec.compiler.compile.compare_and_filter_sls(
        tf_data["resources"], sls_data
    )

    hub.tf_idem.RUNS["TF_IDEM_RESOURCE_MAP"] = tf_reseource_type_name_and_resource_map
    hub.tf_idem.RUNS["SLS_DATA"] = filtered_sls_data
