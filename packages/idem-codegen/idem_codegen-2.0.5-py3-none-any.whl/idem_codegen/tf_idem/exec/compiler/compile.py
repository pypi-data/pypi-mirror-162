import os
from collections import ChainMap


# Get the list of all modules from terraform files present in 'tf_dir' directory.
def get_module_list(hub, tf_dir):
    list_of_modules = set()
    files = os.listdir(tf_dir)

    for file in files:
        if not file.endswith(".tf"):
            continue
        tf_data = hub.tf_idem.tool.utils.parse_tf_data(os.path.join(tf_dir, file))
        module = tf_data.get("module", {})
        for module_name in set().union(*(d.keys() for d in module)):
            # fetch the list of modules present in the main.tf
            list_of_modules.add(f"module.{module_name}")
    return list_of_modules


# Collect all the module variables in the modules present in 'tf_dir' directory.
def collect_module_variables(hub, tf_dir):
    module_variables_map = {}
    files = os.listdir(tf_dir)

    for file in files:
        if not file.endswith(".tf"):
            continue
        tf_data = hub.tf_idem.tool.utils.parse_tf_data(os.path.join(tf_dir, file))
        modules = tf_data.get("module", {})
        for module in modules:
            for key, value in list(module.values())[0].items():
                if value.startswith("${module."):
                    module_variables_map[key] = value

    return module_variables_map


# Look for tfvars file in 'tf_dir' directory and parse it into dictionary, if present
def collect_tfvars_data(hub, tf_dir):
    tfvars_data = {}
    files = os.listdir(tf_dir)

    for file in files:
        if not file.endswith(".tfvars"):
            continue
        tfvars_data = hub.tf_idem.tool.utils.parse_tf_data(os.path.join(tf_dir, file))
        break
    return tfvars_data


def process_tf_state_resources(hub, tf_state_resources, list_of_modules):
    processed_tf_state_resources = []
    for resource in tf_state_resources:
        if (
            not hub.tf_idem.RUNS["TF_STATE_V3"]
            and resource.get("module") not in list_of_modules
        ):
            continue
        if resource["mode"] == "managed":
            tf_resource_type = resource["type"]

            # Safe check to identify that the tool supports all concerned resource types of terraform and Idem
            # If no support found, then log the warning and ignore this resource data
            if tf_resource_type not in hub.tf_idem.tool.utils.tf_idem_resource_type_map:
                hub.log.warning("Add mapping for the resource '%s'", tf_resource_type)
                continue

            idem_resource_type = hub.tf_idem.tool.utils.tf_idem_resource_type_map.get(
                tf_resource_type
            )

            # Safe checks to identify that the tool knows uuid of all concerned resource types of terraform and Idem
            # If no uuid found, then log the warning and ignore this resource data
            if (
                tf_resource_type not in hub.tf_idem.tool.utils.tf_resource_type_uuid
                and tf_resource_type
                not in hub.tf_idem.tool.utils.tf_resource_type_default_uuid
            ):
                hub.log.warning("Add tf unique identifier for '%s'", tf_resource_type)
                if (
                    idem_resource_type
                    not in hub.idem_codegen.tool.utils.idem_resource_type_uuid
                    and idem_resource_type
                    not in hub.idem_codegen.tool.utils.idem_resource_type_default_uuid
                ):
                    hub.log.warning(
                        f"Add idem unique identifier for '%s'", idem_resource_type
                    )
                continue

            processed_tf_state_resources.append(resource)

        elif resource["mode"] == "data":
            # processed_tf_state_resources.append(resource)
            continue  # Placeholder to process 'data' constructs of Terraform

    return processed_tf_state_resources


