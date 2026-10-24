from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def balances_path(year: int, part: int) -> str:
    """Path of a raw balances file in the `interim` filesystem."""
    return f"financial_statements/{year}/balances_{year}_{part}.txt"


def processed_path(stage: str, name: str, extension: str = "csv") -> str:
    """Path of a file in the `processed` filesystem, e.g. homologation/data2021.csv."""
    return f"{stage}/{name}.{extension}"
