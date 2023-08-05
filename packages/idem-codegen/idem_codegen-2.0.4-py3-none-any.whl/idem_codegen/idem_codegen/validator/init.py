def validate(hub, run_name: str):
    if run_name not in hub.idem_codegen.tool.utils.ACCEPTABLE_RUN_NAMES:
        raise ValueError("Invalid value of parameter 'run_name'")

    if not hub.OPT.idem_codegen.output_directory_path:
        raise ValueError(
            "Mandatory configuration parameter 'output_directory_path' is missing."
        )

    if not hub.OPT.idem_codegen.idem_describe_path:
        raise ValueError(
            "Mandatory configuration parameter 'idem_describe_path' is missing."
        )

    hub[run_name].validator.validate.check()
