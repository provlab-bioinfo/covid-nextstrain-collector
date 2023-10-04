import json
import os
import csv

def load_config(config_path: str) -> dict[str, object]:
    with open(config_path, 'r') as f:
        config = json.load(f)

    return config