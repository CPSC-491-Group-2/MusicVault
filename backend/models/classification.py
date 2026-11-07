"""Data classification labels for database columns.

Every column carries its level in ``Column.info["classification"]``. The
policy is docs/data-classification.md and the full inventory is
docs/data-classification-inventory.csv. tests/security/
test_data_classification.py fails CI if a column is missing a label or
disagrees with the inventory.
"""

from __future__ import annotations

import csv
from enum import StrEnum
from pathlib import Path

from sqlalchemy import MetaData

INFO_KEY = "classification"

INVENTORY_FILE = (
    Path(__file__).resolve().parents[2] / "docs" / "data-classification-inventory.csv"
)


class DataClass(StrEnum):
    """Classification levels, least to most sensitive."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


def classified(level: DataClass) -> dict[str, DataClass]:
    """The ``info`` dict for a mapped_column of the given level."""
    return {INFO_KEY: level}


def column_classifications(metadata: MetaData) -> dict[str, str | None]:
    """Map "table.column" to its label (None if unlabeled) for every column."""
    return {
        f"{table.name}.{column.name}": column.info.get(INFO_KEY)
        for table in metadata.sorted_tables
        for column in table.columns
    }


def classification_problems(metadata: MetaData) -> list[str]:
    """Columns with no label, or a label that isn't a DataClass level."""
    valid = {level.value for level in DataClass}
    problems = []
    for name, label in column_classifications(metadata).items():
        if label is None:
            problems.append(f"{name}: no classification")
        elif label not in valid:
            problems.append(f"{name}: unknown classification {label!r}")
    return problems


def load_inventory(path: Path = INVENTORY_FILE) -> dict[str, str]:
    """Map "table.column" to its classification in the inventory CSV."""
    inventory = {}
    with path.open(newline="") as file:
        for row in csv.DictReader(file):
            name = f"{row['table']}.{row['column']}"
            if name in inventory:
                raise ValueError(f"{path.name} lists {name} more than once")
            inventory[name] = row["classification"]
    return inventory
