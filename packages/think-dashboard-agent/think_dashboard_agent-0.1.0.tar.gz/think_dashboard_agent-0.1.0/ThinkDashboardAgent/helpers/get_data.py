from typing import Dict, Any
import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_data() -> Dict[str, Any]:
    with open(BASE_DIR / 'config.yaml') as f:
        data: Dict[str, Any] = yaml.load(f, Loader=yaml.FullLoader)
    return data
