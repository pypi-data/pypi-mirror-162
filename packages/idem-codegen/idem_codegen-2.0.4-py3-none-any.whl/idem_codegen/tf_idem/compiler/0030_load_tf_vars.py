"""
    Get tfvars_data, if tfvars file is present in terraform parent directory.
"""

__contracts__ = ["compile"]


def stage(hub):
    tfvars = hub.tf_idem.exec.compiler.compile.collect_tfvars_data(
        hub.OPT.idem_codegen.terraform_directory_path
    )
    if not tfvars:
        hub.log.warning("tfvars file not found in working directory")
    hub.tf_idem.RUNS["TF_VARS"] = tfvars
