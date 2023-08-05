import pathlib
from operator import getitem, setitem
from typing import Any, Dict, Optional, Union

from ruamel.yaml import YAML

from .yaml_utils import lint_yaml_file


def update_yaml_file(
    yaml_folder: Union[str, pathlib.Path],
    file_name: str,
    update_dict: Dict[str, Any],
    record_file_name: Optional[str] = None,
    check_type: bool = True,
    lint_yaml_file_after_update: bool = True,
) -> None:
    """Update the entries in a yaml file according to the update_dict.

    Args:
        yaml_folder (str | pathlib.Path): the folder containing the yaml files.
        file_name (str): the name of the file to update, without the extension.
        update_dict (Dict[str, typing.Any]): the dictionary containing the
            updated values.
        record_file_name (str, optional): the name of the file used to keep track
            of the updates. If None, the record file is not updated.
        check_type (bool): if True, the type of the updated values is checked
            against the type of the original values. If the type is different,
            a TypeError is raised. The default is True.
        lint_yaml_file_after_update (bool): if True, the yaml file is linted
            after the update. The default is True.

    Raises:
        FileNotFoundError: the file to update does not exist.
        KeyError: a key in the update_dict does not exist in the original yaml file.
        TypeError: the type of the updated values is different from the original.

    Example:
        >>> update_yaml_file("path/to/yaml/folder", "group_a", {"a_int": 2, "a_float": 2.0})
    """

    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)

    yaml_file = pathlib.Path(yaml_folder) / (file_name + ".yaml")
    if not yaml_file.exists():
        yaml_file = pathlib.Path(yaml_folder) / (file_name + ".yml")
        if not yaml_file.exists():
            raise FileNotFoundError(f"The file {file_name}.yaml/yml does not exist.")

    with open(yaml_file, "r", encoding="UTF-8") as file_handle:
        parameters_dict = yaml.load(file_handle)

    # For each key in the update_dict, update the corresponding key in the parameters_dict.
    for key, value in update_dict.items():
        split_key = key.split(".")

        object_ref = parameters_dict

        while len(split_key) > 1:
            head = split_key.pop(0)
            object_ref = getitem(object_ref, head)
            if not isinstance(object_ref, dict):
                raise KeyError(f"Could not find {key} in {file_name}")

        if check_type:  # Check that the type matches.
            last_value = getitem(object_ref, split_key[0])
            if not issubclass(type(last_value), type(value)):
                raise TypeError(
                    f"The type of {key} in {file_name} is not the same as the type of the update value. "
                    + f"It should be {type(last_value)} but is {type(value)}."
                )
        setitem(object_ref, split_key[0], value)

    # Write the updated parameters to the file.
    with open(yaml_file, "w", encoding="UTF-8") as file_handle:
        yaml.dump(parameters_dict, file_handle)

    if lint_yaml_file_after_update:  # Lint the yaml file after the changes.
        lint_yaml_file(yaml_file)

    if record_file_name is not None:
        record_file = pathlib.Path(yaml_folder) / (record_file_name + ".yaml")

        with open(record_file, "a", encoding="UTF-8") as file_handle:
            record_dict = yaml.load(file_handle)

            for key, value in update_dict.items():
                record_dict[f"record_{key}_value"] = value
                record_dict[f"record_{key}_time"] = type(value).__name__
