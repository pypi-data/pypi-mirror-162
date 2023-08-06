"""
General-purpose data structure and representation format for tasks
(stand-alone or part of a larger data workflow) that involve multiple
data resources.
"""
from __future__ import annotations
from typing import Union
import doctest
import json

class datatask(dict):
    """
    Data structure that represents a data task. A data task consists of:

    * an optional collection of data resource name definitions (to allow
      for use of concise references within the input and output entries),
    * an optional list of input data resources (with optional schemas), and
    * a required list of output data resources (with a schema required
      for each output).

    The resource definitions attribute should be a map of names to
    individual file paths or URIs.

    >>> dt = datatask({
    ...     "resources": {
    ...         "abc": "https://examples.org/abc.txt",
    ...         "xyz": "xyz.txt"
    ...     },
    ...     "inputs": {"abc": ["column"]},
    ...     "outputs": {"xyz": [{"abc": "column"}]}
    ... })

    Any attempt to construct an instance with an invalid collection of
    resource definitions raises an exception.

    >>> dt = {"resources": [], "outputs": {"xyz.txt": []}}
    >>> datatask(dt)
    Traceback (most recent call last):
      ...
    TypeError: resources attribute value must be a dictionary that maps \
resource name strings to file path or URI strings
    >>> datatask({"resources": {"abc": 123}, "outputs": {"xyz.txt": []}})
    Traceback (most recent call last):
      ...
    TypeError: each resource entry value must be a path or URI string

    A valid instance must have at least one input entry or one output entry.
    Having only input entries is acceptable (a data task may be executed for
    its side effects), as is having only output entries (a data task may be
    executed that generates data without referencing any input data).

    >>> datatask.from_json({})
    Traceback (most recent call last):
      ...
    ValueError: at least one input or output must be specified
    >>> datatask.from_json({"inputs": {}, "outputs": {}})
    Traceback (most recent call last):
      ...
    ValueError: at least one input or output must be specified

    Input entries are specified using a dictionary that maps each input
    resource name, path, or URI either directly to its schema (consisting of
    a list of column names) or to an input specification dictionary that can
    contain a schema definition (optional) and a boolean value indicating
    whether a header column is present (also optional).

    >>> dt = datatask({
    ...     "inputs": {"abc.txt": ["a", "b", "c"], "def.csv": {}},
    ...     "outputs": {"xyz.txt": []}
    ... })
    >>> dt = datatask({
    ...     "inputs": {
    ...         "abc.txt": {
    ...             "schema": ["a", "b", "c"],
    ...             "header": False
    ...         },
    ...         "def.csv": {}
    ...     },
    ...     "outputs": {"xyz.txt": []}
    ... })

    Any attempt to construct an instance with an invalid collection of
    input entries raises an exception.

    >>> dt = {"inputs": 123, "outputs": {"xyz.txt": []}}
    >>> datatask(dt)
    Traceback (most recent call last):
      ...
    TypeError: inputs attribute must be a list of resource names, paths, \
and/or URIs, or a dictionary mapping resource names, paths, and/or URIs to \
their corresponding specifications or schemas
    >>> dt = datatask({"inputs": [123]})
    Traceback (most recent call last):
      ...
    TypeError: each input resource name, path, or URI must be a string
    >>> dt = {"inputs": {123: []}, "outputs": {"xyz.txt": []}}
    >>> datatask(dt)
    Traceback (most recent call last):
      ...
    TypeError: each specified input must be a string corresponding to a defined \
resource name, a valid path, or a valid URI
    >>> datatask({"inputs": {"abc.txt": 123}})
    Traceback (most recent call last):
      ...
    TypeError: input must be associated with a schema or specification
    >>> datatask({"inputs": {"abc.txt": [123]}})
    Traceback (most recent call last):
      ...
    TypeError: input schema must be a list of strings
    >>> dt = datatask({"inputs": {"abc.txt": {"header": 123}}})
    Traceback (most recent call last):
      ...
    TypeError: input header indicator must be a boolean value
    >>> d = {"inputs": {"abc.txt": {"invalid_field": 123}}}
    >>> dt = datatask(d)
    Traceback (most recent call last):
      ...
    ValueError: input specification can only contain a schema definition and/or \
a header indicator

    Output entries are specified using a dictionary that maps each output
    resource name, path, or URI either directly to its schema or to an output
    specification dictionary that can contain a header row definition (optional)
    and a schema definition (required). The schema definition must consist of a
    list of dictionaries; no other constraints are enforced on the structure of
    a schema. A recommended approach is to use a single-entry dictionary such as
    ``{"abc.csv": "b"}`` to reference a named column ``"b"`` found in an input
    resource ``"abc.csv"``.

    >>> dt = datatask({
    ...     "resources": {
    ...         "xyz": "xyz.csv"
    ...     },
    ...     "inputs": {"abc.csv": ["a", "b", "c"]},
    ...     "outputs": {"xyz": [{"abc.csv": "c"}, {"abc.csv": "b"}]}
    ... })

    The header row definition must be a list of strings (corresponding to column
    names).

    >>> dt = datatask({
    ...     "resources": {
    ...         "xyz": "xyz.csv"
    ...     },
    ...     "inputs": {"abc.csv": ["a", "b", "c"]},
    ...     "outputs": {
    ...         "xyz": {
    ...             "schema": [{"z": {"abc.csv": 2}}, {"y": {"abc.csv": 1}}],
    ...             "header": True
    ...         }
    ...     }
    ... })

    Any attempt to construct an instance without with an invalid collection of
    output entries raises an exception.

    >>> datatask.from_json({"outputs": []})
    Traceback (most recent call last):
      ...
    ValueError: at least one input or output must be specified
    >>> dt = datatask({"outputs": [123]})
    Traceback (most recent call last):
      ...
    TypeError: each output resource name, path, or URI must be a string
    >>> datatask.from_json({"outputs": None})
    Traceback (most recent call last):
      ...
    TypeError: outputs attribute must be a dictionary mapping resource \
names, paths, and/or URIs to their corresponding specifications or schemas
    >>> datatask.from_json({"outputs": {123: []}})
    Traceback (most recent call last):
      ...
    ValueError: each specified output must be a string corresponding to a \
defined resource name, a valid path, or a valid URI
    >>> datatask.from_json({"outputs": {"xyz.txt": 123}})
    Traceback (most recent call last):
      ...
    TypeError: output must be associated with a schema or specification
    >>> datatask.from_json({"outputs": {"xyz.txt": [1, 2, 3]}})
    Traceback (most recent call last):
      ...
    TypeError: output schema must be a list of dictionaries
    >>> dt = datatask({
    ...     "outputs": {
    ...         "xyz.csv": {
    ...             "schema": [{"abc.csv": 2}, {"abc.csv": 1}],
    ...             "header": 123
    ...         }
    ...     }
    ... })
    Traceback (most recent call last):
      ...
    TypeError: output header indicator must be a boolean value
    >>> d = {"outputs": {"xyz.csv": {"invalid_field": 123}}}
    >>> dt = datatask(d)
    Traceback (most recent call last):
      ...
    ValueError: output specification can only contain a schema definition and a \
header definition
    """
    def __new__(cls, argument: dict) -> datatask:
        """
        Create class instance from a dictionary with a compatible structure.

        >>> datatask({"inputs": {}, "outputs": {"xyz.txt":[]}})
        {'inputs': {}, 'outputs': {'xyz.txt': []}}
        """
        # Check that the resources attribute has a valid structure.
        resources = {}
        if "resources" in argument:
            if not isinstance(argument["resources"], dict):
                raise TypeError(
                    'resources attribute value must be a dictionary ' +
                    'that maps resource name strings to file path or ' +
                    'URI strings'
                )

            resources = argument["resources"]
            if not all(isinstance(uri, str) for uri in resources.values()):
                raise TypeError(
                    'each resource entry value must be a path or URI string'
                )

        # Check that the inputs attribute has a valid structure.
        if "inputs" in argument:
            if not isinstance(argument["inputs"], (list, dict)):
                raise TypeError(
                    'inputs attribute must be a list of resource names, paths, ' +
                    'and/or URIs, or a dictionary mapping resource names, paths, ' +
                    'and/or URIs to their corresponding specifications or schemas'
                )

            if isinstance(argument["inputs"], list):
                if not all(isinstance(input, str) for input in argument["inputs"]):
                    raise TypeError(
                        'each input resource name, path, or URI must be a string'
                    )

            if isinstance(argument["inputs"], dict):
                for (name_or_uri, specification) in argument["inputs"].items():
                    # Ensure the input reference is valid.
                    if not isinstance(name_or_uri, str):
                        raise TypeError(
                            'each specified input must be a string corresponding to ' +
                            'a defined resource name, a valid path, or a valid URI'
                        )

                    # Ensure that the specification has a valid structure.
                    (header, schema) = (False, None)
                    if isinstance(specification, list):
                        schema = specification
                    elif isinstance(specification, dict):
                        if not set(specification.keys()).issubset({"schema", "header"}):
                            raise ValueError(
                                'input specification can only contain a schema ' +
                                'definition and/or a header indicator'
                            )
                        schema = specification.get("schema", [])
                        header = specification.get("header", False)
                    else:
                        raise TypeError(
                            'input must be associated with a schema or specification'
                        )

                    if not isinstance(header, bool):
                        raise TypeError(
                            'input header indicator must be a boolean value'
                        )

                    if not (
                        isinstance(schema, list) and
                        all(isinstance(column, str) for column in schema)
                    ):
                        raise TypeError('input schema must be a list of strings')

        # Check that the outputs attribute has a valid structure.
        if "outputs" in argument:
            if not isinstance(argument["outputs"], (list, dict)):
                raise TypeError(
                    'outputs attribute must be a dictionary mapping ' +
                    'resource names, paths, and/or URIs to their ' +
                    'corresponding specifications or schemas'
                )

            if isinstance(argument["outputs"], list):
                if not all(isinstance(output, str) for output in argument["outputs"]):
                    raise TypeError(
                        'each output resource name, path, or URI must be a string'
                    )

            if isinstance(argument["outputs"], dict):
                for (name_or_uri, specification) in argument["outputs"].items():
                    # Ensure the output reference is valid.
                    if not isinstance(name_or_uri, str):
                        raise ValueError(
                            'each specified output must be a string corresponding ' +
                            'to a defined resource name, a valid path, or a valid URI'
                        )

                    # Ensure that the specification has a valid structure.
                    (header, schema) = (False, None)
                    if isinstance(specification, list):
                        schema = specification
                    elif isinstance(specification, dict):
                        if not set(specification.keys()).issubset({"schema", "header"}):
                            raise ValueError(
                                'output specification can only contain a schema ' +
                                'definition and a header definition'
                            )
                        schema = specification.get("schema", [])
                        header = specification.get("header", False)
                    else:
                        raise TypeError(
                            'output must be associated with a schema or specification'
                        )

                    if not isinstance(header, bool):
                        raise TypeError('output header indicator must be a boolean value')

                    if not (
                        isinstance(schema, list) and
                        all(isinstance(column, dict) for column in schema)
                    ):
                        raise TypeError('output schema must be a list of dictionaries')

        # Check that the instance is non-trivial.
        if (
            ("inputs" not in argument or len(argument.get("inputs", {})) == 0) and
            ("outputs" not in argument or len(argument.get("outputs", {})) == 0)
        ):
            raise ValueError('at least one input or output must be specified')

        return dict.__new__(cls, argument)

    @staticmethod
    def from_json(argument: Union[str, dict]) -> datatask:
        """
        Parse a dictionary or JSON string into an instance of this class.

        >>> datatask.from_json('{"outputs": {"xyz.txt":[]}}')
        {'outputs': {'xyz.txt': []}}
        >>> datatask.from_json({"inputs": {}, "outputs": {"xyz.txt":[]}})
        {'inputs': {}, 'outputs': {'xyz.txt': []}}
        """
        if isinstance(argument, str):
            argument = json.loads(argument)

        return datatask(argument)

    def to_json(self: datatask, *args, **kwargs) -> str:
        """
        Convert an instance of this class into a JSON string.

        >>> dt = datatask({"outputs": {"abc.text": []}})
        >>> dt.to_json()
        '{"outputs": {"abc.text": []}}'

        All arguments supplied to this method are passed directly to the internal
        invocation of :obj:`json.dumps`.

        >>> print(dt.to_json(indent=2))
        {
          "outputs": {
            "abc.text": []
          }
        }
        """
        return json.dumps(self, *args, **kwargs)

    def resources(self: datatask) -> dict:
        """
        Return dictionary mapping resource name to resource URIs for this instance.

        >>> dt = datatask.from_json({
        ...     "inputs": {"abc.txt": {}},
        ...     "outputs": {"xyz.text": [{"abc.txt": 0}]}
        ... })
        >>> dt.resources()
        {}
        """
        return self.get("resources", {})

    def inputs(self: datatask) -> dict:
        """
        Return dictionary of inputs for this instance.

        >>> dt = datatask.from_json({
        ...     "inputs": {"abc.txt": {}},
        ...     "outputs": {"xyz.text": [{"abc.txt": 0}]}
        ... })
        >>> dt.inputs()
        {'abc.txt': {}}
        """
        return self.get("inputs", {})

    def outputs(self: datatask) -> dict:
        """
        Return dictionary of outputs for this instance.

        >>> dt = datatask.from_json({
        ...     "inputs": {"abc.txt": {}},
        ...     "outputs": {"xyz.text": [{"abc.txt": 0}]}
        ... })
        >>> dt.outputs()
        {'xyz.text': [{'abc.txt': 0}]}
        """
        return self.get("outputs", {})

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
