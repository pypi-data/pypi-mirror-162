import os

__contracts__ = ["validate"]


def check(hub):
    if hub.OPT.idem_codegen.get_tf_state_from_s3:
        if (
            not hub.OPT.idem_codegen.tf_state_bucket_name
            or not hub.OPT.idem_codegen.tf_state_key
        ):
            raise ValueError(
                "If 'get_tf_state_from_s3' is 'True', then 'tf_state_bucket_name' and 'tf_state_key' are required parameters."
            )
    else:
        if not hub.OPT.idem_codegen.tf_state_file_path:
            raise ValueError(
                "If 'get_tf_state_from_s3' is 'False', then 'tf_state_file_path' is mandatory parameter."
            )

    if not hub.OPT.idem_codegen.terraform_directory_path:
        raise ValueError(
            "Mandatory configuration parameter 'terraform_directory_path' is missing."
        )

    # Change the current directory to 'terraform_directory_path' for further processing
    os.chdir(hub.OPT.idem_codegen.terraform_directory_path)
