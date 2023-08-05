import json
import os
import re

import yaml
from ruamel.yaml import RoundTripDumper
from ruamel.yaml import YAML

from idem_codegen.tf_idem.tool.utils import FILES_TO_IGNORE

separator = "____"

ACCEPTABLE_RUN_NAMES = ["tf_idem", "discovery"]

ACCEPTABLE_GENERATE_TYPES = ["resource_ids"]

idem_resource_type_uuid = {
    "aws.iam.role_policy_attachment": "role_name::policy_arn",
    "aws.iam.user_policy": "user_name::name",
    "aws.iam.role_policy": "role_name::name",
    "aws.eks.addon": "cluster_name::resource_id",
    "aws.eks.nodegroup": "cluster_name::nodegroup_arn",
    "aws.route53.hosted_zone_association": "zone_id::vpc_id::vpc_region",
    "aws.sns.topic_policy": "topic_arn",
    "aws.s3.bucket_notification": "name",
}

idem_resources_with_no_resource_id = {
    "aws.iam.role_policy_attachment": "role_name::policy_arn",
}

idem_resource_type_default_uuid = [
    "aws.ec2.vpc",
    "aws.ec2.subnet",
    "aws.ec2.security_group",
    "aws.cloudwatch.log_group",
    "aws.rds.db_subnet_group",
    "aws.elasticache.cache_subnet_group",
    "aws.ec2.flow_log",
    "aws.iam.role",
    "aws.ec2.internet_gateway",
    "aws.ec2.nat_gateway",
    "aws.ec2.route_table",
    "aws.ec2.security_group_rule",
    "aws.ec2.dhcp_option",
    "aws.eks.cluster",
    "aws.iam.policy",
    "aws.iam.user",
    "aws.acm.certificate_manager",
    "aws.autoscaling.launch_configuration",
    "aws.cloudtrail.trail",
    "aws.cloudwatch.metric_alarm",
    "aws.config.rule",
    "aws.dynamodb.table",
    "aws.ec2.ami",
    "aws.ecr.repository",
    "aws.elasticache.cache_parameter_group",
    "aws.iam.access_key",
    "aws.iam.instance_profile",
    "aws.iam.open_id_connect_provider",
    "aws.iam.user_policy_attachment",
    "aws.iam.user_ssh_key",
    "aws.lambda_.function",
    "aws.route53.hosted_zone",
    "aws.s3.bucket",
    "aws.s3.bucket_policy",
    "aws.sns.topic",
    "aws.sns.subscription",
    "aws.ec2.dhcp_option",
    "aws.kms.key",
    "aws_cloudwatch_event_rule",
    "aws.route53.resource_record",
]

attributes_to_ignore_for_arg_bind = ["resource_id", "name", "tags", "arn"]


def read_json(hub, path):
    _file = open(path)  # Open the json file
    json_data = json.loads(_file.read())  # Read the data from json file
    _file.close()
    return json_data


def parse_sls_data(hub, path):
    _file = open(path)  # Open the sls file
    sls_data = yaml.load(
        _file.read(), Loader=yaml.FullLoader
    )  # Read the data from sls file. Parse using yaml parser
    _file.close()
    return sls_data


class RoundTripDumper(RoundTripDumper):
    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()
            super().write_line_break()

    def write_single_quoted(self, text, split=True):
        super().write_plain(text)


class MyDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()
            super().write_line_break()


class MyDumperNoBlankLines(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

    def write_line_break(self, data=None):
        super().write_line_break(data)


def get_sls_data_from_directory(hub, sls_files_directory_path: str):
    sls_data = {}
    for root, dirs, files in os.walk(sls_files_directory_path):
        for file in files:
            if file not in FILES_TO_IGNORE:
                sls_data.update(parse_sls_data(os.path.join(hub, root, file)))
    return sls_data


def dump_sls_data_to_file(hub, file_path, sls_data, dumper=None):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as file:
        yaml.dump(
            dict(sls_data),
            file,
            default_flow_style=False,
            Dumper=dumper if dumper else MyDumper,
        )


def dump_sls_data_with_jinja_to_file(hub, file_path, sls_data, dumper):
    if sls_data:
        yaml1 = YAML()

        def sanitize(s):
            return s.replace("{{", "<{").replace("{%", "#%")

        def unsanitize(s):
            jinja_format = (
                s.replace("<{", "{{")
                .replace("#%", "{%")
                .replace("'", "")
                .replace("      {%", "  {%")
                .replace("%}\n      -", "%}\n  -")
                .replace(" }}}", " }}")
            )
            return re.sub(r"\n[\w\- :_-]+ \|-", "", jinja_format)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "a") as file:
            file.truncate(0)
            data = yaml1.load(sanitize(sls_data.getvalue()))
            yaml1.dump(data, file, transform=unsanitize)


def dump_data_to_multiple_files(hub, sls_group_data, output_dir_path):
    for file_name, file_data in sls_group_data.items():
        os.makedirs(os.path.join(output_dir_path), exist_ok=True)
        with open(os.path.join(output_dir_path, file_name + ".sls"), "w") as file:
            yaml.dump(dict(file_data), file, default_flow_style=False, Dumper=MyDumper)


def recursively_iterate_sls_files_directory(
    hub, sls_files_directory_path, func, **kwargs
):
    for root, dirs, files in os.walk(sls_files_directory_path):
        for file in files:
            func(os.path.join(root, file), **kwargs)


def get_idem_resource_id(hub, resource_map, resource_type):
    resource_id = ""
    if resource_type in idem_resources_with_no_resource_id:
        resource_id_format = idem_resources_with_no_resource_id[resource_type]
        if "::" in resource_id_format:
            idem_filters = resource_id_format.split("::")
            for idem_filter in idem_filters:
                resource_id += resource_map.get(idem_filter) + "-"
        return resource_id[:-1]
    else:
        return resource_map.get("resource_id")
