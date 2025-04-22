import os
from typing import Any, Dict

import toml


def load_resume_data(file_path: str) -> Dict[str, Any]:
    """
    Load resume data from a TOML configuration file.

    Args:
        file_path (str): Path to the TOML configuration file

    Returns:
        Dict[str, Any]: Parsed resume data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume configuration file not found at {file_path}")

    with open(file_path, "r") as f:
        return toml.load(f)
