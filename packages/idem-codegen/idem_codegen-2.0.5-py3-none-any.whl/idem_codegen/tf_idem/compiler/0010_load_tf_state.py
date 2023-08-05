import json

import boto3

"""
    Read terraform state file from S3 or 'tf_state_file_path' and load it on hub.
"""

__contracts__ = ["compile"]


def stage(hub):
    if hub.OPT.idem_codegen.get_tf_state_from_s3:
        s3_client = boto3.client("s3")
        response = s3_client.get_object(
            Bucket=hub.OPT.idem_codegen.tf_state_bucket_name,
            Key=hub.OPT.idem_codegen.tf_state_key,
        )
        res = response["Body"].read().decode("utf-8")
        tf_state_data = json.loads(res)
    else:
        if hub.test and hub.test.idem_codegen.tfstate_v3:
            tf_state_data = hub.idem_codegen.tool.utils.read_json(
                hub.OPT.idem_codegen.tf_state_file_path.replace(".json", "_v3.json")
            )
        else:
            tf_state_data = hub.idem_codegen.tool.utils.read_json(
                hub.OPT.idem_codegen.tf_state_file_path
            )

    hub.tf_idem.RUNS["TF_STATE_DATA"] = tf_state_data
