from decimal import Decimal
from typing import List, Tuple, Dict
from collections import defaultdict

from src.models import Bill


def compute_debts(bill: Bill, method: str = "equal") -> List[Tuple[str, str, Decimal]]:
    if method == "equal":
        return _compute_equal_split(bill)
    elif method == "proportional":
        return _compute_proportional_split(bill)
    else:
        raise ValueError(f"Unknown method: {method}")


def _compute_equal_split(bill: Bill) -> List[Tuple[str, str, Decimal]]:
    if not bill.users or not bill.items:
        return []

    total = sum(item.price * item.quantity for item in bill.items)
    per_person = total / len(bill.users)

    paid = defaultdict(Decimal)
    for payment in bill.payments:
        paid[payment.user_id] += payment.amount

    balance = {}
    for user_id in bill.users:
        balance[user_id] = paid[user_id] - per_person

    return _simplify_debts(balance)


def _compute_proportional_split(bill: Bill) -> List[Tuple[str, str, Decimal]]:
    if not bill.users or not bill.items:
        return []

    consumed = defaultdict(Decimal)
    for item in bill.items:
        if not item.consumers:
            continue
        per_person = item.price / len(item.consumers)
        for consumer_id in item.consumers:
            consumed[consumer_id] += per_person

    paid = defaultdict(Decimal)
    for payment in bill.payments:
        paid[payment.user_id] += payment.amount

    balance = {}
    for user_id in bill.users:
        balance[user_id] = paid[user_id] - consumed[user_id]

    return _simplify_debts(balance)


def _simplify_debts(balance: Dict[str, Decimal]) -> List[Tuple[str, str, Decimal]]:
    debts = []
    debtors = [(uid, bal) for uid, bal in balance.items() if bal < -Decimal('0.01')]
    creditors = [(uid, bal) for uid, bal in balance.items() if bal > Decimal('0.01')]

    debtors.sort(key=lambda x: x[1])
    creditors.sort(key=lambda x: -x[1])

    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor_id, debt_amount = debtors[i]
        creditor_id, credit_amount = creditors[j]

        amount = min(-debt_amount, credit_amount)
        if amount > Decimal('0.01'):
            debts.append((debtor_id, creditor_id, amount.round(2)))

        debtors[i] = (debtor_id, debt_amount + amount)
        creditors[j] = (creditor_id, credit_amount - amount)

        if abs(debtors[i][1]) < Decimal('0.01'):
            i += 1
        if abs(creditors[j][1]) < Decimal('0.01'):
            j += 1

    return debts