import pytest
from decimal import Decimal

from src.models import Bill, Item, Payment
from src.calculator import compute_debts


def test_one_person_paid_all():
    bill = Bill(name="Test") # Alice paid full bill, others owe money
    
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
    
    bill.payments.append(
        Payment(user_id=alice.id, amount=Decimal("300"))
    )
    
    result = compute_debts(bill, method="equal")
    
    assert len(result) == 2
    total_debt = sum(amount for _, _, amount in result)
    
    assert total_debt == Decimal("200")


def test_empty_bill():
    bill = Bill(name="Test") # Empty bill should return no debts
    
    bill.add_user("Alice")
    
    result = compute_debts(bill, method="equal")
    
    assert result == []


def test_proportional_who_ate_what():
    bill = Bill(name="Test") # Users pay only for consumed items
    
    bill.add_user("Alice")
    bill.add_user("Bob")
    bill.add_user("Charlie")
    
    alice = bill.get_user_by_name("Alice")
    bob = bill.get_user_by_name("Bob")
    charlie = bill.get_user_by_name("Charlie")
    
    # Pizza for Alice and Bob
    bill.items.append(Item( 
        name="Pizza",
        price=Decimal("200"),
        consumers=[alice.id, bob.id],
        quantity=1
    ))
    
    # Salad for everyone
    bill.items.append(Item(
        name="Salad",
        price=Decimal("90"),
        consumers=[alice.id, bob.id, charlie.id],
        quantity=1
    ))
    
    # Alice paid full amount
    bill.payments.append(
        Payment(user_id=alice.id, amount=Decimal("290"))
    )
    
    result = compute_debts(bill, method="proportional")
    
    charlie_debt = None
    
    for from_id, to_id, amount in result:
        if from_id == charlie.id:
            charlie_debt = amount
            break
    
    assert charlie_debt == Decimal("30")


def test_proportional_no_consumers():
    bill = Bill(name="Test") # Item without consumers should be ignored
    
    bill.add_user("Alice")
    bill.add_user("Bob")
    
    alice = bill.get_user_by_name("Alice")
    
    bill.items.append(Item(
        name="Secret item",
        price=Decimal("100"),
        consumers=[],
        quantity=1
    ))
    
    bill.payments.append(
        Payment(user_id=alice.id, amount=Decimal("100"))
    )
    
    result = compute_debts(bill, method="proportional")
    
    assert result == []