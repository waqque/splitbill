from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
import uuid


class BillError(Exception): # custom application error type
    pass


class UserNotFoundError(BillError): # user not found error
    pass


@dataclass 
class User: # user class
    name: str # user name
    id: str = field(default_factory=lambda: str(uuid.uuid4())) # user id


@dataclass
class Item: # item class
    name: str # item name
    price: Decimal # price
    consumers: List[str] # list of users (item consumers)
    quantity: int = 1 # quantity


@dataclass
class Payment: # payment class
    user_id: str # id (who paid)
    amount: Decimal # payment amount
    timestamp: datetime = field(default_factory=datetime.now) # payment time


@dataclass
class Bill: # bill class
    id: str = field(default_factory=lambda: str(uuid.uuid4())) # bill id
    name: str = "Новый счёт" # default bill name
    created_at: datetime = field(default_factory=datetime.now) # current time
    users: Dict[str, User] = field(default_factory=dict) # users dictionary
    items: List[Item] = field(default_factory=list) # list of items
    payments: List[Payment] = field(default_factory=list) # list of payments
    settlements: List[dict] = field(default_factory=list) # list of final debts

    def add_user(self, name: str) -> User: # method: add user
        user = User(name=name) # new user
        self.users[user.id] = user # saved to dictionary
        return user

    def get_user_by_name(self, name: str) -> Optional[User]:
        normalized_name = name.strip().lower()

        for user in self.users.values():
            if user.name.strip().lower() == normalized_name:
                return user

        return None

    def get_user_name(self, user_id: str) -> str: # method: get username by id
        user = self.users.get(user_id)
        return user.name if user else user_id