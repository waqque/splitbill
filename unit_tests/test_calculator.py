import pytest
from decimal import Decimal

from src.models import Bill, Item, Payment
from src.calculator import compute_debts


def test_one_person_paid_all():
    # Alice paid full bill, others owe money
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
    
    bill.payments.append(
        Payment(user_id=alice.id, amount=Decimal("300"))
    )
    
    result = compute_debts(bill, method="equal")
    
    assert len(result) == 2
    total_debt = sum(amount for _, _, amount in result)
    
    assert total_debt == Decimal("200")


def test_two_people_paid():
    # Multiple users paid for the bill
    bill = Bill(name="Test")
    
    bill.add_user("Alice")
    bill.add_user("Bob")
    bill.add_user("Charlie")
    
    bill.items.append(Item(
        name="Food",
        price=Decimal("300"),
        consumers=[],
        quantity=1
    ))
    
    alice = bill.get_user_by_name("Alice")
    bob = bill.get_user_by_name("Bob")
    
    bill.payments.append(
        Payment(user_id=alice.id, amount=Decimal("200"))
    )
    
    bill.payments.append(
        Payment(user_id=bob.id, amount=Decimal("100"))
    )
    
    result = compute_debts(bill, method="equal")
    
    assert len(result) > 0


def test_items_with_quantity():
    # Item quantity should affect total price
    bill = Bill(name="Test")
    
    bill.add_user("Alice")
    bill.add_user("Bob")
    
    bill.items.append(Item(
        name="Pizza",
        price=Decimal("100"),
        consumers=[],
        quantity=3
    ))
    
    alice = bill.get_user_by_name("Alice")
    
    bill.payments.append(
        Payment(user_id=alice.id, amount=Decimal("300"))
    )
    
    result = compute_debts(bill, method="equal")
    
    assert len(result) == 1
    assert result[0][2] == Decimal("150")


def test_empty_bill():
    # Empty bill should return no debts
    bill = Bill(name="Test")
    
    bill.add_user("Alice")
    
    result = compute_debts(bill, method="equal")
    
    assert result == []


def test_proportional_who_ate_what():
    # Users pay only for consumed items
    bill = Bill(name="Test")
    
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


def test_proportional_everyone_ate_same():
    # Everyone consumed the same item
    bill = Bill(name="Test")
    
    bill.add_user("Alice")
    bill.add_user("Bob")
    bill.add_user("Charlie")
    
    alice = bill.get_user_by_name("Alice")
    bob = bill.get_user_by_name("Bob")
    charlie = bill.get_user_by_name("Charlie")
    
    bill.items.append(Item(
        name="Pizza",
        price=Decimal("300"),
        consumers=[alice.id, bob.id, charlie.id],
        quantity=1
    ))
    
    bill.payments.append(
        Payment(user_id=alice.id, amount=Decimal("200"))
    )
    
    bill.payments.append(
        Payment(user_id=bob.id, amount=Decimal("100"))
    )
    
    result = compute_debts(bill, method="proportional")
    
    assert len(result) == 1
    assert result[0][2] == Decimal("100")


def test_proportional_no_consumers():
    # Item without consumers should be ignored
    bill = Bill(name="Test")
    
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


def test_simplify_one_debtor_one_creditor():
    # One debtor and one creditor
    bill = Bill(name="Test")
    
    bill.add_user("Alice")
    bill.add_user("Bob")
    
    bill.items.append(Item(
        name="Pizza",
        price=Decimal("200"),
        consumers=[],
        quantity=1
    ))
    
    alice = bill.get_user_by_name("Alice")
    
    bill.payments.append(
        Payment(user_id=alice.id, amount=Decimal("200"))
    )
    
    result = compute_debts(bill, method="equal")
    
    assert len(result) == 1
    assert result[0][2] == Decimal("100")


def test_simplify_two_debtors_one_creditor():
    # Two users owe one creditor
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
    
    bill.payments.append(
        Payment(user_id=alice.id, amount=Decimal("300"))
    )
    
    result = compute_debts(bill, method="equal")
    
    assert len(result) == 2