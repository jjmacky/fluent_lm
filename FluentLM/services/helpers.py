import json
from pathlib import Path
from typing import Dict
import secrets
import string
# from logging import PipelineLogger

def get_key_by_value(dictionary, target_value):
    keys = [key for key, value in dictionary.items() if value == target_value]
    return keys

def load_json(file_path: Path) -> Dict:
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        # PipelineLogger().get_logger().error(f"Error decoding JSON from {file_path}: {e}")
        raise

def save_json(data_to_write, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data_to_write, json_file, indent=4)

def contains_substring(substring, string_list):
    return any(substring in s for s in string_list)

def generate_random_string(length = 10):
    characters = string.ascii_letters
    return ''.join(secrets.choice(characters) for _ in range(length))
