import re
from collections import ChainMap
from typing import Any
from typing import Dict

from idem_codegen.idem_codegen.tool.utils import (
    separator,
)

__contracts__ = ["parameterize"]

from idem_codegen.tf_idem.tool.utils import ternary_operator_pattern

attributes_to_ignore = ["resource_id", "arn"]

var_pattern = re.compile(r"^var\.[\w.\[\]-]+")


def convert_attribute_value_to_params(
    hub,
    resolved_value,
    attribute_key=None,
    attribute_value=None,
    tf_resource_key=None,
    additional_function=None,
):
    if not resolved_value or not isinstance(resolved_value, str):
        return
    parameterized_value = None

    # TODO: Uncomment this line after we add account_id as a mandatory param in params.sls
    # resolved_value = resolved_value.replace("${data.aws_caller_identity.current.account_id}", 'params.get("account_id")')
    if re.match(var_pattern, resolved_value):
        resolved_value = "${" + resolved_value + "}"
    while re.search(r"\${var\.[\w.\[\]-]+}", resolved_value):
        res_value = process_output_variables(hub, resolved_value)
        if res_value:
            resolved_value = res_value
        else:
            resolved_value = re.sub(
                r"\${var\.[\w.\[\]-]+}",
                hub.tf_idem.tool.generator.parameterizer.utils.convert_var_to_param,
                resolved_value,
            )
        parameterized_value = resolved_value

    if resolved_value and attribute_key != None and attribute_key == "tags":
        parameterized_value = (
            hub.tf_idem.exec.generator.parameterizer.parameterize.format_tf_tags(
                resolved_value, attribute_value, parameterized_value
            )
        )

    return parameterized_value


def process_output_variables(hub, var_input):
    variable_name = var_input[6:-1]
    module_variables_map = hub.tf_idem.RUNS["MODULE_VARIABLES"]
    output_variables_map = hub.tf_idem.RUNS["OUTPUT_VARIABLES"]
    if variable_name not in module_variables_map:
        return None
    variable_value = output_variables_map.get(module_variables_map[variable_name])
    if variable_value.startswith("${"):
        # Example variable_value is '${aws_iam_role.xyz-admin.arn}'
        val = variable_value[2:-1]
        resource_type = hub.tf_idem.tool.utils.tf_idem_resource_type_map.get(
            val.split(".")[0]
        )
        resource = val.split(".")[1]
        param = val.split(".")[2]

        search_block = {
            f"{variable_name}-search": {
                f"{resource_type}.search": [
                    {
                        "resource_id": f'{{{{ params.get("{list(val.rsplit(".", 1))[0]}") }}}}'
                    }
                ]
            }
        }
        hub.tf_idem.RUNS["SEARCH_BLOCK"].update(search_block)
        return f"${{{resource_type}:{resource}-search:{param}}}"


