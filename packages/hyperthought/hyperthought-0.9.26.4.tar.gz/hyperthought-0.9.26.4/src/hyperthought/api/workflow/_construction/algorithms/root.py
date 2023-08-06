"""
root.py

Find the root node given a flat array of inputs.

The inputs will have standard input keys.  For present purposes, the important
keys are 'id' and 'children'.
"""

# TODO:  Consolidate key constants.
ID_KEY = 'id'
CHILDREN_KEY = 'children'


def find_root(elements):
    """
    Find root node id given a flat list of elements.

    Parameters
    ----------
    elements : list of dict
        Keys include 'id', 'name', 'type', 'predecessors', 'successors',
        'children' for ('workflow' types), and 'metadata'
        (for 'process' types).

    Returns
    -------
    The id of the root node.
    """
    all_ids = {element[ID_KEY] for element in elements}
    child_ids = []

    for element in elements:
        if CHILDREN_KEY in element:
            child_ids.extend(element[CHILDREN_KEY])

    child_ids = set(child_ids)
    root_ids = all_ids - child_ids
    assert len(root_ids) == 1, "Invalid number of roots for workflow."
    return root_ids.pop()
