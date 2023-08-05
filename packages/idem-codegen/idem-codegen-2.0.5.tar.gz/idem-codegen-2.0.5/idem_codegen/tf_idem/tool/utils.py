import re

import hcl2

tf_resource_type_uuid_separator = {
    "aws_route53_zone_association": ":",
}

ternary_operator_pattern = re.compile(
    r"\${[\s\d\w. ]+\?[\s\d\w.[\] ]+:[\s\d\w.[\] ]+}|[\s\d\w. ]+\?[\s\d\w.[\] ]+:[\s\d\w.[\] ]+"
)

ternery_operator_pattern_in_jinja = re.compile(
    r'["$.{{\s\w\d()\[\]\/}}+\*|-]+\?["$.{{\s\w\d()\[\]\/}}+\*|-]+\:["$.{{\s\w\d()\[\]\/}}+\*|-]+'
)

var_pattern_unprocessed1 = r"\${var\.[\w.\[\]-]+"

var_pattern_unprocessed2 = r"var\.[\w.\[\]-]+"

count_index_pattern = r"\$[{ +\d]+count.index[ *\d-]+}"

# NOTE : For any new entry in this map, ensure to add required details in tf_resource_type_uuid,
# tf_resource_type_default_uuid, idem_resource_type_uuid and idem_resource_type_default_uuid
tf_idem_resource_type_map = {
    "aws_cloudwatch_log_group": "aws.cloudwatch.log_group",
    "aws_db_subnet_group": "aws.rds.db_subnet_group",
    "aws_eip": "aws.ec2.elastic_ip",
    "aws_elasticache_subnet_group": "aws.elasticache.cache_subnet_group",
    "aws_flow_log": "aws.ec2.flow_log",
    "aws_iam_role": "aws.iam.role",
    "aws_iam_role_policy": "aws.iam.role_policy",
    "aws_internet_gateway": "aws.ec2.internet_gateway",
    "aws_nat_gateway": "aws.ec2.nat_gateway",
    "aws_route_table": "aws.ec2.route_table",
    "aws_security_group": "aws.ec2.security_group",
    "aws_security_group_rule": "aws.ec2.security_group_rule",
    "aws_subnet": "aws.ec2.subnet",
    "aws_vpc": "aws.ec2.vpc",
    "aws_vpc_dhcp_options": "aws.ec2.dhcp_option",
    "aws_eks_cluster": "aws.eks.cluster",
    "aws_iam_policy": "aws.iam.policy",
    "aws_iam_role_policy_attachment": "aws.iam.role_policy_attachment",
    "aws_iam_user": "aws.iam.user",
    "aws_iam_user_policy": "aws.iam.user_policy",
    "aws_acm_certificate": "aws.acm.certificate_manager",
    "aws_launch_configuration": "aws.autoscaling.launch_configuration",
    "aws_cloudtrail": "aws.cloudtrail.trail",
    "aws_cloudwatch_metric_alarm": "aws.cloudwatch.metric_alarm",
    "aws_config_config_rule": "aws.config.rule",
    "aws_dynamodb_table": "aws.dynamodb.table",
    "aws_ami": "aws.ec2.ami",
    "aws_ecr_repository": "aws.ecr.repository",
    "aws_eks_addon": "aws.eks.addon",
    "aws_eks_node_group": "aws.eks.nodegroup",
    "aws_elasticache_parameter_group": "aws.elasticache.cache_parameter_group",
    "aws_iam_access_key": "aws.iam.access_key",
    "aws_iam_instance_profile": "aws.iam.instance_profile",
    "aws_iam_openid_connect_provider": "aws.iam.open_id_connect_provider",
    "aws_iam_user_policy_attachment": "aws.iam.user_policy_attachment",
    "aws_iam_user_ssh_key": "aws.iam.user_ssh_key",
    "aws_lambda_function": "aws.lambda_.function",
    "aws_route53_zone": "aws.route53.hosted_zone",
    "aws_route53_zone_association": "aws.route53.hosted_zone_association",
    "aws_s3_bucket": "aws.s3.bucket",
    "aws_s3_bucket_notification": "aws.s3.bucket_notification",
    "aws_s3_bucket_policy": "aws.s3.bucket_policy",
    "aws_sns_topic": "aws.sns.topic",
    "aws_sns_topic_policy": "aws.sns.topic_policy",
    "aws_sns_topic_subscription": "aws.sns.subscription",
    "aws_kms_key": "aws.kms.key",
    "aws_cloudwatch_event_rule": "aws.event.rule",
    "aws_subnets": "aws.ec2.subnet.list",
    "aws_ec2_transit_gateway": "aws.ec2.transit_gateway",
}

tf_resource_type_uuid = {
    "aws_iam_role_policy": "role::name",
    "aws_iam_role_policy_attachment": "role::policy_arn",
    "aws_iam_user_policy": "user::name",
    "aws_eks_addon": "addon_name::cluster_name",
    "aws_eks_node_group": "clusterName::nodeGroupName",
    "aws_route53_zone_association": "zone_id::vpc_id::vpc_region",
    "aws_eip": "public_ip",
}