def parameterize(hub, sls_data: Dict[str, Any]):
    """
    This function takes sls_data as input loop through all the attribute values and
    check if they can be parameterized and convert ${var.test_variable} in terraform
    to {{params.get("test_variable")}} in sls.

    :param hub:
    :param sls_data:
    :return:
    """

    # get terraform resources_map. It's map of all terraform resources
    # we are trying to convert to sls

    terraform_resource_map = hub.tf_idem.RUNS["TF_RESOURCE_MAP"]
    complete_dict_of_variables = hub.tf_idem.RUNS["TF_VARIABLES"]
    idem_state_list = []
    # If we do not have terraform_resource_map we cannot parameterize,
    # raise an error if it's not found in hub

    if not terraform_resource_map:
        hub.log.warning(
            "Not able to parameterize, Terraform resource map is not found in hub."
        )
        return sls_data
    # ToDO: Simplify more

    # Initialize SEARCH_BLOCK variable on hub
    hub.tf_idem.RUNS["SEARCH_BLOCK"] = {}
    for item in list(sls_data):
        if len(idem_state_list) > 0:
            if item.rsplit("-", 1)[0] in idem_state_list:
                del sls_data[item]
                continue
        count = 1
        resource_attributes = list(sls_data[item].values())[0]
        is_data_source = False
        if item.startswith("data."):
            is_data_source = True
            terraform_resource = resource_type
        else:
            resource_type = list(sls_data[item].keys())[0].replace(".present", "")
            resource_map = dict(ChainMap(*resource_attributes))

            # get terraform resource to look for parameters used
            terraform_resource = terraform_resource_map.get(
                f"{resource_type}{separator}{resource_map.get('resource_id')}"
            )
            (count, idem_state_list) = hub.tf_idem.exec.generator.jinja.count.get_count(
                ternary_operator_pattern,
                count,
                idem_state_list,
                item,
                terraform_resource,
            )

        # if not terraform_resource:
        #     continue
        # loop through attributes
        for resource_attribute in resource_attributes:
            for (
                resource_attribute_key,
                resource_attribute_value,
            ) in resource_attribute.items():

                if is_data_source or (
                    terraform_resource
                    and resource_attribute_key not in attributes_to_ignore
                ):
                    if is_data_source:
                        tf_resource_value = resource_attribute_value
                        tf_resource_key = resource_attribute_key
                        is_attribute_different = False
                    else:
                        (
                            tf_resource_value,
                            tf_resource_key,
                            is_attribute_different,
                        ) = hub.tf_idem.tool.utils.get_tf_equivalent_idem_attribute(
                            terraform_resource,
                            list(terraform_resource.keys())[0],
                            resource_attribute_key,
                        )

                    if isinstance(tf_resource_value, str) and re.search(
                        r"\${jsonencode\(var\.[\w-]+\)}", tf_resource_value
                    ):
                        tf_resource_value = re.sub(
                            r"\${jsonencode\(var\.[\w-]+\)}",
                            lambda jsonencode_string: f'"${{var.{jsonencode_string.group()[17:-2]}}}"',
                            tf_resource_value,
                        )

                    # call the recursive function on the attribute value
                    parameterized_value = hub.idem_codegen.tool.nested_iterator.recursively_iterate_over_resource_attribute(
                        tf_resource_value,
                        hub.tf_idem.generator.parameterizer.default.convert_attribute_value_to_params,
                        attribute_key=resource_attribute_key,
                        attribute_value=resource_attribute_value,
                        tf_resource_key=tf_resource_key,
                        additional_function=hub.tf_idem.exec.generator.parameterizer.parameterize.format_tags,
                    )

                    if isinstance(
                        tf_resource_value, str
                    ) and ternary_operator_pattern.search(tf_resource_value):
                        expression = resource_attribute_value.split(" ? ")[0].strip()
                        true_block = (
                            resource_attribute_value.split(" ? ")[1]
                            .split(" : ")[0]
                            .strip()
                        )
                        false_block = (
                            resource_attribute_value.split(" ? ")[1]
                            .split(" : ")[1]
                            .strip()
                        )
                        if re.match(var_pattern, expression):
                            expression = convert_attribute_value_to_params(
                                hub, expression
                            )
                        if re.match(var_pattern, true_block):
                            true_block = convert_attribute_value_to_params(
                                hub, true_block
                            )
                        if re.match(var_pattern, false_block):
                            false_block = convert_attribute_value_to_params(
                                hub, false_block
                            )
                        parameterized_value = (
                            f"{expression} ? {true_block} : {false_block}"
                        )

                    if parameterized_value:
                        if is_attribute_different:
                            hub.tf_idem.tool.utils.set_tf_equivalent_idem_attribute(
                                resource_attribute_key,
                                parameterized_value,
                                list(terraform_resource.keys())[0],
                                resource_attribute_key,
                                resource_attribute,
                            )
                        else:
                            resource_attribute[
                                resource_attribute_key
                            ] = parameterized_value

                    elif not isinstance(resource_attribute_value, bool):
                        attribute_in_variable = hub.tf_idem.exec.generator.parameterizer.parameterize.is_attr_value_in_variables(
                            resource_attribute_value, complete_dict_of_variables
                        )
                        if attribute_in_variable:
                            resource_attribute[
                                resource_attribute_key
                            ] = f'{{{{params.get("{attribute_in_variable}")}}}}'
                elif resource_attribute_key == "resource_id":
                    resource_attribute[
                        resource_attribute_key
                    ] = f'{{{{ params.get("{item}")}}}}'
    if hub.tf_idem.RUNS.get("SEARCH_BLOCK"):
        search_sls = hub.tf_idem.RUNS["SEARCH_BLOCK"]
        search_sls.update(sls_data)
        sls_data = search_sls
        hub.tf_idem.RUNS["SEARCH_BLOCK"] = {}

    return sls_data
