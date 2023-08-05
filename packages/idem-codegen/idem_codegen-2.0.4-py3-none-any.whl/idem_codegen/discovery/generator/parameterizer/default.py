from typing import Any
from typing import Dict

__contracts__ = ["parameterize"]


def parameterize(hub, sls_data: Dict[str, Any]):
    """
    This function takes sls_data as input loop through all the attribute values and
    check if they can be parameterized to {{params.get("test_variable")}} in sls.

    :param hub:
    :param sls_data:
    :return:
    """

    # TODO: Integrate Archer code here to parameterize

    return sls_data
