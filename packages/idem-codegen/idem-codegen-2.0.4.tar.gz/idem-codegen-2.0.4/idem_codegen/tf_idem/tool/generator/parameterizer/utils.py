import re


def is_attr_value_in_variables(hub, idem_resource_val, complete_dict_of_variables):
    for attr_key, attribute_value in complete_dict_of_variables.items():
        if attribute_value == idem_resource_val:
            return attr_key
    return None


def change_bool_values_to_string(hub, complete_list_of_variables):
    for var, value in complete_list_of_variables.items():
        if isinstance(value, bool):
            complete_list_of_variables[var] = str(value)
        if "local" in var:
            if isinstance(value, dict):
                updated_dict = {}
                for local_key, local_value in value.items():
                    local_value_updated = hub.tf_idem.tool.generator.parameterizer.utils.convert_var_to_value(
                        local_value, complete_list_of_variables
                    )
                    if local_value_updated:
                        local_value = local_value_updated
                    updated_dict[local_key] = local_value
                complete_list_of_variables[var] = updated_dict
    return complete_list_of_variables


def convert_var_to_value(hub, resolved_value, complete_list_of_variables):
    parameterized_value = None
    while re.search(r"\${var\.[\w-]+}", resolved_value):
        resolved_value = re.sub(
            r"\${var\.[\w-]+}",
            hub.tf_idem.tool.generator.parameterizer.utils.convert_var_to_original_value,
            resolved_value,
        )
        parameterized_value = complete_list_of_variables.get(resolved_value)
    return parameterized_value


def convert_var_to_param(hub, var_input):
    variable_name = var_input.group()[6:-1]
    return f'{{{{ params.get("{variable_name}") }}}}'


def convert_var_to_original_value(hub, var_input):
    return var_input.group()[6:-1]


def convert_local_to_param(hub, var_input):
    variable_name = var_input.group()[2:-1]
    variable_name = variable_name.replace(".", "_")
    return f'{{{{ params.get("{variable_name}") }}}}'


def convert_local_to_param_dict(hub, var_input):
    variable_name = var_input.group()[2:-1]
    variable_name = variable_name.replace(".", "_") + "_dict"
    return f'{{{{ params.get("{variable_name}") }}}}'


def handle_count_index_in_tags(hub, additional_tags, attribute_value):
    if isinstance(attribute_value, list):
        attribute_value = (
            hub.tf_idem.tool.generator.parameterizer.utils.convert_tags_list_dict(
                attribute_value
            )
        )
    additional_tags_updated = {}
    for tag_key in additional_tags:
        tag_value = additional_tags.get(tag_key)
        if "-${count.index}" in tag_key:
            tag_key = hub.tf_idem.tool.generator.parameterizer.utils.replace_count_index_in_tags(
                tag_key, attribute_value.get(tag_key)
            )
        if "-${count.index}" in additional_tags.get(tag_key):
            tag_value = hub.tf_idem.tool.generator.parameterizer.utils.replace_count_index_in_tags(
                tag_value, attribute_value.get(tag_key)
            )
        additional_tags_updated[tag_key] = tag_value
    return additional_tags_updated


def replace_count_index_in_tags(hub, tag_key, original_tag_value):
    split_list = original_tag_value.split("-")
    for count_index in split_list:
        if count_index.isnumeric():
            tag_key = tag_key.replace("-${count.index}", f"-{count_index}")
    return tag_key


def convert_tags_list_dict(hub, tags_list):
    tags_dict = {}
    for tag in tags_list:
        tags_dict[tag.get("Key")] = tag.get("Value")
    return tags_dict


def convert_tags_dict_list(hub, tags_dict):
    tags_list = []
    for tag in tags_dict:
        tags_list.append(
            {
                "Key": hub.tf_idem.tool.generator.parameterizer.utils.fix_format_of_additional_tags(
                    tag
                ),
                "Value": hub.tf_idem.tool.generator.parameterizer.utils.fix_format_of_additional_tags(
                    tags_dict[tag]
                ),
            }
        )
    return tags_list


def adjust_format_of_additional_tags(hub, tag_str):
    # Handle if params is  at beginning or ending or middle
    tag_str = tag_str.replace('params.get(\\"', '"+params.get("')
    tag_str = tag_str.replace('"params.get(\\"', 'params.get("')
    tag_str = tag_str.replace('"+params.get(\\"', 'params.get("')
    tag_str = tag_str.replace('\\")', '")+"')
    tag_str = tag_str.replace('+""', "")
    tag_str = tag_str.replace('""+', "")

    return tag_str


def fix_format_of_additional_tags(hub, input_tag):
    if not any(substring in input_tag for substring in ["{{", "}}"]):
        return input_tag
    input_tag = re.sub("{{", '" + {{', input_tag)
    input_tag = re.sub("}}", '}} + "', input_tag)
    if input_tag.endswith(' + "'):
        input_tag = input_tag[:-4]
    if input_tag.startswith('" + '):
        input_tag = input_tag[4:]
    if not input_tag.endswith("}") and not input_tag.endswith('"'):
        input_tag = f'{input_tag}"'
    if not input_tag.startswith("{") and not input_tag.startswith('"'):
        input_tag = f'"{input_tag}'
    return input_tag
