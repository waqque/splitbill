import pytest
from decimal import Decimal

from src.models import Bill, Item, Payment
from src.calculator import compute_debts


def test_one_person_paid_all():
    """Alice paid 300 for pizza. Bob and Charlie should pay 100 each"""
    bill = Bill(name="Test")
    bill.add_user("Alice")
    bill.add_user("Bob")
    bill.add_user("Charlie")
    
    bill.items.append(Item(
        name="Pizza",
        price=Decimal("300"),
        consumers=[],
        quantity=1
    ))
    
    alice = bill.get_user_by_name("Alice")
    bill.payments.append(Payment(user_id=alice.id, amount=Decimal("300")))
    
    result = compute_debts(bill, method="equal")
    
    assert len(result) == 2
    total_debt = sum(amount for _, _, amount in result)
    assert total_debt == Decimal("200")


def test_empty_bill():
    """Empty bill - no debts"""
    bill = Bill(name="Test")
    bill.add_user("Alice")
    
    result = compute_debts(bill, method="equal")
    
    assert result == []