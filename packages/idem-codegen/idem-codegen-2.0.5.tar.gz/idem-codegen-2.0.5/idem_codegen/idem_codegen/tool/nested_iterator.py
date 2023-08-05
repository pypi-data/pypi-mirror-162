import json


def recursively_iterate_over_resource_attribute(
    hub, resource_attribute_value, func, **kwargs
):

    if isinstance(resource_attribute_value, dict):
        for item in resource_attribute_value:
            processed_value = recursively_iterate_over_resource_attribute(
                hub, resource_attribute_value[item], func, **kwargs
            )
            if processed_value:
                resource_attribute_value[item] = processed_value
        if kwargs.get("additional_function"):
            resource_attribute_value = kwargs.get("additional_function")(
                resource_attribute_value, **kwargs
            )
        return resource_attribute_value
    elif isinstance(resource_attribute_value, list):
        new_attributes = []
        for item in resource_attribute_value:
            processed_value = recursively_iterate_over_resource_attribute(
                hub, item, func, **kwargs
            )
            if processed_value:
                new_attributes.append(processed_value)
            else:
                new_attributes.append(item)
        return new_attributes
    else:
        if isinstance(
            resource_attribute_value, str
        ) and resource_attribute_value.startswith("{"):
            # policy document handle separately for parameterization
            if "tf_resource_key" in kwargs:
                return hub.idem_codegen.tool.nested_iterator.parameterize_policy_document_json(
                    resource_attribute_value, func, **kwargs
                )
            else:
                attribute_value = json.loads(resource_attribute_value)
                for item in attribute_value:
                    processed_value = recursively_iterate_over_resource_attribute(
                        hub, attribute_value[item], func, **kwargs
                    )
                    if processed_value:
                        attribute_value[item] = processed_value
                return json.dumps(attribute_value)
    return func(resource_attribute_value, **kwargs)


def parameterize_policy_document_json(hub, resource_attribute_value, func, **kwargs):
    try:
        tf_resource_policy = json.loads(resource_attribute_value)
        idem_resource_policy = json.loads(kwargs.get("attribute_value"))
        for item in idem_resource_policy:
            processed_value = (
                hub.idem_codegen.tool.nested_iterator.recursively_iterate_over_policy(
                    idem_resource_policy[item],
                    tf_resource_policy[item],
                    item,
                    func,
                    None,
                )
            )
            if processed_value:
                idem_resource_policy[item] = processed_value
        return json.dumps(idem_resource_policy)
    except Exception:
        hub.log.warning("cannot convert policy document", resource_attribute_value)


def recursively_iterate_over_policy(
    hub, idem_value, terraform_value, idem_resource_key, func, additional_function
):
    if isinstance(idem_value, dict) and isinstance(terraform_value, dict):
        for item in idem_value:
            processed_value = recursively_iterate_over_policy(
                hub,
                idem_value[item],
                terraform_value[item],
                item,
                func,
                additional_function,
            )
            if processed_value:
                idem_value[item] = processed_value
        return idem_value
    elif isinstance(idem_value, list) and isinstance(terraform_value, list):
        new_attributes = []
        for index, item in enumerate(idem_value):
            processed_value = recursively_iterate_over_policy(
                hub,
                item,
                terraform_value[index],
                idem_resource_key,
                func,
                additional_function,
            )
            if processed_value:
                new_attributes.append(processed_value)
            else:
                new_attributes.append(item)
        return new_attributes
    else:
        return func(
            terraform_value,
            idem_resource_key,
            idem_value,
            idem_resource_key,
            additional_function,
        )
