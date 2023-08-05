============
idem-codegen
============

.. image:: https://img.shields.io/badge/made%20with-pop-teal
   :alt: Made with pop, a Python implementation of Plugin Oriented Programming
   :target: https://pop.readthedocs.io/

.. image:: https://img.shields.io/badge/made%20with-python-yellow
   :alt: Made with Python
   :target: https://www.python.org/

Description
===========

The existing cloud infrastructure gets managed either directly via cloud provider console or via software tools like Terraform.
The goal of project 'Idem CodeGen' is to onboard customers to use Idem for Infrastructure as Code (IaC) management solution by
discovering their existing infrastructure and to facilitate the process of migration for customers who currently use Terraform
for IaC management by converting terraform files into SLS files. Manually converting each Terraform file into SLS file is not a
feasible option for any Terraform customer as all files collectively may comprise of 1000+ resource objects distributed across 100+ files.
Also, for customers those use web console directly to manage the infrastructure, Idem can discover existing cloud infrastructure and automatically
generates SLS code for all discovered resources. 'Idem CodeGen' leverages this capability to organise the SLS code by automatically generating hierarchical,
maintainable and reusable SLS files.

Steps to run idem-codegen for terraform to idem IaC transformation
==================================================================

Run following commands::

    pip install -e .
    idem_codegen tf_idem -c [path_to_config_file]


Sample config file::

    {
        "idem_codegen": {
            "tf_state_bucket_name": "",
            "tf_state_key": "",
            "idem_describe": False,
            "get_tf_state_from_s3": False,
            "output_directory_path": "[path_to_output_directory]",
            "idem_describe_path": "[path_to_idem_describe_response_file]",
            "tf_state_file_path": "[path_to_tfstate_json_file]",
            "terraform_directory_path": "[path_to_terraform_directory]",
            "group_style": "default"
        }
    }

Steps to run idem-codegen for infrastructure discovery and IaC generation
=========================================================================

Run following commands::

    pip install -e .
    idem_codegen discovery -c [path_to_config_file]


Sample config file::

    {
        "idem_codegen": {
            "idem_describe": False,
            "output_directory_path": "[path_to_output_directory]",
            "idem_describe_path": "[path_to_idem_describe_response_file]",
            "group_style": "default"
        }
    }





Steps to generate resource_ids from terraform state file
========================================================

Run the following command::

    idem_codegen generate --type=resource_ids -c [path_to_config_file]

Note-: '--type' parameter is only required with 'generate' subcommand.

Sample config file::

    {
        "idem_codegen": {
            "output_directory_path": "[path_to_output_directory]",
            "tf_state_file_path": "[path_to_tfstate_json_file]",
        }
    }


Note-: Resource ids of security group rule have to be changed manually.

Run help command to understand more about configuration parameters::

    idem_codegen --help
