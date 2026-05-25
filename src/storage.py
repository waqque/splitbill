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

    def list_bills(self) -> List[str]:
        files = list(self.data_dir.glob("*.json"))
        bills = []
        for filepath in files:
            data = self.load(filepath.name)
            if data:
                bills.append({"id": data.id, "name": data.name})
        return bills

    def _bill_to_dict(self, bill: Bill) -> dict:
        return {
            "id": bill.id,
            "name": bill.name,
            "created_at": bill.created_at.isoformat(),
            "users": [
                {"id": uid, "name": u.name}
                for uid, u in bill.users.items()
            ],
            "items": [
                {
                    "name": i.name,
                    "price": float(i.price),
                    "consumers": i.consumers,
                    "quantity": i.quantity
                }
                for i in bill.items
            ],
            "payments": [
                {"user_id": p.user_id, "amount": float(p.amount)}
                for p in bill.payments
            ],
            "settlements": bill.settlements
        }

    def _dict_to_bill(self, data: dict) -> Bill:
        bill = Bill(id=data["id"], name=data["name"])
        for u in data.get("users", []):
            user = User(name=u["name"], id=u["id"])
            bill.users[user.id] = user
        for i in data.get("items", []):
            item = Item(
                name=i["name"],
                price=Decimal(str(i["price"])),
                consumers=i["consumers"],
                quantity=i.get("quantity", 1)
            )
            bill.items.append(item)
        for p in data.get("payments", []):
            payment = Payment(
                user_id=p["user_id"],
                amount=Decimal(str(p["amount"]))
            )
            bill.payments.append(payment)
        bill.settlements = data.get("settlements", [])
        return bill