import collections
from datetime import datetime
from functools import partial
import uuid
from xml.etree.ElementTree import tostring

import requests

from ..base import GenericAPI, ERROR_THRESHOLD
from ...metadata import MetadataItem

from ._construction import algorithms as alg, xml_generation as xmlgen


class NotFoundError(Exception):
    pass


class Element:
    """
    Base class for a workflow element.

    Will be extended by Workflow, Process, and Decision.

    Parameters
    ----------
    name : str or None
        The name of the workflow element.
    assignee : str or None
        The username of the person to whom an element is assigned.
    notes : str or None
        Notes associated with the element.
    due_date : str or datetime or None
        The date by which the work associated with the element should be
        completed.
    parent : Workflow
        The parent workflow.
    parent_id : str
        The (HyperThought) id of the parent workflow.
        This should only be used when an element is being added to an
        existing workflow.  Otherwise, parent should be used.
    """
    def __init__(self, name=None, assignee=None, notes=None, due_date=None,
                 parent=None, parent_id=None):
        self._validate_nullable_nonempty_string(name)
        self._validate_nullable_nonempty_string(assignee)
        self._validate_nullable_nonempty_string(notes)
        self._validate_due_date(due_date)
        self._validate_parent(parent)
        self._validate_nullable_nonempty_string(parent_id)

        self._id = str(uuid.uuid4())
        # client_id is used by the UI library to identify canvas elements.
        self._client_id = str(uuid.uuid4())
        self._type = self.__class__.__name__.lower()
        self._name = name
        self._assignee = assignee
        self._notes = notes
        self._due_date = due_date
        self._parent = parent

        if parent:
            self._parent_id = parent.id
            self._parent.add_child(self)
        else:
            self._parent_id = parent_id

        self._successors = {}
        self._predecessors = {}

    def to_json(self):
        """
        Get JSON (dict) representation.

        This will get only the element itself, not including children.
        """
        # TODO:  Rework procedural generator to make JSON representations
        #        unnecessary.

        if isinstance(self.due_date, datetime):
            due_date = self.due_date.isoformat()
        else:
            due_date = self.due_date

        return {
            'id': self.id,
            'client_id': self.client_id,
            'type': self.type,
            'name': self.name,
            'assignee': self.assignee,
            'notes': self.notes,
            'due_date': due_date,
            'successors': list(self._successors.keys()),
            'predecessors': list(self._predecessors.keys()),
        }

    def is_valid(self, path=''):
        """
        Determine if element has all data needed by procedural generator.

        Parameters
        ----------
        path : str
            The path to the workflow.  Used to print the location of the error.
        """
        path = f"{path}/{self}"

        if not self.name:
            print(f"name missing: {path}")
            return False

        return True

    @property
    def id(self):
        return self._id

    @property
    def client_id(self):
        return self._client_id

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._validate_nullable_nonempty_string(value)
        self._name = value

    @property
    def assignee(self):
        return self._assignee

    @assignee.setter
    def assignee(self, value):
        self._validate_nullable_nonempty_string(value)
        self._assignee = value

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, value):
        self._validate_nullable_nonempty_string(value)
        self._notes = value

    @property
    def due_date(self):
        return self._due_date

    @due_date.setter
    def due_date(self, value):
        self._validate_due_date(value)
        self._due_date = value

    @property
    def parent(self):
        if not self._parent and self._parent_id:
            print(f"there is a parent_id, '{self._parent_id}', but no parent")

        return self._parent

    @parent.setter
    def parent(self, value):
        self._validate_parent(value)

        if self._parent == value:
            return

        self._parent = value
        self._parent_id = value.id if value else None

        for successor in self._successors.values():
            self.remove_successor(successor)

        for predecessor in self._predecessors.values():
            predecessor.remove_successor(self)

    @property
    def parent_id(self):
        return self._parent_id

    @parent_id.setter
    def parent_id(self, value):
        self._validate_nullable_nonempty_string(value)
        self.parent = None
        self._parent_id = value

    @property
    def successors(self):
        """Get list of successors (Element objects)."""
        return list(self._successors.values())

    @property
    def predecessors(self):
        """Get list of predecessors (Element objects)."""
        return list(self._predecessors.values())

    def add_successor(self, element):
        """Add a successor."""
        self._validate_element(element)

        if (
            not self.parent
            or
            not element.parent
            or
            self.parent != element.parent
        ):
            raise ValueError(
                "predecessor and successor must have the same (non-null) "
                "parent"
            )

        self._successors[element.id] = element
        element._predecessors[self.id] = self

    def remove_successor(self, element):
        self._validate_element(element)

        if element.id not in self._successors:
            return

        self._successors[element.id].pop()
        element._precessors[self.id].pop()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return f"unnamed_{self.__class__.__name__}"

    def _validate_nullable_nonempty_string(self, s):
        if s is None:
            return

        if not s or not isinstance(s, str):
            return ValueError("input must be None or a non-empty string")

    def _validate_due_date(self, due_date):
        if (
            due_date is not None
            and
            not isinstance(due_date, datetime)
            and
            not isinstance(due_date, str)
        ):
            raise ValueError("due_due must be None, a datetime, or a string")

    def _validate_element(self, element):
        if not isinstance(element, Element):
            raise ValueError("element must be an Element instance")

    def _validate_parent(self, parent):
        if parent is not None and not isinstance(parent, Workflow):
            raise ValueError("parent must be None or a Workflow instance")