def compare_and_filter_sls(hub, tf_resources, sls_data):
    idem_resource_uuid_and_resource_map = (
        construct_idem_resource_uuid_value_and_resource_map(hub, sls_data)
    )
    tf_idem_resource_type_map = hub.tf_idem.tool.utils.tf_idem_resource_type_map
    tf_resource_type_uuid = hub.tf_idem.tool.utils.tf_resource_type_uuid
    tf_reseource_type_name_and_resource_map = {}
    security_group_ids = []
    security_group_ids_tf_map = {}
    filtered_sls_data = {}
    for tf_resource in tf_resources:
        tf_resource_type = tf_resource["type"]
        tf_resource_name = tf_resource["name"]

        # Constructing map to avoid iterating over tf_data again : <tf_resource_type____tf_resource_name, tf_resource>
        tf_reseource_type_name_and_resource_map[
            f"{tf_resource_type}{hub.idem_codegen.tool.utils.separator}{tf_resource_name}"
        ] = tf_resource
        resource_index = 0
        for resource_instance in tf_resource["instances"]:
            attributes = resource_instance["attributes"]
            resource_key = (
                f"{tf_resource_type}.{tf_resource_name}-{resource_index}"
                if len(tf_resource["instances"]) > 1
                else f"{tf_resource_type}.{tf_resource_name}"
            )

            # Special handling for Security Group Rules
            if tf_resource_type == "aws_security_group":
                security_group_ids.append(attributes["id"])
                security_group_ids_tf_map[attributes["id"]] = tf_resource

            tf_uuid = (
                "id"
                if tf_resource_type not in tf_resource_type_uuid
                else tf_resource_type_uuid[tf_resource_type]
            )
            if (
                tf_uuid in attributes
                and f"{tf_idem_resource_type_map.get(tf_resource_type)}{hub.idem_codegen.tool.utils.separator}{attributes[tf_uuid]}"
                in idem_resource_uuid_and_resource_map
            ):
                filtered_sls_data[
                    f"{tf_idem_resource_type_map.get(tf_resource_type)}{hub.idem_codegen.tool.utils.separator}{attributes[tf_uuid]}"
                ] = {
                    "resource": idem_resource_uuid_and_resource_map[
                        f"{tf_idem_resource_type_map.get(tf_resource_type)}{hub.idem_codegen.tool.utils.separator}{attributes[tf_uuid]}"
                    ],
                    "idem_resource_id": attributes[tf_uuid],
                    "resource_path": resource_key,
                }
            else:
                (
                    tf_unique_key_value_found_successfully,
                    tf_unique_value,
                    idem_unique_value,
                ) = hub.tf_idem.tool.utils.generate_tf_unique_value(
                    tf_uuid, attributes, tf_resource_type
                )
                if (
                    tf_unique_key_value_found_successfully
                    and f"{tf_idem_resource_type_map.get(tf_resource_type)}{hub.idem_codegen.tool.utils.separator}{tf_unique_value}"
                    in idem_resource_uuid_and_resource_map
                ):
                    filtered_sls_data[
                        f"{tf_idem_resource_type_map.get(tf_resource_type)}{hub.idem_codegen.tool.utils.separator}{tf_unique_value}"
                    ] = {
                        "resource": idem_resource_uuid_and_resource_map[
                            f"{tf_idem_resource_type_map.get(tf_resource_type)}{hub.idem_codegen.tool.utils.separator}{tf_unique_value}"
                        ],
                        "idem_resource_id": idem_unique_value,
                        "resource_path": resource_key,
                    }
            resource_index = resource_index + 1

    # Special handling for Security Group Rules
    if security_group_ids:
        security_group_rules = get_security_group_rules(
            security_group_ids,
            idem_resource_uuid_and_resource_map,
            security_group_ids_tf_map,
        )
        filtered_sls_data.update(security_group_rules)

    return tf_reseource_type_name_and_resource_map, filtered_sls_data


def get_security_group_rules(
    security_group_ids, idem_resource_uuid_and_resource_map, security_group_ids_tf_map
):
    security_group_rules = {}
    security_group_rule_id_index_map = {}
    for key, value in idem_resource_uuid_and_resource_map.items():
        sgr_resource = {}
        if "aws.ec2.security_group_rule.present" in value:
            resource = ChainMap(*value["aws.ec2.security_group_rule.present"])
            if resource.get("group_id") in security_group_ids:
                sgr_resource["resource"] = value
                sgr_resource["idem_resource_id"] = key
                if resource.get("group_id") in security_group_rule_id_index_map:
                    security_group_rule_id_index_map[resource.get("group_id")] = (
                        security_group_rule_id_index_map[resource.get("group_id")] + 1
                    )
                else:
                    security_group_rule_id_index_map[resource.get("group_id")] = 0
                rule_index = security_group_rule_id_index_map[resource.get("group_id")]
                tf_resource = security_group_ids_tf_map.get(resource.get("group_id"))
                sgr_resource[
                    "resource_path"
                ] = f"{tf_resource['type']}.{tf_resource['name']}-rule-{rule_index}"
                security_group_rules[key] = sgr_resource
    return security_group_rules


# Constructing map to avoid iterating over sls_data again : <idem_resource_uuid, idem_resource>
def construct_idem_resource_uuid_value_and_resource_map(hub, sls_data):
    idem_resource_type_uuid = hub.idem_codegen.tool.utils.idem_resource_type_uuid
    idem_resource_uuid_and_resource_map = {}
    for idem_resource_name in sls_data:
        resource_data = sls_data[idem_resource_name]
        resource_type = list(resource_data.keys())[0][
            :-8
        ]  # truncating '.present' from end
        resource_uuid_key = (
            "resource_id"
            if resource_type not in idem_resource_type_uuid
            else idem_resource_type_uuid[resource_type]
        )
        idem_filters = [resource_uuid_key]
        if "::" in resource_uuid_key:
            idem_filters = resource_uuid_key.split("::")

        resource_attribute_dicts = list(resource_data.values())[0]
        resource_attributes = dict(ChainMap(*resource_attribute_dicts))

        idem_unique_value = ""
        idem_unique_key_value = ""
        idem_unique_key_value_found_successfully = True
        for idem_filter in idem_filters:
            # NOTE : If uuid is not properly declared in idem_resource_type_uuid, then all sls instances of this
            # resource type will be ignored in filtered sls data. Henceforth, in TF to SLS file conversion, such
            # resource types will not appear in SLS
            if idem_filter not in resource_attributes:
                hub.log.warning(
                    "Invalid uuid key defined for idem resource type '%s'",
                    resource_type,
                )
                idem_unique_key_value_found_successfully = False
                break
            idem_unique_value = (
                idem_unique_value
                + (":" if idem_unique_value else "")
                + resource_attributes[idem_filter]
            )
            idem_unique_key_value = (
                idem_unique_key_value
                + ("-" if idem_unique_key_value else "")
                + resource_attributes[idem_filter]
            )
        # TODO : Check if we have to use idem_unique_value or idem_unique_key_value
        if idem_unique_key_value_found_successfully:
            idem_resource_uuid_and_resource_map[
                f"{resource_type}{hub.idem_codegen.tool.utils.separator}{idem_unique_value}"
            ] = resource_data

    return idem_resource_uuid_and_resource_map
