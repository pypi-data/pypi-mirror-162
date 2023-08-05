def stage(hub):
    module_variables_map = hub.tf_idem.exec.compiler.compile.collect_module_variables(
        hub.OPT.idem_codegen.terraform_directory_path
    )
    hub.tf_idem.RUNS["MODULE_VARIABLES"] = module_variables_map
