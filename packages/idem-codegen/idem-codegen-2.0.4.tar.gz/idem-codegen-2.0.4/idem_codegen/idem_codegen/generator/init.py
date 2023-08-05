import copy
import io
import os
import pathlib

from idem_codegen.idem_codegen.tool.utils import MyDumper
from idem_codegen.idem_codegen.tool.utils import RoundTripDumper
from idem_codegen.tf_idem.tool.utils import FILES_TO_IGNORE


def generate(hub, sls_file_path, run_name, idem_resource_id_map):
    # we process only sls_files and some sls files needs to be ignored
    if pathlib.Path(sls_file_path).suffix != ".sls":
        hub.log.info(
            f"Not able to run generate phase on file '{sls_file_path}', since it's not an sls file."
        )
        return
    jinja_dump_data = io.StringIO()
    sls_file_data = hub.idem_codegen.tool.utils.parse_sls_data(sls_file_path)
    sls_original_data = copy.deepcopy(sls_file_data)
    if (
        sls_file_data
        and os.path.basename(sls_file_path) not in FILES_TO_IGNORE
        and "delete-" not in sls_file_path
    ):
        sls_file_data = hub[run_name].generator.argument_binder.default.arg_bind(
            sls_file_data, idem_resource_id_map
        )

        sls_file_data = hub[run_name].generator.parameterizer.default.parameterize(
            sls_file_data
        )

        # add comments
        jinja_dump_data = hub.idem_codegen.generator.jinja.init.execute(
            run_name, sls_file_data, sls_original_data
        )

        try:
            # write the sls_data back to file after parameterization and argument binding
            hub.idem_codegen.tool.utils.dump_sls_data_with_jinja_to_file(
                sls_file_path, jinja_dump_data, RoundTripDumper
            )
        except Exception:
            hub.idem_codegen.tool.utils.dump_sls_data_to_file(
                sls_file_path, jinja_dump_data, MyDumper
            )


def run(hub, run_name: str, sls_files_directory: str):
    """
    :param hub:
    :param run_name: The state run name
    :param sls_files_directory:
    """

    if not sls_files_directory:
        sls_files_directory = hub.OPT.idem_codegen.get("output_directory_path")

    if "SLS_DATA_WITH_KEYS" in hub[run_name].RUNS:
        sls_data = hub[run_name].RUNS["SLS_DATA_WITH_KEYS"]
    else:
        sls_data = hub.idem_codegen.tool.utils.get_sls_data_from_directory(
            sls_files_directory
        )
    idem_resource_id_map = hub.idem_codegen.exec.generator.generate.resource_id_map(
        sls_data
    )

    # recursively loop through the given sls files that were grouped in group phase
    # This utility function will iterate recursively from root directory

    # generate resource_ids, init and delete files.
    hub[run_name].generator.files.default.create(None, sls_files_directory, {})

    hub.idem_codegen.tool.utils.recursively_iterate_sls_files_directory(
        sls_files_directory,
        hub.idem_codegen.generator.init.generate,
        run_name=run_name,
        idem_resource_id_map=idem_resource_id_map,
    )
