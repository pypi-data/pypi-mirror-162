"""
    Filter managed and data resources that belong to modules obtained in 'load_tf_modules' step.
"""

__contracts__ = ["compile"]


def stage(hub):
    list_of_modules = hub.tf_idem.RUNS.get("TF_MODULES", None)
    tf_state_data = hub.tf_idem.RUNS["TF_STATE_DATA"]

    # Processing resources
    tf_state_data[
        "resources"
    ] = hub.tf_idem.exec.compiler.compile.process_tf_state_resources(
        tf_state_data["resources"], list_of_modules
    )

    # TODO : If any more constructs need to be processed in tf_state, add the logic here

    hub.tf_idem.RUNS["TF_STATE_DATA"] = tf_state_data