class Workflow(Element):
    """
    Workflow data to be used as input to procedural generator.

    Parameters
    ----------
    space_id : str
        The id of the workspace where the workflow will be created.
        This will only be needed for top-level workflows.

    See base class for additional parameters.
    """
    # TODO:  Check for parent-child cycles.

    def __init__(self, space_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validate_nullable_nonempty_string(space_id)

        self._space_id = space_id
        self._children = {}

    @property
    def space_id(self):
        return self._space_id

    @space_id.setter
    def space_id(self, value):
        self._validate_nullable_nonempty_string(value)
        self._space_id = value

    @property
    def children(self):
        return list(self._children.values())

    def add_child(self, element):
        self._validate_element(element)
        self._children[element.id] = element
        element.parent = self

    def remove_child(self, element):
        self._validate_element(element)

        if element.id not in self._children:
            return

        self._children.pop(element.id)
        element.parent = None

        for child in self._children.values():
            child.remove_successor(element)
            element.remove_successor(child)

    def is_valid(self, path=''):
        """
        Determine whether the workflow has all data needed by procedural
        generator.

        Parameters
        ----------
        path : str
            The path to the workflow.  Used to print the location of the error.
        """
        if not super().is_valid(path):
            return False

        path = f"{path}/{self}"

        if not self._space_id and not self._parent and not self._parent_id:
            print(f"space_id, parent, or parent_id needed by {path}")
            return False

        for child in self._children.values():
            if not child.is_valid(path):
                return False

        return True

    def to_json(self):
        output = super().to_json()
        output['children'] = list(self._children.keys())
        return output


class Process(Element):
    """
    Process data to be used as input to procedural generator.

    Parameters
    ----------
    metadata : list of hyperthought.metadata.MetadataItem
        Metadata for the process.

    See base class for other parameters.
    """

    def __init__(self, metadata=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Python ids will be used as keys, to avoid duplicates.
        # Metadata names can be used multiple times, but a given MetadataItem
        # class instance can be used only once.
        self._metadata = {}

        if metadata:
            for metadata_item in metadata:
                self.add_metadata_item(metadata_item=metadata_item)

    @property
    def metadata(self):
        return list(self._metadata.values())

    def add_metadata_item(self, metadata_item):
        if not isinstance(metadata_item, MetadataItem):
            raise ValueError("metadata_item must be a MetadataItem")

        self._metadata[id(metadata_item)] = metadata_item

    def remove_metadata_item(self, metadata_item):
        if not isinstance(metadata_item, MetadataItem):
            raise ValueError("metadata_item must be a MetadataItem")

        item_id = id(metadata_item)

        if item_id not in self._metadata:
            return

        self._metadata.pop(item_id)

    def remove_metadata(self):
        self._metadata = {}

    def get_api_formatted_metadata(self):
        return [
            item.to_api_format() for item in self._metadata.values()
        ]

    def to_json(self):
        output = super().to_json()
        output['metadata'] = self.get_api_formatted_metadata()
        return output


class Decision(Element):
    """
    Decision data to be used as input to procedural generator.

    Parameters
    ----------
    decision_question : str
        A yes/no question associated with the decision.

    See base class for additional parameters.
    """
    VALID_SUCCESSOR_TYPES = {'yes', 'no'}

    def __init__(self, decision_question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validate_nullable_nonempty_string(decision_question)
        self._decision_question = decision_question
        self._successors_yes = {}
        self._successors_no = {}

        # Python ids will be used as keys, to avoid duplicates.
        # Metadata names can be used multiple times, but a given MetadataItem
        # class instance can be used only once.
        self._metadata = {}

    @property
    def metadata(self):
        return list(self._metadata.values())

    def add_metadata_item(self, metadata_item):
        if not isinstance(metadata_item, MetadataItem):
            raise ValueError("metadata_item must be a MetadataItem")

        self._metadata[id(metadata_item)] = metadata_item

    def remove_metadata_item(self, metadata_item):
        if not isinstance(metadata_item, MetadataItem):
            raise ValueError("metadata_item must be a MetadataItem")

        item_id = id(metadata_item)

        if item_id not in self._metadata:
            return

        self._metadata.pop(item_id)

    def remove_metadata(self):
        self._metadata = {}

    def get_api_formatted_metadata(self):
        return [
            item.to_api_format() for item in self._metadata.values()
        ]

    @property
    def decision_question(self):
        return self._decision_question

    @decision_question.setter
    def decision_question(self, value):
        self._validate_nullable_nonempty_string(value)
        self._decision_question = value

    @property
    def yes_successors(self):
        return list(self._successors_yes)

    @property
    def no_successors(self):
        return list(self._successors_no)

    def add_successor(self, element, successor_type):
        """
        Add a successor.

        Parameters
        ----------
        element : Element
            The element that will succeed the current element.
        successor_type : str
            The type of successor.  Must be 'yes' or 'no'.
        """
        self._validate_successor_type(successor_type)
        super().add_successor(element)

        if successor_type == 'yes':
            self._successors_yes[element.id] = element
        else:
            self._successors_no[element.id] = element

    def remove_successor(self, element):
        """Remove a successor."""
        super().remove_successor(element)

        if element.id in self._successors_yes:
            self._successors_yes.pop(element.id)

        if element.id in self._successors_no:
            self._successors_no.pop(element.id)

    def _validate_successor_type(self, successor_type):
        if successor_type not in self.VALID_SUCCESSOR_TYPES:
            return ValueError(
                f"successor_type must be in {self.VALID_SUCCESSOR_TYPES}"
            )

    def is_valid(self, path=''):
        """
        Determine whether a decision is valid.

        Parameters
        ----------
        path : str
            Used to print path to invalid elements.
        """
        if not super().is_valid(path):
            return False

        path = f"{path}/{self}"

        yes_successors = set(self._successors_yes.keys())
        no_successors = set(self._successors_no.keys())
        all_successors = set(self._successors.keys())

        if all_successors != yes_successors | no_successors:
            print(
                f"Invalid node: {path}.  "
                "Decision successors are incorrectly specified."
            )
            return False

        if not self.decision_question:
            print(f"Decision missing question: {path}.")
            return False

        return True

    def to_json(self):
        """Convert decision element to JSON."""
        output = super().to_json()
        output['decision_question'] = self.decision_question
        output['yes_successors'] = list(self._successors_yes.keys())
        output['no_successors'] = list(self._successors_no.keys())
        output['metadata'] = self.get_api_formatted_metadata()
        return output


class WorkflowAPI(GenericAPI):
    """
    Files API switchboard.

    Contains methods that (loosely) correspond to endpoints for the
    HyperThought workflow app.  The methods simplify some get/update tasks.

    Parameters
    ----------
    auth : auth.Authorization
        Authorization object used to get headers and cookies needed to call
        HyperThought endpoints.
    """

    VERSION = 'v1'

    def __init__(self, auth):
        super().__init__(auth)

        self._workflow_base_url = f"{self._base_url}/api/workflow/"

        if self.VERSION:
            self._workflow_base_url += f"{self.VERSION}/"

    def get_templates(self, space_id, parent_id=None,
                      sort_field='name', sort_direction='ascending'):
        """
        Get workflow templates in a given workspace.

        Parameters
        ----------
        space_id : str
            The id (uuid) of the workspace of interest.
        parent_id : str or None
            The id of the parent template.
        sort_field : str
            The field to sort by.
        sort_direction : str
            The sort direction.  Must be 'ascending' or 'descending'.

        Returns
        -------
        A list of dicts, each dict providing information on a workflow in the
        project.
        """
        curried_request = partial(
            requests.get,
            url=f"{self._base_url}/api/workflow/process/templates/",
            params={
                'workspaceId': space_id,
                'parentId': parent_id,
                'column': sort_field,
                'sortDirection': sort_direction,
            },
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method will throw an exception.
            self._report_api_error(response=r)

        return r.json()

    def get_active_workflows(self, space_id, parent_id=None,
                             sort_field='name', sort_direction='ascending'):
        """
        Get active workflows in a given workspace.

        Parameters
        ----------
        space_id : str
            The id (uuid) of the workspace of interest.
        parent_id : str or None
            The id of the parent template.
        sort_field : str
            The field to sort by.
        sort_direction : str
            The sort direction.  Must be 'ascending' or 'descending'.

        Returns
        -------
        A list of dicts, each dict providing information on a workflow in the
        project.
        """
        curried_request = partial(
            requests.get,
            url=f"{self._base_url}/api/workflow/process/active_workflows/",
            params={
                'workspaceId': space_id,
                'parentId': parent_id,
                'column': sort_field,
                'sortDirection': sort_direction,
            },
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method will throw an exception.
            self._report_api_error(response=r)

        # Process the data to eliminate UI-centric structure.
        raw_data = r.json()
        output = {}

        for raw_element in raw_data:
            output_key = raw_element['title']

            if output_key in output:
                output[output_key].extend(raw_element['children'])
            else:
                output[output_key] = raw_element['children']

        return output

    def get_children(self, workflow_id):
        """
        Get children (contained elements) of a parent workflow.

        Parameters
        ----------
        workflow_id : str
            The id (uuid) of the parent workflow or subworkflow.

        Returns
        -------
        A list of dicts, each dict corresponding to a MarkLogic document
        for a child (contained element).
        """
        url = f"{self._base_url}/api/workflow/process/{workflow_id}/children"
        curried_request = partial(
            requests.get,
            url=url,
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method will throw an exception.
            self._report_api_error(response=r)

        return r.json()

    def get_document(self, document_id):
        """
        Get a workflow document (process, workflow, or decision) given an id.

        Parameters
        ----------
        document_id : str or None
            The id of the process to get.  If provided, project_id and
            workflow_path will be ignored.  If None, project_id and
            workflow_path will need to be provided.

        Returns
        -------
        Returns a document associated with the given id.
        """
        curried_request = partial(
            requests.get,
            url=f"{self._workflow_base_url}process/{document_id}/",
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method will throw an exception.
            self._report_api_error(response=r)

        return r.json()

    def update_document(self, updated_document):
        """Commit updates to a process."""
        if not isinstance(updated_document, collections.abc.Mapping):
            raise ValueError("updated_document must be a Mapping (i.e., dict)")

        if 'id' not in updated_document:
            raise ValueError("updated_document must contain 'id'")

        document_id = updated_document.pop('id')

        # Transform data to fit endpoint spec.
        if 'content' in updated_document:
            updates = updated_document['content']

            if 'metadata' in updated_document and updated_document['metadata']:
                updates['metadata'] = updated_document['metadata']
        else:
            updates = updated_document

        if 'comments' in updates:
            updates.pop('comments')

        url = f"{self._base_url}/api/workflow/process/{document_id}/"
        curried_request = partial(
            requests.patch,
            url=url,
            json=updates,
        )
        # TODO:  Surround all such calls by try/except.  Report errors.
        r = self.attempt_api_call(curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method will throw an exception.
            self._report_api_error(response=r)

    def _get_permissions(self, element, space_id=None):
        """Get permissions for a workflow element."""
        if not isinstance(element, Element):
            raise ValueError("element must be an instance of Element")

        if space_id:
            return {
                'workspaces': {
                    space_id: 'edit'
                }
            }
        elif element.parent_id:
            parent = self.get_document(document_id=element.parent_id)

            if not parent:
                raise NotFoundError(
                    f"The parent workflow id, '{element.parent_id}', does "
                    "not correspond to a valid workflow document"
                )

            return parent['permissions']
        else:
            raise ValueError(
                f"Element with id {element.id} must have a parent_id "
                "if no space_id argument is provided"
            )

    def redraw_canvas(self, workflow_id):
        """
        Redraw a workflow canvas.

        This will place elements automatically according to the algorithm
        used in workflow generation.

        Parameters
        ----------
        workflow_id : str
            The id of the workflow to be redrawn.
        """
        # Get parent workflow.
        workflow = self.get_document(document_id=workflow_id)

        # Update XML.
        children = []

        for child_id in workflow['children']:
            child_document = self.get_document(document_id=child_id)
            # Translate into form needed for XML construction.
            child = {
                'id': child_id,
                'client_id': child_document['clientId'],
                'type': child_document['processType'],
                'name': child_document['name'],
                'predecessors': set(child_document['predecessors']),
                'successors': set(child_document['successors']),
            }

            if child_document['processType'] == 'decision':
                yes_successors = set()
                no_successors = set()

                for successor_id in child_document['decisionPath']:
                    if child_document['decisionPath'][successor_id] == 'yes':
                        yes_successors.add(successor_id)
                    elif child_document['decisionPath'][successor_id] == 'no':
                        no_successors.add(successor_id)

                child['yes_successors'] = yes_successors
                child['no_successors'] = no_successors

            children.append(child)

        children = alg.coordinates.add_coordinates(children)
        xml_ = tostring(xmlgen.create_xml(logical_children=children)).decode()
        xml_ = xml_.replace("\"", "\'")
        workflow['xml'] = xml_

        # Commit changes.
        self.update_document(updated_document=workflow)

    def _update_parent_workflow(self, parent_id, new_child_id):
        """
        Update a parent workflow when a client adds new elements to it.

        This should only be called when new elements are added to existing
        workflows.

        Parameters
        ----------
        parent_id : str
            The id of the parent workflow to be updated.
        new_child_id : str
            The id of the child element to be added.
        """
        # Get parent workflow.
        parent = self.get_document(document_id=parent_id)

        # Add new child id to children.
        child_ids = set(parent['children'])
        child_ids.add(new_child_id)
        parent['children'] = list(child_ids)

        # Commit changes.
        self.update_document(updated_document=parent)

        # Update XML.
        self.redraw_canvas(workflow_id=parent_id)

    def create_workflow(self, workflow, update_parent=True,
                        check_validity=True, permissions=None):
        """
        Create a workflow document (as opposed to process or decision).

        Parameters
        ----------
        workflow : Workflow
            Representation of workflow data.
        update_parent : bool
            Add workflow to parent workflow and regenerate the parent's XML.
            This should only be True if a workflow is added as a child to an
            existing workflow.
        check_validity : bool
            Check the workflow object for validity.
            Used to improve performance of recursive calls. Clients can ignore.
        permissions : dict or None
            Document permissions.
            Used in recursive calls.  Clients can ignore.
        """
        if check_validity and not workflow.is_valid():
            raise ValueError(f"invalid workflow: {workflow}")

        if not permissions:
            permissions = self._get_permissions(
                element=workflow,
                space_id=workflow.space_id,
            )

        # Create XML for canvas.
        children = [child.to_json() for child in workflow.children]
        children = alg.coordinates.add_coordinates(children)
        xml_ = tostring(xmlgen.create_xml(logical_children=children)).decode()
        xml_ = xml_.replace("\"", "\'")

        # Create payload.
        username = self._auth.get_username()
        create_date = datetime.now().isoformat()
        payload = {
            'xml': xml_,
            'pk': workflow.id,
            'name': workflow.name,
            'creator': username,
            'created': create_date,
            'modifier': username,
            'modified': create_date,
            'template': True,
            'process_type': workflow.type,
            'permissions': permissions,
            'children': [child.id for child in workflow.children],
            'client_id': workflow.client_id,
            'predecessors': [
                predecessor.id for predecessor in workflow.predecessors
            ],
            'successors': [
                successor.id for successor in workflow.successors
            ],
        }

        if workflow.parent_id:
            payload['parent_process'] = workflow.parent_id

        if workflow.notes:
            payload['notes'] = workflow.notes

        if workflow.assignee:
            payload['assignee'] = workflow.assignee

        if workflow.due_date:
            payload['dueDate'] = workflow.due_date

        url = f"{self._base_url}/api/workflow/process/"
        curried_request = partial(
            requests.post,
            url=url,
            json=payload,
        )
        r = self.attempt_api_call(curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method will throw an exception.
            self._report_api_error(response=r)

        if update_parent and workflow.parent_id:
            self._update_parent_workflow(
                new_child_id=workflow.id,
                parent_id=workflow.parent_id,
            )

        for child in workflow.children:
            if isinstance(child, Process):
                self.create_process(
                    process=child,
                    update_parent=False,
                    check_validity=False,
                    permissions=permissions,
                )
            elif isinstance(child, Workflow):
                self.create_workflow(
                    workflow=child,
                    update_parent=False,
                    check_validity=False,
                    permissions=permissions,
                )
            elif isinstance(child, Decision):
                self.create_decision(
                    decision=child,
                    update_parent=False,
                    check_validity=False,
                    permissions=permissions,
                )
            else:
                # TODO:  Raise exception.
                raise Exception(f"unimplemented child type: {child.type}")

    def create_process(self, process, update_parent=True, check_validity=True,
                       permissions=None):
        """
        Create a process document (as opposed to workflow or decision).

        Parameters
        ----------
        process : Process
            Representation of process data.
        update_parent : bool
            Add process to parent workflow and regenerate the parent's XML.
            This should only be True if a process is added as a child to an
            existing workflow.
        check_validity : bool
            Check the process object for validity.
            Used to improve performance of recursive calls. Clients can ignore.
        permissions : dict or None
            Document permissions.
            Used in recursive calls.  Clients can ignore.
        """
        if check_validity and not process.is_valid():
            raise ValueError(f"invalid process: {process}")

        if not permissions:
            permissions = self._get_permissions(element=process)

        if not process.parent_id:
            raise ValueError(f"Process without parent_id: {process.id}")

        username = self._auth.get_username()
        create_date = datetime.now().isoformat()
        payload = {
            'pk': process.id,
            'client_id': process.client_id,
            'name': process.name,
            'creator': username,
            'created': create_date,
            'modifier': username,
            'modified': create_date,
            'template': True,
            'process_type': process.type,
            'permissions': permissions,
            'parent_process': process.parent_id,
            'predecessors': [
                predecessor.id for predecessor in process.predecessors
            ],
            'successors': [
                successor.id for successor in process.successors
            ],
        }

        url = f"{self._base_url}/api/workflow/process/"
        curried_request = partial(
            requests.post,
            url=url,
            json=payload,
        )
        r = self.attempt_api_call(curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method will throw an exception.
            self._report_api_error(response=r)

        if update_parent:
            self._update_parent_workflow(
                new_child_id=process.id,
                parent_id=process.parent_id,
            )

        # Separate call needed for metadata.
        # TODO:  Modify POST endpoint to accept metadata.
        if process.metadata:
            # Get document.
            # (Can't user r.json() from previous call because documents
            # are formatted inconsistently.  That return value contains the
            # entire ML document.)
            # TODO:  Fix the above (in core-router).
            document = self.get_document(document_id=process.id)
            document['metadata'] = process.get_api_formatted_metadata()
            self.update_document(document)

    def create_decision(self, decision, update_parent=True,
                        check_validity=True, permissions=None):
        """
        Create a decision document (as opposed to process or decision).

        Parameters
        ----------
        decision : Decision
            Representation of decision data.
        update_parent : bool
            Add process to parent workflow and regenerate the parent's XML.
            This should only be True if a process is added as a child to an
            existing workflow.
        check_validity : bool
            Check the process object for validity.
            Used to improve performance of recursive calls. Clients can ignore.
        permissions : dict or None
            Document permissions.
            Used in recursive calls.  Clients can ignore.
        """
        if check_validity and not decision.is_valid():
            raise ValueError(f"invalid process: {decision}")

        if not permissions:
            permissions = self._get_permissions(element=decision)

        if not decision.parent_id:
            raise ValueError(f"Process without parent_id: {decision.id}")

        username = self._auth.get_username()
        create_date = datetime.now().isoformat()

        # Specify decision paths.
        decision_path = {}

        for successor_id in decision.yes_successors:
            decision_path[successor_id] = 'yes'

        for successor_id in decision.no_successors:
            decision_path[successor_id] = 'no'

        payload = {
            'pk': decision.id,
            'client_id': decision.client_id,
            'name': decision.name,
            'creator': username,
            'created': create_date,
            'modifier': username,
            'modified': create_date,
            'template': True,
            'process_type': decision.type,
            'permissions': permissions,
            'parent_process': decision.parent_id,
            'predecessors': [
                predecessor.id for predecessor in decision.predecessors
            ],
            'successors': [
                successor.id for successor in decision.successors
            ],
            'decision_path': decision_path,
        }

        url = f"{self._base_url}/api/workflow/process/"
        curried_request = partial(
            requests.post,
            url=url,
            json=payload,
        )
        r = self.attempt_api_call(curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method will throw an exception.
            self._report_api_error(response=r)

        if update_parent:
            self._update_parent_workflow(
                new_child_id=decision.id,
                parent_id=decision.parent_id,
            )

        # Separate call needed for metadata.
        # TODO:  Modify POST endpoint to accept metadata.
        if decision.metadata:
            # Get document.
            # (Can't user r.json() from previous call because documents
            # are formatted inconsistently.  That return value contains the
            # entire ML document.)
            # TODO:  Fix the above (in core-router).
            document = self.get_document(document_id=decision.id)
            document['metadata'] = decision.get_api_formatted_metadata()
            self.update_document(document)

    def add_link(self, source_id, target_id, decision_path=None):
        """
        Add a predecessor-successor relationship between workflow elements.

        Parameters
        ----------
        source_id : str
            The id of the element at the head of the edge connecting the two
            elements.
        target_id : str
            The id of the element at the tail of the edge.
        decision_path : str or None
            The path to be followed based on the decision, i.e. 'yes' or 'no'.
            If None, there will be no decision path and the source will
        """
        if not isinstance(source_id, str):
            raise ValueError("source_id must be a string")

        if not isinstance(target_id, str):
            raise ValueError("target_id must be a string")

        if decision_path is not None and decision_path not in ('yes', 'no'):
            raise ValueError("decision_path must be 'yes' or 'no' if provided")

        # Raise error if a decision path is specified and the source document
        # is not a decision, or if no decision path is specified and the source
        # document is a decision.
        source_document = self.get_document(document_id=source_id)

        if not source_document:
            raise ValueError(f"No document exists with id {source_id}")

        if 'processType' not in source_document:
            raise ValueError(
                f"Document with id {source_id} is not a valid workflow "
                "document.  It is missing a processType."
            )

        if (
            decision_path is not None
            and
            source_document['processType'] != 'decision'
        ):
            raise ValueError(f"Document with id {source_id} is not a decision")

        if (
            decision_path is None
            and
            source_document['processType'] == 'decision'
        ):
            raise ValueError(
                "A decision_path must be provided for a link from a decision."
            )

        # Add the predecessor-successor relationship.
        curried_request = partial(
            requests.post,
            url=(
                f"{self._workflow_base_url}"
                f"process/{source_id}/link/{target_id}/"
            ),
        )
        r = self.attempt_api_call(curried_request=curried_request)

        if r.status_code >= ERROR_THRESHOLD:
            # NOTE:  This method will throw an exception.
            self._report_api_error(response=r)

        # Add the decision path.
        if decision_path:
            source_document['decisionPath'][target_id] = decision_path
            self.update_document(updated_document=source_document)

        # Update the parent canvas to display the link.
        self.redraw_canvas(workflow_id=source_document['parentProcess'])
