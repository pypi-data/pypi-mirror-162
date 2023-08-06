"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import json
from typing import Any
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.data.json import THIS_FILE_DIR as JSON_DATA_DIR

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
WEBCOLORS_JSON = JSON_DATA_DIR.joinpath("webcolors.json")
# endregion[Constants]


def get_webcolors_data() -> list[dict[str:Any]]:
    with WEBCOLORS_JSON.open('r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)
    _out = []
    for item_data in data:
        new_item_data = {}
        new_item_data["name"] = item_data.get("name").casefold()
        new_item_data["value"] = (item_data.get("rgb").get('r'), item_data.get("rgb").get('g'), item_data.get("rgb").get('b'), 1.0)
        _out.append(new_item_data)
    return _out
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
