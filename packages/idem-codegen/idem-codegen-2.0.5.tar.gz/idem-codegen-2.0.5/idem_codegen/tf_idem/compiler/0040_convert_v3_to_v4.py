"""
    These steps convert tfstate file in the format of tfstate file version 4.
    This stage is needed only when version of tfstate file is 3.

"""
from collections import OrderedDict


def stage(hub):
    hub.tf_idem.RUNS["TF_STATE_V3"] = False
    tf_state_data = hub.tf_idem.RUNS["TF_STATE_DATA"]
    if tf_state_data["version"] == 3:
        tf_state_data["version"] = 4
        hub.tf_idem.RUNS["TF_STATE_V3"] = True
        tf_state_modules = tf_state_data["modules"]
        final_resource_dict = OrderedDict()
        for module in tf_state_modules:
            module_resources = module["resources"]
            for resource_name, resource_value in module_resources.items():
                parameters = OrderedDict()
                parameters["attributes"] = resource_value["primary"]["attributes"]
                resource_name = resource_name.split("-index_")[0]
                if resource_name in final_resource_dict:
                    final_resource_dict[resource_name]["instances"].append(parameters)
                    continue
                resource = OrderedDict()
                name_type = resource_name.split(".")
                name = name_type[-1]
                resource["name"] = name
                if name_type[0] == "data":
                    resource["mode"] = "data"
                else:
                    resource["mode"] = "managed"
                resource["type"] = resource_value["type"]
                resource["provider"] = resource_value["provider"]
                resource["instances"] = [parameters]
                final_resource_dict[resource_name] = resource
        tf_state_data["resources"] = list(final_resource_dict.values())
        del tf_state_data["modules"]
        hub.tf_idem.RUNS["TF_STATE_DATA"] = tf_state_data