tf_resource_type_default_uuid = [
    "aws_vpc",
    "aws_subnet",
    "aws_security_group",
    "aws_cloudwatch_log_group",
    "aws_db_subnet_group",
    "aws_eip",
    "aws_elasticache_subnet_group",
    "aws_flow_log",
    "aws_iam_role",
    "aws_internet_gateway",
    "aws_nat_gateway",
    "aws_route_table",
    "aws_security_group_rule",
    "aws_vpc_dhcp_options",
    "aws_eks_cluster",
    "aws_iam_policy",
    "aws_iam_user",
    "aws_acm_certificate",
    "aws_iam_role_policy",
    "aws_launch_configuration",
    "aws_cloudtrail",
    "aws_cloudwatch_metric_alarm",
    "aws_config_config_rule",
    "aws_dynamodb_table",
    "aws_ami",
    "aws_ecr_repository",
    "aws_elasticache_parameter_group",
    "aws_iam_access_key",
    "aws_iam_instance_profile",
    "aws_iam_openid_connect_provider",
    "aws_iam_user_policy_attachment",
    "aws_iam_user_ssh_key",
    "aws_lambda_function",
    "aws_route53_zone",
    "aws_s3_bucket",
    "aws_s3_bucket_notification",
    "aws_s3_bucket_policy",
    "aws_sns_topic",
    "aws_sns_topic_policy",
    "aws_sns_topic_subscription",
    "aws_ec2_vpc_dhcp_options",
    "aws_iam_role",
    "aws_iam_role_policy",
    "aws_kms_key",
    "aws_cloudwatch_event_rule",
    "aws_route53_record",
]

FILES_TO_IGNORE = [
    "variables.sls",
    "init.sls",
    "resource_ids.sls",
    "tags.sls",
]

DATA_COMMENT = (
    "ToDo: The attribute '{resource}' has resolved value of 'data' state. Please create a variable with "
    "resolved value and use {{ params.get('variable_name') }} instead of resolved value of 'data' state."
)
CONDITIONAL_COMMENT = (
    "ToDo: The attribute '{resource}' has conditional operator. Use {{% if params.get("
    "'variable_name') %}} and {{% else %}} for if-else condition"
)

tf_equivalent_idem_attributes = {
    "aws_vpc": {"cidr_block_association_set": "cidr_block"},
    "aws_iam_role_policy": {"policy_document": "policy"},
    "aws_iam_role": {"assume_role_policy_document": "assume_role_policy"},
    "aws_s3_bucket": {"name": "bucket"},
    "aws_route53_zone": {"hosted_zone_name": "name"},
}

tf_equivalent_idem_attribute_key = {
    "aws_vpc": {
        "cidr_block_association_set": "cidr_block_association_set...[0]...CidrBlock"
    },
    "aws_iam_role_policy": {"policy_document": "policy_document"},
    "aws_iam_role": {"assume_role_policy_document": "assume_role_policy_document"},
}


def parse_tf_data(hub, path):
    _file = open(path)  # Open the *.tf file
    tf_data = hcl2.load(_file)  # Parse using python-hcl2 parser
    _file.close()
    return tf_data


def generate_tf_unique_value(hub, tf_uuid, attributes, tf_resource_type):
    tf_filters = [tf_uuid]
    if "::" in tf_uuid:
        tf_filters = tf_uuid.split("::")

    tf_unique_value = ""
    idem_unique_value = ""
    for tf_filter in tf_filters:
        # NOTE : If tf uuid is not properly declared in tf_resource_type_uuid, then all instances of this
        # resource type will be ignored in filtered sls data. Henceforth, in TF to SLS file conversion, such
        # resource types will not appear in SLS
        if (
            tf_filter not in attributes
            and tf_resource_type not in tf_resource_type_uuid
        ):
            return False, None, None
        tf_unique_value = (
            tf_unique_value
            + (":" if tf_unique_value else "")
            + attributes.get(tf_filter, "")
        )
        idem_resource_separator = (
            tf_resource_type_uuid_separator[tf_resource_type]
            if tf_resource_type in tf_resource_type_uuid_separator
            else "-"
        )
        idem_unique_value = (
            idem_unique_value
            + (idem_resource_separator if idem_unique_value else "")
            + attributes.get(tf_filter, "")
        )
    return True, tf_unique_value, idem_unique_value


def get_tf_equivalent_idem_attribute(
    hub, tf_resource, tf_resource_type, idem_resource_attribute
):
    if tf_resource_type in tf_equivalent_idem_attributes:
        tf_equivalent_idem_resource_attributes = tf_equivalent_idem_attributes[
            tf_resource_type
        ]
        if idem_resource_attribute in tf_equivalent_idem_resource_attributes:
            return (
                list(list(tf_resource.values())[0].values())[0].get(
                    tf_equivalent_idem_resource_attributes[idem_resource_attribute]
                ),
                tf_equivalent_idem_resource_attributes[idem_resource_attribute],
                True,
            )
    return (
        list(list(tf_resource.values())[0].values())[0].get(idem_resource_attribute),
        idem_resource_attribute,
        False,
    )


def set_tf_equivalent_idem_attribute(
    hub,
    attribute_key,
    attribute_value,
    tf_resource_type,
    idem_resource_attribute,
    resource_data,
):
    if tf_resource_type in tf_equivalent_idem_attribute_key:
        tf_equivalent_idem_resource_attributes = tf_equivalent_idem_attribute_key[
            tf_resource_type
        ]
        if idem_resource_attribute in tf_equivalent_idem_resource_attributes:
            path_arr = tf_equivalent_idem_resource_attributes[attribute_key].split(
                "..."
            )
            recent_element = resource_data
            for index_e, path_element in enumerate(path_arr):
                if index_e == len(path_arr) - 1:
                    recent_element[path_element] = attribute_value
                    continue
                if path_element.startswith("[") and path_element.endswith("]"):
                    index_of_element = int(
                        path_element.replace("[", "").replace("]", "")
                    )
                    recent_element = recent_element[index_of_element]
                else:
                    recent_element = recent_element[path_element]
    elif tf_resource_type in tf_equivalent_idem_attributes:
        tf_equivalent_idem_resource_attributes = tf_equivalent_idem_attributes[
            tf_resource_type
        ]
        if idem_resource_attribute in tf_equivalent_idem_resource_attributes:
            resource_data[idem_resource_attribute] = attribute_value


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
