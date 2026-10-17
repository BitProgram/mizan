"""Domain models for MizanZarb.

Dataclasses only. No business logic. No I/O. Shapes for every entity
the engine knows about.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal, Protocol

from .money import ZERO

Currency = Literal["USD", "EUR", "GBP", "PKR", "INR", "AED", "SAR"]
CustomerStatus = Literal["trial", "active", "churned", "paused"]
ExpenseCategory = Literal[
    "infra",
    "tools",
    "hardware",
    "marketing",
    "education",
    "office",
    "tax",
    "other",
]
Platform = Literal["stripe", "paddle", "appstore", "gumroad", "direct", "manual"]
ProductStatus = Literal["prelaunch", "live", "sunset"]
RecurPeriod = Literal["monthly", "yearly", "weekly"]
SubPlan = Literal["monthly", "annual", "lifetime", "once"]
SubStatus = Literal["active", "past_due", "cancelled", "expired", "trial"]
TxnType = Literal["charge", "refund", "chargeback", "payout"]

@dataclass
class Settings:
    """Global configuration, written once at first run."""

    currency: Currency = "USD"
    tax_reserve_percent: Decimal = Decimal("0.30")
    savings_target_percent: Decimal = Decimal("0.20")
    monthly_income_goal: Decimal = Decimal("10000")
    ltv_amortize_lifetime_months: int = 24
    consulting_rate_hourly: Decimal = Decimal("75")


@dataclass
class Product:
    """A software product you ship and monetize."""
    id: int
    name: str
    launch_date: str | None = None
    status: ProductStatus = "prelaunch"
    dev_hours_logged: Decimal = ZERO
    note: str | None = None


@dataclass
class Customer:
    """A paying (or formerly paying) customer."""
    id: int
    email: str
    product_id: int
    acquired_via: str = "organic"
    acquired_date: str | None = None
    status: CustomerStatus = "active"
    churned_date: str | None = None
    country: str | None = None
    note: str | None = None


@dataclass
class Subscription:
    """A recurring or one-time revenue relationship with a customer."""

    id: int
    customer_id: int
    plan: SubPlan
    gross_price: Decimal
    started_date: str
    platform: Platform
    current_period_end: str | None = None
    cancelled_date: str | None = None
    status: SubStatus = "active"
    original_price: Decimal | None = None
    note: str | None = None


@dataclass
class Transaction:
    """A single movement of money. The source of truth for revenue."""

    id: int
    type: TxnType
    gross: Decimal
    platform_fee: Decimal
    net: Decimal
    date: str
    platform: Platform
    customer_id: int | None = None
    subscription_id: int | None = None
    note: str | None = None


@dataclass
class Expense:
    """A cost. The COGS flag drives gross-margin math."""

    id: int
    amount: Decimal
    category: ExpenseCategory
    date: str
    is_cogs: bool = False
    is_recurring: bool = False
    recur_period: RecurPeriod | None = None
    vendor: str | None = None
    note: str | None = None


@dataclass
class Lead:
    """An acquisition cost record. One row per spend event."""

    id: int
    date: str
    source: str
    cost: Decimal
    converted_customer_id: int | None = None
    note: str | None = None


@dataclass
class AppState:
    """The whole world. Everything MizanZarb knows lives here."""

    version: str = "0.0.1"
    settings: Settings = field(default_factory=Settings)
    products: list[Product] = field(default_factory=list)
    customers: list[Customer] = field(default_factory=list)
    subscriptions: list[Subscription] = field(default_factory=list)
    transactions: list[Transaction] = field(default_factory=list)
    expenses: list[Expense] = field(default_factory=list)
    leads: list[Lead] = field(default_factory=list)


class HasID(Protocol):
    """Any object with an integer .id attribute."""

    id: int


def next_id(items: list[HasID]) -> int:
    """Return the next ID for a list of entities that have an .id attribute."""
    if not items:
        return 1
    return max(item.id for item in items) + 1

