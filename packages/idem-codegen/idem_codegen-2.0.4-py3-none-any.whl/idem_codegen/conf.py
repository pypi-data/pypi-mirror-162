# https://pop.readthedocs.io/en/latest/tutorial/quickstart.html#adding-configuration-data
# In this dictionary goes all the immutable values you want to show up under hub.OPT.idem_codegen
CONFIG = {
    "config": {
        "default": None,
        "help": "Load extra options from a configuration file onto hub.OPT.idem_codegen",
    },
    "tf_state_bucket_name": {"default": "", "help": "Name of S3 bucket"},
    "tf_state_key": {"default": "", "help": "S3 bucket key name"},
    "get_tf_state_from_s3": {
        "default": False,
        "help": "If true, download the tf_state json file from s3 bucket",
    },
    "terraform_directory_path": {
        "default": "",
        "help": "Absolute path of the account directory where terraform files are stored",
    },
    "output_directory_path": {
        "default": "",
        "help": "Absolute path of the output directory where converted files will be generated.",
    },
    "idem_describe_path": {
        "default": "",
        "help": "Absolute path of the file containing sls data collected from IDEM describe command.",
    },
    "tf_state_file_path": {
        "default": "",
        "help": "Absolute path of the terraform state file fetched from s3 bucket. Used when tf_state is taken as input",
    },
    "group_style": {
        "default": "default",
        "help": "Provide the name of grouping mechanism that should be used to group discovered resources. "
        "Acceptable values are:\n"
        "1. default : Groups resource using the default grouping mechanism of the run path\n"
        "2. resource_type : Puts all resources of same type like VPC in one file\n"
        "3. arg_bind : Puts all co-related resources together in one file\n"
        "4. resource_service: Puts all resources belonging to same service like EC2 in one file\n",
    },
    "type": {"default": "resource_ids", "subcommands": ["generate"]},
}

# The selected subcommand for your cli tool will show up under hub.SUBPARSER
# The value for a subcommand is a dictionary that will be passed as kwargs to argparse.ArgumentParser.add_subparsers
SUBCOMMANDS = {
    "generate": {
        "desc": "Generate file 'type' like resource_ids.sls explicitly from terraform state file",
        "help": "Generate file 'type' resource_ids.sls explicitly from terraform state file",
    },
    "tf_idem": {
        "desc": "Perform conversion of terraform IaC to SLS format",
        "help": "Perform conversion of terraform IaC to SLS format",
    },
    "discovery": {
        "desc": "Discover an existing infrastructure and generate SLS IaC",
        "help": "Discover an existing infrastructure and generate SLS IaC",
    },
}

# Include keys from the CONFIG dictionary that you want to expose on the cli
# The values for these keys are a dictionaries that will be passed as kwargs to argparse.ArgumentParser.add_option
CLI_CONFIG = {
    "config": {"options": ["-c"], "subcommands": ["_global_"]},
    "tf_state_bucket_name": {"options": ["-b", "--s3-bucket-name"]},
    "tf_state_key": {"options": ["-k", "--s3-state-key"]},
    "get_tf_state_from_s3": {"options": ["-s", "--use-s3"]},
    "terraform_directory_path": {"options": ["-w", "--in"]},
    "output_directory_path": {"options": ["-o", "--out"]},
    "idem_describe_path": {"options": ["-i", "--idem-desc"]},
    "tf_state_file_path": {"options": ["-t", "--tf-state"]},
    "group_style": {"options": ["-g", "--group-style"]},
    "type": {"options": ["--type"], "subcommands": ["generate"]},
}

# These are the namespaces that your project extends
# The hub will extend these keys with the modules listed in the values
DYNE = {
    "idem_codegen": ["idem_codegen"],
    "tf_idem": ["tf_idem"],
    "discovery": ["discovery"],
}
