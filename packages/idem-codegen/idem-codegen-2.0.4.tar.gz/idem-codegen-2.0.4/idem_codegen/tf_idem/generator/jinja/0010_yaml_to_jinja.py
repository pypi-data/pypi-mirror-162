import io
from collections import ChainMap
from typing import Any
from typing import Dict

import ruamel
from jinja2 import Template
from ruamel.yaml.comments import CommentedMap

from idem_codegen.idem_codegen.tool.utils import (
    separator,
)

__contracts__ = ["add_jinja"]


from idem_codegen.tf_idem.tool.utils import ternary_operator_pattern

attributes_to_ignore = ["resource_id", "arn"]


def add_jinja(hub, sls_data: Dict[str, Any], sls_original_data: Dict[str, Any]):
    terraform_resource_map = hub.tf_idem.RUNS["TF_RESOURCE_MAP"]

    # If we do not have terraform_resource_map we cannot parameterize,
    # raise an error if it's not found in hub
    idem_state_list = []
    ch = "i"
    sls_data_count_obj = io.StringIO()
    if not terraform_resource_map:
        hub.log.warning(
            "Not able to parameterize, Terraform resource map is not found in hub."
        )
        return sls_data
    for item in sls_data:
        list_of_comments = []
        # deleting the extra idem state based on count
        if len(idem_state_list) > 0:
            if item.rsplit("-", 1)[0] in idem_state_list:
                del sls_data[item]
                continue
        count = 1
        if item[-7:] != "-search" and not item.startswith("data."):
            resource_attributes = list(sls_data[item].values())[0]
            resource_type = list(sls_data[item].keys())[0].replace(".present", "")
            dict(ChainMap(*resource_attributes))

            if not sls_original_data.get(item):
                continue

            original_data_attributes = list(sls_original_data[item].values())[0]
            original_resource_id = dict(ChainMap(*original_data_attributes)).get(
                "resource_id"
            )
            # get terraform resource to look for parameters used
            terraform_resource = terraform_resource_map.get(
                f"{resource_type}{separator}{original_resource_id}"
            )
            if resource_type != "aws.ec2.security_group_rule":
                (
                    count,
                    idem_state_list,
                ) = hub.tf_idem.exec.generator.jinja.count.get_count(
                    ternary_operator_pattern,
                    count,
                    idem_state_list,
                    item,
                    terraform_resource,
                )

                for resource_attribute in resource_attributes:
                    for (
                        resource_attribute_key,
                        resource_attribute_value,
                    ) in resource_attribute.items():

                        if (
                            terraform_resource
                            and resource_attribute_key not in attributes_to_ignore
                        ):
                            (
                                tf_resource_value,
                                tf_resource_key,
                                is_attribute_different,
                            ) = hub.tf_idem.tool.utils.get_tf_equivalent_idem_attribute(
                                terraform_resource,
                                list(terraform_resource.keys())[0],
                                resource_attribute_key,
                            )
                            if resource_attribute_key == "name":
                                if count > 1:
                                    resource_attribute[
                                        resource_attribute_key
                                    ] = f'{{{{ params.get("{item[:-1]}"+({ch} | string))}}}}'
                                    continue

                            # handle count.index from resource_attribute_value
                            hub.tf_idem.tool.generator.jinja.utils.handle_count_index(
                                ch,
                                resource_attribute,
                                resource_attribute_key,
                                resource_attribute_value,
                            )

                            # convert to if-else jinja template for ternery fields
                            if_else_formatted_value = hub.tf_idem.tool.generator.jinja.utils.convert_attribute_value_to_if_else(
                                resource_attribute_key,
                                resource_attribute[resource_attribute_key],
                            )
                            if if_else_formatted_value:
                                resource_attribute[
                                    resource_attribute_key
                                ] = ruamel.yaml.scalarstring.LiteralScalarString(
                                    if_else_formatted_value
                                )

                        elif resource_attribute_key == "resource_id":
                            if count > 1:
                                resource_attribute[
                                    resource_attribute_key
                                ] = f'{{{{ params.get("{item[:-1]}"+({ch} | string))}}}}'

                if terraform_resource:
                    list_of_comments.extend(
                        hub.tf_idem.exec.generator.jinja.comments.look_for_possible_improvements(
                            terraform_resource, resource_attributes
                        )
                    )

        if count > 1:
            count_item = item[:-1] + f"{{{{{ch}}}}}"
            sls_file_data_with_comment = CommentedMap({count_item: sls_data[item]})
            if len(list_of_comments) > 0:
                sls_file_data_with_comment.yaml_set_start_comment(
                    "\n".join(list_of_comments)
                )
            obj = ruamel.yaml.round_trip_dump(sls_file_data_with_comment)
            for_loop = f"{{% for {ch} in range({count}) %}}\n"
            end_loop = "{% endfor %}"
            tm = Template("\n{{ for_loop }}{{ obj }}{{ end_loop }}\n\n")
            tm.stream(for_loop=for_loop, obj=obj, end_loop=end_loop).dump(
                sls_data_count_obj
            )
            ch = chr(ord(ch) + 1)
        elif count == 0:
            continue
        else:
            sls_file_data_with_comment = CommentedMap({item: sls_data[item]})
            if len(list_of_comments) > 0:
                sls_file_data_with_comment.yaml_set_start_comment(
                    "\n".join(list_of_comments)
                )
            obj = ruamel.yaml.round_trip_dump(sls_file_data_with_comment)
            tm = Template("\n{{ obj }}\n")
            tm.stream(obj=obj).dump(sls_data_count_obj)
    return sls_data_count_obj
