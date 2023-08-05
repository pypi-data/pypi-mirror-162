"""
    Collect names of all modules defined in terraform files present in terraform parent directory.
"""

__contracts__ = ["compile"]


def stage(hub):
    module_list = hub.tf_idem.exec.compiler.compile.get_module_list(
        hub.OPT.idem_codegen.terraform_directory_path
    )
    if not module_list:
        hub.log.warning("No modules found in working directory")
    hub.tf_idem.RUNS["TF_MODULES"] = module_list
