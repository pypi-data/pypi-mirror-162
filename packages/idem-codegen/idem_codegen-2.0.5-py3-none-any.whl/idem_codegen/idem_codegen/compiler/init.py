__func_alias__ = {"compile_": "compile"}


def compile_(hub, run_name):
    """
    Compile the data defined in the given run name
    """
    for compiler_stage in sorted(hub[run_name].compiler._loaded.keys()):
        hub[run_name].compiler[compiler_stage].stage()
