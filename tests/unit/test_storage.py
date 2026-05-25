import pytest
import json
import tempfile
from pathlib import Path
from decimal import Decimal
from src.storage import JSONStorage
from src.models import Bill, User, Item, Payment


class TestJSONStorage:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def storage(self, temp_dir):
        return JSONStorage(temp_dir)

    @pytest.fixture
    def sample_bill(self):
        bill = Bill(name="Тестовый счёт")
        bill.add_user("Антон")
        bill.add_user("Мария")
        item = Item(
            name="Пицца",
            price=Decimal("1000"),
            consumers=list(bill.users.keys())
        )
        bill.items.append(item)
        payment = Payment(
            user_id=list(bill.users.keys())[0],
            amount=Decimal("1000")
        )
        bill.payments.append(payment)
        return bill

    def test_save_bill(self, storage, sample_bill):
        filename = "test_bill.json"
        storage.save(sample_bill, filename)
        
        filepath = storage.data_dir / filename
        assert filepath.exists()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert data["name"] == "Тестовый счёт"
        assert len(data["users"]) == 2
        assert len(data["items"]) == 1

    def test_load_bill(self, storage, sample_bill):
        filename = "test_bill.json"
        storage.save(sample_bill, filename)
        
        loaded = storage.load(filename)
        assert loaded is not None
        assert loaded.name == sample_bill.name
        assert len(loaded.users) == len(sample_bill.users)
        assert len(loaded.items) == len(sample_bill.items)

    def test_load_nonexistent(self, storage):
        loaded = storage.load("nonexistent.json")
        assert loaded is None

    def test_list_bills(self, storage, sample_bill):
        storage.save(sample_bill, "bill1.json")
        
        bill2 = Bill(name="Второй счёт")
        storage.save(bill2, "bill2.json")
        
        bills = storage.list_bills()
        assert len(bills) == 2
        names = [b["name"] for b in bills]
        assert "Тестовый счёт" in names
        assert "Второй счёт" in names

    def test_save_and_load_preserves_data(self, storage, sample_bill):
        filename = "test_bill.json"
        storage.save(sample_bill, filename)
        loaded = storage.load(filename)
        
        assert loaded.id == sample_bill.id
        assert loaded.name == sample_bill.name
        
        original_user = list(sample_bill.users.values())[0]
        loaded_user = list(loaded.users.values())[0]
        assert original_user.name == loaded_user.name
        assert original_user.id == loaded_user.id

    def test_empty_data_dir(self, storage):
        bills = storage.list_bills()
        assert bills == []