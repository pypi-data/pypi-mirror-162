import pathlib
from operator import getitem, setitem
from typing import Any, Dict, List, MutableMapping, Union

from addict import Addict
from ruamel.yaml import YAML


class Parameters:
    """The Parameters object loads the yaml files from the folder specified in the constructor,
    and allows easy dot-notation access to the parameters, as well as an useful serialization
    methods.

    Attributes:
        yaml_folder (str | pathlib.Path): the folder containing the yaml files.
        auto_load (bool): if True, the yaml files are loaded automatically when
            the object is created. The default is True.
    Example:
        >>> pars = Parameters("path/to/yaml/folder")
        >>> pars.group_a.a_int
        1
        >>> pars.group_a.a_float
        1.0
    """

    def __init__(
        self, yaml_folder: Union[str, pathlib.Path], auto_load: bool = True
    ) -> None:
        super().__init__()
        self._keys: List[str] = []
        self._yaml_folder = pathlib.Path(yaml_folder)
        self._successful_load = False

        if auto_load:
            self.load()

    def load(self) -> None:
        """Load parameters into the object by parsing the yaml files.

        Raises:
            FileNotFoundError: the folder containing the yaml files does not exist.
        """
        yaml = YAML()

        if self._yaml_folder.exists():
            for suffix in ["yaml", "yml"]:
                for file in self._yaml_folder.glob(f"*.{suffix}"):
                    file_name = file.with_suffix("").name
                    with open(file, "r", encoding="UTF-8") as file_handle:
                        loaded_dict = yaml.load(file_handle)
                        if loaded_dict is not None:
                            self.__setattr__(file_name, Addict(loaded_dict))
                            self._keys.append(file_name)
        else:
            raise FileNotFoundError(f"The folder {self._yaml_folder} does not exist.")

        del yaml
        self._successful_load = True

    @property
    def __dict__(self):
        """Return the parameters as a dictionary."""
        if self._successful_load:
            return {key: self.__getattribute__(key) for key in self._keys}
        else:
            return {}

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        if self._successful_load:
            return str(
                f'Parameters object, loading from "{self._yaml_folder}":\n'
                + self.__dict__.__repr__()
            )
        else:
            return f"Parameters object, did not load yaml folder yet."

    @staticmethod
    def _flatten_dict_gen(
        dict_to_flatten: MutableMapping[str, Any], parent_key: str, separator: str
    ):
        """https://www.freecodecamp.org/news/how-to-flatten-a-dictionary-in-python-in-4-different-ways/"""
        for k, v in dict_to_flatten.items():
            new_key = parent_key + separator + k if parent_key else k
            if isinstance(v, MutableMapping):
                yield from Parameters._flatten_dict(
                    v, new_key, separator=separator
                ).items()
            else:
                yield new_key, v

    @staticmethod
    def _flatten_dict(
        dict_to_flatten: MutableMapping, parent_key: str = "", separator: str = "."
    ) -> Dict[str, Any]:
        """https://www.freecodecamp.org/news/how-to-flatten-a-dictionary-in-python-in-4-different-ways/"""
        return dict(
            Parameters._flatten_dict_gen(dict_to_flatten, parent_key, separator)
        )

    def serialize(self) -> Dict[str, Any]:
        """Return the parameters as a dictionary of depth one.

        Example:
            >>> pars.serialize()
            { 'group_a.a_int': 1,
              'group_a.a_float': 1.0,
              'group_a.a_bool': True,
              'group_a.a_dictionary.first_key': 'first',
              'group_a.a_dictionary.second_key': 'second',
            ...
        """
        return Parameters._flatten_dict(self.__dict__)

    def replace_entry(self, key: str, value: Any, type_check: bool = True) -> None:
        """Replace the value of a parameter.

        Args:
            key (str): the key of the parameter to replace.
            value (typing.Any): the new value of the parameter.
            type_check (bool): if True, the type of the value is checked against the
                type of the parameter, and an error is raised if the types do not match.
                The default is True.

        Example:
            >>> pars.replace_entry("group_a.a_dictionary.first_key", 'some_new_value')

        Raises:
            KeyError: the key does not exist in the parameters.
            TypeError: the type of the value does not match the type of the parameter.
        """

        split_key = key.split(".")

        # First step is attr, next is items.
        head = split_key.pop(0)
        object_ref = getattr(self, head)
        if not isinstance(object_ref, dict):
            raise KeyError(f"Could not find {key} in the Parameters object.")

        while len(split_key) > 1:
            head = split_key.pop(0)
            object_ref = getitem(object_ref, head)
            if not isinstance(object_ref, dict):
                raise KeyError(f"Could not find {key} in the Parameters object.")

        if type_check:  # Check that the type matches the type of the parameter.
            last_value = getitem(object_ref, split_key[0])
            if not issubclass(type(last_value), type(value)):
                raise TypeError(
                    f"The type of {key} in the Parameters object. is not the same as the type of the replace value. "
                    + f"It should be {type(last_value)}, but it is {type(value)}."
                )
        setitem(object_ref, split_key[0], value)
