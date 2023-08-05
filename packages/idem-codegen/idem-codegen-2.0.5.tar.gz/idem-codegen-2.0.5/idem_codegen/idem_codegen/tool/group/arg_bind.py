import collections
from collections import ChainMap
from typing import Any
from typing import Dict


def generate_graph_data(data):
    graph = collections.defaultdict(list)
    for sublist in data:
        # It's enough to connect each sublist element to the first element.
        # No need to connect each sublist element to each other sublist element.
        for item in sublist[1:]:
            graph[sublist[0]].append(item)
            graph[item].append(sublist[0])
        if len(sublist) == 1:
            # Make sure we add nodes even if they don't have edges.
            graph.setdefault(sublist[0], [])
    return graph


def generate_nodes(graph, node):
    leaf_node = [node]
    visited = set()
    while leaf_node:
        leaf_node_node = leaf_node.pop()
        if leaf_node_node in visited:
            continue
        visited.add(leaf_node_node)
        leaf_node.extend(graph[leaf_node_node])
    return visited


def group_sls_data_by_arg_bind(data):
    graph = generate_graph_data(data)
    sls_data_grouped_by_arg_bind = []
    nodes_with_component_known = set()
    for node in graph:
        if node in nodes_with_component_known:
            continue
        component = generate_nodes(graph, node)
        sls_data_grouped_by_arg_bind.append(component)
        nodes_with_component_known.update(component)

    return sls_data_grouped_by_arg_bind


def check_if_attribute_is_argbinded(
    hub,
    resource_attribute_value,
    idem_resource_id_map,
    resource_id,
    resource_id_group_map,
):

    resource_in_id_map = idem_resource_id_map.get(resource_attribute_value)
    if resource_in_id_map and len(resource_in_id_map) > 1:
        hub.log.warning(
            "Multiple resources found with same unique id. not able to do argument binding."
        )
        hub.log.warning(resource_in_id_map)
        return resource_attribute_value

    # check if the attribute value is present in map and make sure it's not same resource that we are trying to modify
    # The second condition avoids argument binding with in same resource state which is not possible.

    if resource_in_id_map and resource_in_id_map[0].get("resource_id") != resource_id:
        if resource_attribute_value not in resource_id_group_map:
            resource_id_group_map[resource_attribute_value] = []
        resource_id_group_map[resource_attribute_value].append(resource_id)


def generate_grouped_data_output(sls_grouped_data, sls_data):
    grouped_sls_data_sources = {}
    group_index = 0
    resources_grouped = []
    for grouped_sls_data in sls_grouped_data:
        group_index = group_index + 1
        grouped_sls_data_sources["group_" + str(group_index)] = {}
        for resource in grouped_sls_data:
            if resource in sls_data:
                grouped_sls_data_sources["group_" + str(group_index)][
                    resource
                ] = sls_data[resource]
                resources_grouped.append(resource)

    ungrouped_resources = {}
    for item in sls_data:
        if item not in resources_grouped:
            ungrouped_resources[item] = sls_data[item]
    grouped_sls_data_sources["ungrouped_resources"] = ungrouped_resources
    return grouped_sls_data_sources


def generate_arg_bind_groups(hub, sls_data: Dict[str, Any]):
    sls_grouped_data = {}
    idem_resource_id_map = hub.idem_codegen.exec.generator.generate.resource_id_map(
        sls_data
    )
    resource_id_group_map = {}
    for item in sls_data:
        resource_attributes = list(sls_data[item].values())[0]
        resource_map = dict(ChainMap(*resource_attributes))
        resource_type = list(sls_data[item].keys())[0].replace(".present", "")
        # loop through attributes
        for resource_attribute in resource_attributes:
            for (
                resource_attribute_key,
                resource_attribute_value,
            ) in resource_attribute.items():
                # call the recursive function on the attribute value
                if (
                    resource_attribute_key
                    not in hub.idem_codegen.tool.utils.attributes_to_ignore_for_arg_bind
                ):
                    hub.idem_codegen.tool.nested_iterator.recursively_iterate_over_resource_attribute(
                        resource_attribute_value,
                        hub.idem_codegen.tool.group.arg_bind.check_if_attribute_is_argbinded,
                        idem_resource_id_map=idem_resource_id_map,
                        resource_id=hub.idem_codegen.tool.utils.get_idem_resource_id(
                            resource_map, resource_type
                        ),
                        resource_id_group_map=resource_id_group_map,
                    )
    resource_id_group_list = []
    for sls_resource in resource_id_group_map:
        resource_id_group_list.append(
            [sls_resource] + resource_id_group_map[sls_resource]
        )

    sls_grouped_data = group_sls_data_by_arg_bind(resource_id_group_list)
    grouped_sls_data_sources = generate_grouped_data_output(sls_grouped_data, sls_data)

    return grouped_sls_data_sources
