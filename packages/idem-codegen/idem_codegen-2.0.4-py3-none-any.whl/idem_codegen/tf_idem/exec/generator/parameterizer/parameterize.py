import json
import re


def format_tf_tags(hub, resolved_value, attribute_value, parameterized_value):
    if re.search(r"\${merge\(", resolved_value):
        resolved_value = resolved_value.replace("'", '"')
        try:
            format_additional_tags_str = (
                resolved_value.replace("${merge(local.tags,,", "")
                .replace(",)}", "")
                .replace("{{ ", "")
                .replace("}} ", "")
                .replace(" {{", "")
                .replace(" }}", "")
                .replace("{{", "")
                .replace("}}", "")
                .replace("'", '"')
            )

            format_additional_tags_str_p = format_additional_tags_str.replace(
                '("', '(\\"'
            ).replace('")', '\\")')
            additional_tags = json.loads(format_additional_tags_str_p)

            parameterized_value = (
                f'{{{{ params.get("local_tags") + {hub.tf_idem.tool.generator.parameterizer.utils.adjust_format_of_additional_tags(json.dumps(hub.tf_idem.tool.generator.parameterizer.utils.convert_tags_dict_list(additional_tags)))}}}}}'
                if isinstance(attribute_value, list)
                else f'{{{{ params.get("local_tags_dict") + {hub.tf_idem.tool.generator.parameterizer.utils.adjust_format_of_additional_tags(json.dumps(dict(additional_tags)))}}}}}'
            )
        except Exception as e:
            print("Exception in loading additional tags :: ", e)
    elif "local." in resolved_value:
        json_loads = json.loads(json.dumps(resolved_value))
        if isinstance(attribute_value, list):
            parameterized_value = re.sub(
                r"\${local.[\w-]+}",
                hub.tf_idem.tool.generator.parameterizer.utils.convert_local_to_param,
                str(json_loads),
            )
        else:
            parameterized_value = re.sub(
                r"\${local.[\w-]+}",
                hub.tf_idem.tool.generator.parameterizer.utils.convert_local_to_param_dict,
                str(json_loads),
            )
    return parameterized_value


def format_tags(
    hub,
    resource_attribute_value,
    attribute_key,
    attribute_value,
    tf_resource_key,
    additional_function=None,
):
    if attribute_key == "tags" and isinstance(attribute_value, list):
        resource_attribute_value = (
            hub.tf_idem.tool.generator.parameterizer.utils.convert_tags_dict_list(
                resource_attribute_value
            )
        )
    return resource_attribute_value


def is_attr_value_in_variables(hub, idem_resource_val, complete_dict_of_variables):
    for attr_key, attribute_value in complete_dict_of_variables.items():
        if attribute_value == idem_resource_val:
            return attr_key
    return None
