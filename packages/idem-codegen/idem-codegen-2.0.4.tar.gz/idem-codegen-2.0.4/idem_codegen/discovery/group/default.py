"""
    Default group mechanism for discovery to group based on resource types
"""

__contracts__ = ["group"]


def segregate(hub, run_name: str):
    hub.idem_codegen.group.resource_type.segregate(run_name)
