"""
    Grouping mechanism for discovery to group all co-related resources
"""


def segregate(hub, run_name: str):
    hub[run_name].group.default.segregate(run_name)
