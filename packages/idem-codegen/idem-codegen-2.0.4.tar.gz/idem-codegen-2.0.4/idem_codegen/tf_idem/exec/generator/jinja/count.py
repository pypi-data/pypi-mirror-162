def get_count(
    hub, conditional_pattern, count, idem_state_list, item, terraform_resource
):
    if not terraform_resource:
        return count, idem_state_list
    for tf_resource_value in terraform_resource.values():
        for tf_resource_parameter in tf_resource_value.values():
            if "count" not in tf_resource_parameter:
                return count, idem_state_list
            idem_state_list.append(item.rsplit("-", 1)[0])
            if conditional_pattern.search(str(tf_resource_parameter.get("count"))):
                count = int(
                    str(tf_resource_parameter.get("count")).split("?")[1].split(":")[0]
                )
            else:
                count = tf_resource_parameter.get("count")
    return count, idem_state_list
