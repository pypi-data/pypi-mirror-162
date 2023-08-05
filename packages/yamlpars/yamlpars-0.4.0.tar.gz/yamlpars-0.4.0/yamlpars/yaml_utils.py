import pathlib
import re
from typing import Union


def lint_yaml_file(yaml_file: Union[str, pathlib.Path]) -> None:
    """Lint a yaml file, such that it passes yamllint.

    Args:
        yaml_file: the path to the file to lint.
    """

    # Fix spaces between comments
    # https://regex101.com/r/prKl93/2
    yaml_file = pathlib.Path(yaml_file)

    if not yaml_file.exists():
        raise FileNotFoundError(f"The file {yaml_file} does not exist.")

    with open(yaml_file, "r", encoding="UTF-8") as handle:
        content = handle.read()
        regex = r"^(\s*\w+[^\n\r#]+?)(?:[ \t]*)#(?:\s*)([^\n\r]*)$"
        subst = "\\g<1>  # \\g<2>"
        content_new = re.sub(regex, subst, content, 0, re.MULTILINE)
    with open(yaml_file, "w", encoding="UTF-8") as handle:
        handle.write(content_new)

    # Fix spaces at the end of the line and a final new line
    with open(yaml_file, "r", encoding="UTF-8") as handle:
        content = handle.read()
        regex = r"^(.*?)(?:\s*)$"
        subst = "\\g<1>"
        content_new = re.sub(regex, subst, content, 0, re.MULTILINE)
    with open(yaml_file, "w", encoding="UTF-8") as handle:
        handle.write(content_new + "\n")
