"""
coordinates.py

Add logical row and column coordinates to workflow elements.

See the add_coordinates docstring for more information.
"""

from collections import defaultdict
from copy import deepcopy

from . import unionfind


_COLUMN_KEY = 'column'
_ROW_KEY = 'row'


def _add_columns(elements):
    """
    Assign columns in a notional workflow canvas grid to workflow elements.

    This functionality will be used to assign positions (x-coordinates)
    to elements of a connected component.

    A simple array could be used to track y-coordinates.  The length
    of the array would depend on the maximum number of columns identified
    in this function.

    Parameters
    ----------
    elements : list of dicts
        Each element should have keys 'id' (str), 'predecessors' (list of str),
        and 'successors' (list of str).  Predecessors and successors should be
        symmetric.  Values for a new key for the column (x-coordinate) will be
        added.

    Returns
    -------
    The elements array with column data added, as well as the number of columns
    required to render the workflow.
    """
    # Validate inputs.
    try:
        elements = [dict(element) for element in elements]
    except Exception:
        raise ValueError('elements must be list-like of dict-like')

    # Make sure that none of the elements have column attributes.
    for element in elements:
        if _COLUMN_KEY in element:
            del element[_COLUMN_KEY]

    # Create dict for fast lookup.
    try:
        element_map = {element['id']: element for element in elements}
    except Exception:
        raise ValueError("each element must have an 'id' field")

    # Keep track of elements that have been passed to the add_column
    # function, defined below.
    visited_element_ids = set()

    def add_column(element):
        """Add column key (int value) to each element."""
        if _COLUMN_KEY in element:
            return

        if element['id'] in visited_element_ids:
            raise ValueError('cycle detected')

        visited_element_ids.add(element['id'])

        if 'predecessors' not in element or not element['predecessors']:
            element[_COLUMN_KEY] = 0
            return

        max_predecessor_column = 0

        for predecessor_id in element['predecessors']:
            predecessor = element_map[predecessor_id]

            if _COLUMN_KEY not in predecessor:
                add_column(predecessor)

            if max_predecessor_column < predecessor[_COLUMN_KEY]:
                max_predecessor_column = predecessor[_COLUMN_KEY]

        element[_COLUMN_KEY] = max_predecessor_column + 1

    max_column = 0

    for element in elements:
        add_column(element)

        if element[_COLUMN_KEY] > max_column:
            max_column = element[_COLUMN_KEY]

    n_columns = max_column + 1  # Convert from maximum index to size.
    return elements, n_columns


def _add_rows(elements, n_columns, start_row=0):
    """
    Add row numbers to a connected component.

    First pass:  Add successors to subsequent columns in the same order the
    predecessors appear in current columns.

    Future work: Refine the algorithm to minimize edge crossing.

    Parameters
    ----------
    elements : list of dict
        List of dicts having keys 'id', 'predecessors', 'successors', and
        _COLUMN_KEY.
    n_columns : int
        The number of columns in the workflow.
    start_row : int
        The topmost logical row where elements will be placed.

    Returns
    -------
    The highest logical row number needed for the workflow.
    Row numbers will be added to elements in place.
    """
    START_COLUMN = 0
    column_to_elements = defaultdict(list)

    for element in elements:
        column_to_elements[element[_COLUMN_KEY]].append(element)

    # Add row numbers to the first column of elements.
    row_number = start_row

    for element in column_to_elements[START_COLUMN]:
        element[_ROW_KEY] = row_number
        row_number += 1

    highest_row_number = row_number - 1

    # Define function to recursively add row numbers to successor columns.
    def add_rows_to_successors(column_number):
        nonlocal highest_row_number
        column_elements = sorted(column_to_elements[column_number],
                                 key=lambda elem: elem[_ROW_KEY])
        successor_column_number = column_number + 1
        successors = {
            element['id']: element
            for element in column_to_elements[successor_column_number]
        }
        successor_ids_added = set()
        row_number = start_row

        for element in column_elements:
            successor_ids = element['successors']

            for successor_id in successor_ids:
                if (
                    successor_id in successors
                    and
                    successor_id not in successor_ids_added
                ):
                    successor = successors[successor_id]
                    successor[_ROW_KEY] = row_number
                    row_number += 1
                    successor_ids_added.add(successor_id)

        row_number -= 1

        if row_number > highest_row_number:
            highest_row_number = row_number

        if successor_column_number < n_columns - 1:
            add_rows_to_successors(successor_column_number)

    add_rows_to_successors(column_number=START_COLUMN)
    return highest_row_number


def _add_coordinates_to_component(elements, start_row=0):
    """
    Add row and column data to a connected component.

    Parameters
    ----------
    elements : list of dicts
        Each element should have keys 'id' (str) and 'predecessors'
        (list of str).
        Values for a new key for the column (x-coordinate) will be added.
    start_row : int
        The starting row where sequenced elements should be placed.
        The idea is to put free elements, those without any predecessors or
        successors, at the top of the canvas in a grid.

    Returns
    -------
    A dict with keys 'elements' (elements array with logical row/column
    data added), 'max_column' (maximum column number needed), and
    'max_row' (maximum row number needed, taking start_row into consideration).
    """
    elements, n_columns = _add_columns(elements)
    max_row = _add_rows(elements, n_columns, start_row)
    return {
        'elements': elements,
        'max_column': n_columns - 1,  # Convert from number to highest index.
        'max_row': max_row,
    }


def add_coordinates(elements):
    """
    Add row and column data to all elements on a workflow canvas.

    Parameters
    ----------
    elements : list of dicts
        Each element should have keys 'id' (str), 'predecessors' (list of str),
        and 'successors' (list of str).

    Returns
    -------
    A copy of the elements list, with keys 'row' and 'column' added.
    The row/column numbers will be logical, zero-based numbers.
    They will eventually require translation into positions on the canvas.
    """
    # Validate elements.
    for element in elements:
        if not (
            'id' in element
            and
            'name' in element
            and
            'predecessors' in element
            and
            'successors' in element
        ):
            raise ValueError(
                "Input elements must contain keys 'id', 'name', "
                "'predecessors', and 'successors'."
            )

    # Start by identifying all unconnected elements.
    # These will be placed at the top.
    unconnected_elements = []
    remaining_elements = []

    for element in elements:
        if not element['predecessors'] and not element['successors']:
            unconnected_elements.append(element)
        else:
            remaining_elements.append(element)

    if unconnected_elements:
        unconnected_elements = deepcopy(unconnected_elements)
        ELEMENTS_PER_ROW = 5
        row = 0
        # Initialize to -1 so addition can precede usage.
        # This will allow the rows to be counted more easily.
        column = -1

        for element in unconnected_elements:
            column += 1

            if column >= ELEMENTS_PER_ROW:
                column = 0
                row += 1

            element[_ROW_KEY] = row
            element[_COLUMN_KEY] = column

        start_row = row + 1
    else:
        start_row = 0

    uf = unionfind.UnionFind()

    for element in remaining_elements:
        element_id = element['id']

        for predecessor_id in element['predecessors']:
            uf.union(element_id, predecessor_id)

    components = uf.get_components()
    id_to_element = {element['id']: element for element in remaining_elements}
    all_elements = list(unconnected_elements)

    for component in components:
        component_elements = [id_to_element[id_] for id_ in component]
        results = _add_coordinates_to_component(
            elements=component_elements,
            start_row=start_row,
        )
        all_elements.extend(results['elements'])
        start_row = results['max_row'] + 1

    return all_elements
