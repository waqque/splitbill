import json
from pathlib import Path
from typing import Optional, List
from decimal import Decimal

from src.models import Bill, User, Item, Payment


class JSONStorage:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

    def save(self, bill: Bill, filename: str) -> None:
        filepath = self.data_dir / filename
        data = self._bill_to_dict(bill)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def load(self, filename: str) -> Optional[Bill]:
        filepath = self.data_dir / filename
        if not filepath.exists():
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return self._dict_to_bill(data)

