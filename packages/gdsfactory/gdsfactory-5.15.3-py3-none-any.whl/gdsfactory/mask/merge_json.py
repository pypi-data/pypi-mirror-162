"""Combine multiple JSONs into one."""

import json
import pathlib
from typing import Any, Dict

from gdsfactory.config import logger
from gdsfactory.types import PathType


def merge_json(
    doe_directory: PathType,
    json_version: int = 6,
) -> Dict[str, Any]:
    """Returns combined dict with several JSON files from doe_directory

    Args:
        doe_directory: defaults to current working directory
        json_version:

    """
    logger.debug(f"Merging JSON files from {doe_directory}")
    cells = {}
    doe_directory = pathlib.Path(doe_directory)

    for filename in doe_directory.glob("**/*.json"):
        logger.debug(f"merging {filename}")
        with open(filename) as f:
            data = json.load(f)
            cells.update(data.get("cells"))

    does = {d.stem: json.loads(open(d).read()) for d in doe_directory.glob("**/*.json")}
    return dict(
        json_version=json_version,
        cells=cells,
        does=does,
    )


if __name__ == "__main__":
    from pprint import pprint

    from gdsfactory.config import cwd

    d = merge_json(doe_directory=cwd)
    pprint(d)
