
import json
import uuid
from pathlib import Path
from typing import Any


def load_json(file_path: str | Path) -> Any:
    """
    Load JSON data from a file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(file_path: str | Path, data: Any) -> None:
    """
    Save Python data as formatted JSON.
    """

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Keep a value between minimum and maximum.
    """

    return max(minimum, min(value, maximum))


def calculate_percentage(
    value: float,
    total: float,
) -> float:
    """
    Calculate percentage safely.
    """

    if total == 0:
        return 0.0

    return (value / total) * 100


def generate_id(prefix: str = "ID") -> str:
    """
    Generate a unique identifier.
    """

    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"