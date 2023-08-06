
import json
from typing import Any
import os


def save_json(data: Any, filename: str):
    with open(filename, 'w') as f:
        json.dump(data, f, default=lambda o: o.__dict__, indent=4)


def load_json(filename: str):
    with open(filename, 'r') as f:
        return json.load(f)


def get_dirs(path: str) -> list[str]:
    return next(os.walk(path))[1]
