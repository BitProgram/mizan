"""Tests for mizan.core.models."""

from decimal import Decimal

import pytest

from src.mizan.core.models import (
    AppState,
    Currency,
    Customer,
    CustomerStatus,
    Expense,
    ExpenseCategory,
    Lead,
    Platform,
    Product,
    ProductStatus,
    RecurPeriod,
    Settings,
    SubPlan,
    Subscription,
    SubStatus,
    Transaction,
    TxnType,
    next_id,
)
from src.mizan.core.money import ZERO


def test_all_type_aliases_are_importable() -> None:
    """Section 1 sanity: every alias must exist at import time."""
    aliases = [
        Currency,
        CustomerStatus,
        ExpenseCategory,
        Platform,
        ProductStatus,
        RecurPeriod,
        SubPlan,
        SubStatus,
        TxnType,
    ]
    assert len(aliases) == 9


def test_module_imports_without_error() -> None:
    """If models.py has any broken import, this fails immediately."""
    import src.mizan.core.models  # noqa: F401

# Settings()
def test_settings_constructs_with_all_defaults() -> None:
    """Settings() with no arguments should work — every field has a default."""
    settings = Settings()
    assert settings.currency == "USD"
    assert settings.tax_reserve_percent == Decimal("0.30")
    assert settings.savings_target_percent == Decimal("0.20")
    assert settings.monthly_income_goal == Decimal("10000")
    assert settings.ltv_amortize_lifetime_months == 24
    assert settings.consulting_rate_hourly == Decimal("75")


def test_settings_allows_overriding_one_field() -> None:
    """Overriding one field should leave the rest at defaults."""
    settings = Settings(currency="PKR")
    assert settings.currency == "PKR"
    assert settings.tax_reserve_percent == Decimal("0.30")


def test_settings_allows_overriding_multiple_fields() -> None:
    """Overriding multiple fields should work independently."""
    settings = Settings(
        currency="EUR",
        tax_reserve_percent=Decimal("0.25"),
        monthly_income_goal=Decimal("20000"),
    )
    assert settings.currency == "EUR"
    assert settings.tax_reserve_percent == Decimal("0.25")
    assert settings.monthly_income_goal == Decimal("20000")
    assert settings.savings_target_percent == Decimal("0.20")


def test_settings_dataclass_gives_free_repr() -> None:
    """@dataclass auto-generates __repr__ — no manual work needed."""
    settings = Settings()
    repr_str = repr(settings)
    assert "Settings(" in repr_str
    assert "currency='USD'" in repr_str


def test_settings_dataclass_gives_free_equality() -> None:
    """@dataclass auto-generates __eq__ — same fields, same value."""
    a = Settings()
    b = Settings()
    assert a == b

    c = Settings(currency="GBP")
    assert a != c

# Product()
def test_product_requires_id_and_name() -> None:
    """Product cannot be constructed without id and name."""
    with pytest.raises(TypeError):
        Product()  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        Product(id=1)  # type: ignore[call-arg]


def test_product_constructs_with_required_fields_only() -> None:
    """Two required fields — everything else should default."""
    product = Product(id=1, name="Mizan")
    assert product.id == 1
    assert product.name == "Mizan"
    assert product.launch_date is None
    assert product.status == "prelaunch"
    assert product.dev_hours_logged == ZERO
    assert product.note is None


def test_product_allows_overriding_optional_fields() -> None:
    """Every optional field should accept an override."""
    product = Product(
        id=1,
        name="ShipLedger",
        launch_date="2025-03-14",
        status="live",
        dev_hours_logged=Decimal("1240"),
        note="main product",
    )
    assert product.launch_date == "2025-03-14"
    assert product.status == "live"
    assert product.dev_hours_logged == Decimal("1240")
    assert product.note == "main product"


def test_product_default_dev_hours_is_zero_decimal() -> None:
    """The ZERO default should be Decimal, not float or int."""
    product = Product(id=1, name="X")
    assert product.dev_hours_logged == Decimal("0")
    assert isinstance(product.dev_hours_logged, Decimal)


def test_product_default_status_is_prelaunch() -> None:
    """A new product defaults to prelaunch — not live, not sunset."""
    product = Product(id=1, name="X")
    assert product.status == "prelaunch"


def test_product_equality_via_dataclass() -> None:
    """Two products with the same fields compare equal."""
    a = Product(id=1, name="Mizan")
    b = Product(id=1, name="Mizan")
    assert a == b

    c = Product(id=2, name="Mizan")
    assert a != c

# Customer()
def test_customer_requires_id_email_and_product_id() -> None:
    """All three required fields must be present."""
    with pytest.raises(TypeError):
        Customer()  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        Customer(id=1)  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        Customer(id=1, email="a@b.com")  # type: ignore[call-arg]


def test_customer_constructs_with_required_fields_only() -> None:
    """Three required fields — the rest should default."""
    customer = Customer(id=1, email="ab@cd.dev", product_id=1)
    assert customer.id == 1
    assert customer.email == "ab@cd.dev"
    assert customer.product_id == 1
    assert customer.acquired_via == "organic"
    assert customer.acquired_date is None
    assert customer.status == "active"
    assert customer.churned_date is None
    assert customer.country is None
    assert customer.note is None


def test_customer_allows_overriding_optional_fields() -> None:
    """Every optional field should accept an override."""
    customer = Customer(
        id=1,
        email="ab@cd.dev",
        product_id=1,
        acquired_via="twitter",
        acquired_date="2025-08-12",
        status="churned",
        churned_date="2026-02-28",
        country="UK",
        note="loved the product, moved on",
    )
    assert customer.acquired_via == "twitter"
    assert customer.acquired_date == "2025-08-12"
    assert customer.status == "churned"
    assert customer.churned_date == "2026-02-28"
    assert customer.country == "UK"
    assert customer.note == "loved the product, moved on"


def test_customer_product_id_is_foreign_key_not_product_object() -> None:
    """product_id is a plain int reference — no embedded Product instance."""
    customer = Customer(id=1, email="a@b.com", product_id=42)
    assert customer.product_id == 42
    assert isinstance(customer.product_id, int)


def test_customer_equality_via_dataclass() -> None:
    """Two customers with identical fields compare equal."""
    a = Customer(id=1, email="x@y.com", product_id=1)
    b = Customer(id=1, email="x@y.com", product_id=1)
    assert a == b

    c = Customer(id=2, email="x@y.com", product_id=1)
    assert a != c


def test_customer_acquired_date_is_none_not_empty_string() -> None:
    """The default for unknown date is None, never empty string."""
    customer = Customer(id=1, email="a@b.com", product_id=1)
    assert customer.acquired_date is None
    assert customer.acquired_date != ""

# Subscription()
def test_subscription_requires_six_fields() -> None:
    """All six required fields must be present."""
    with pytest.raises(TypeError):
        Subscription()  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        Subscription(id=1, customer_id=1, plan="monthly")  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        Subscription(  # type: ignore[call-arg]
            id=1, customer_id=1, plan="monthly",
            gross_price=Decimal("29.99"), started_date="2025-08-12",
        )  # missing platform


def test_subscription_constructs_with_required_fields_only() -> None:
    """Six required fields — the rest should default."""
    sub = Subscription(
        id=1,
        customer_id=1,
        plan="monthly",
        gross_price=Decimal("29.99"),
        started_date="2025-08-12",
        platform="stripe",
    )
    assert sub.id == 1
    assert sub.customer_id == 1
    assert sub.plan == "monthly"
    assert sub.gross_price == Decimal("29.99")
    assert sub.started_date == "2025-08-12"
    assert sub.platform == "stripe"
    assert sub.current_period_end is None
    assert sub.cancelled_date is None
    assert sub.status == "active"
    assert sub.original_price is None
    assert sub.note is None


def test_subscription_allows_overriding_optional_fields() -> None:
    """Every optional field should accept an override."""
    sub = Subscription(
        id=1,
        customer_id=1,
        plan="annual",
        gross_price=Decimal("299"),
        started_date="2025-08-12",
        platform="paddle",
        current_period_end="2026-08-12",
        cancelled_date=None,
        status="active",
        original_price=Decimal("249"),
        note="upgraded in month 6",
    )
    assert sub.plan == "annual"
    assert sub.current_period_end == "2026-08-12"
    assert sub.original_price == Decimal("249")
    assert sub.note == "upgraded in month 6"


def test_subscription_gross_price_is_decimal() -> None:
    """gross_price must be passed as Decimal, not float, at construction time."""
    sub = Subscription(
        id=1,
        customer_id=1,
        plan="monthly",
        gross_price=Decimal("29.99"),
        started_date="2025-08-12",
        platform="stripe",
    )
    assert isinstance(sub.gross_price, Decimal)
    assert sub.gross_price == Decimal("29.99")


def test_subscription_current_period_end_is_none_for_lifetime() -> None:
    """Lifetime plans have no renewal — current_period_end is None."""
    sub = Subscription(
        id=1,
        customer_id=1,
        plan="lifetime",
        gross_price=Decimal("499"),
        started_date="2025-08-12",
        platform="gumroad",
    )
    assert sub.plan == "lifetime"
    assert sub.current_period_end is None


def test_subscription_original_price_none_when_never_upgraded() -> None:
    """original_price is None means the price has never changed."""
    sub = Subscription(
        id=1,
        customer_id=1,
        plan="monthly",
        gross_price=Decimal("29.99"),
        started_date="2025-08-12",
        platform="stripe",
    )
    assert sub.original_price is None
    assert sub.gross_price == Decimal("29.99")


def test_subscription_original_price_set_after_upgrade() -> None:
    """After an upgrade, original_price remembers the starting price."""
    sub = Subscription(
        id=1,
        customer_id=1,
        plan="monthly",
        gross_price=Decimal("49.99"),      # current
        started_date="2025-08-12",
        platform="stripe",
        original_price=Decimal("29.99"),   # what they used to pay
    )
    assert sub.gross_price == Decimal("49.99")
    assert sub.original_price == Decimal("29.99")


def test_subscription_cancelled_date_none_when_active() -> None:
    """Active subscriptions have cancelled_date=None, never empty string."""
    sub = Subscription(
        id=1,
        customer_id=1,
        plan="monthly",
        gross_price=Decimal("29.99"),
        started_date="2025-08-12",
        platform="stripe",
        status="active",
    )
    assert sub.status == "active"
    assert sub.cancelled_date is None


def test_subscription_equality_via_dataclass() -> None:
    """Two subscriptions with identical fields compare equal."""
    kwargs = {
        "id": 1,
        "customer_id": 1,
        "plan": "monthly",
        "gross_price": Decimal("29.99"),
        "started_date": "2025-08-12",
        "platform": "stripe",
    }
    a = Subscription(**kwargs)
    b = Subscription(**kwargs)
    assert a == b

    c = Subscription(**{**kwargs, "gross_price": Decimal("49.99")})
    assert a != c

# Transaction()
def test_transaction_requires_seven_fields() -> None:
    """All seven required fields must be present."""
    with pytest.raises(TypeError):
        Transaction()  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        Transaction(  # type: ignore[call-arg]
            id=1, type="charge", gross=Decimal("29.99"),
            platform_fee=Decimal("0.87"),
            # missing net, date, platform
        )


def test_transaction_constructs_with_required_fields_only() -> None:
    """All seven required, everything else None."""
    txn = Transaction(
        id=1,
        type="charge",
        gross=Decimal("29.99"),
        platform_fee=Decimal("0.87"),
        net=Decimal("29.12"),
        date="2026-10-15",
        platform="stripe",
    )
    assert txn.id == 1
    assert txn.type == "charge"
    assert txn.gross == Decimal("29.99")
    assert txn.platform_fee == Decimal("0.87")
    assert txn.net == Decimal("29.12")
    assert txn.date == "2026-10-15"
    assert txn.platform == "stripe"
    assert txn.customer_id is None
    assert txn.subscription_id is None
    assert txn.note is None


def test_transaction_with_customer_and_subscription() -> None:
    """Typical subscription charge — both foreign keys populated."""
    txn = Transaction(
        id=1,
        type="charge",
        gross=Decimal("29.99"),
        platform_fee=Decimal("0.87"),
        net=Decimal("29.12"),
        date="2026-10-15",
        platform="stripe",
        customer_id=1,
        subscription_id=1,
    )
    assert txn.customer_id == 1
    assert txn.subscription_id == 1


def test_transaction_payout_has_no_customer_or_subscription() -> None:
    """A payout is a money movement without a specific customer."""
    txn = Transaction(
        id=1,
        type="payout",
        gross=Decimal("-1000"),
        platform_fee=Decimal("0"),
        net=Decimal("-1000"),
        date="2026-10-15",
        platform="direct",
    )
    assert txn.type == "payout"
    assert txn.customer_id is None
    assert txn.subscription_id is None


def test_transaction_refund_has_negative_gross() -> None:
    """Refunds are stored as negative amounts, not as deleted charges."""
    txn = Transaction(
        id=2,
        type="refund",
        gross=Decimal("-29.99"),
        platform_fee=Decimal("0.87"),
        net=Decimal("-30.86"),
        date="2026-10-16",
        platform="stripe",
        customer_id=1,
    )
    assert txn.type == "refund"
    assert txn.gross < ZERO
    assert txn.net < ZERO


def test_transaction_net_is_stored_not_computed() -> None:
    """net is a stored value, not derived from gross - platform_fee at read time."""
    txn = Transaction(
        id=1,
        type="charge",
        gross=Decimal("29.99"),
        platform_fee=Decimal("0.87"),
        net=Decimal("29.12"),
        date="2026-10-15",
        platform="stripe",
    )
    # Even if you mutate gross, net stays what was recorded
    assert txn.net == Decimal("29.12")
    assert txn.net == txn.gross - txn.platform_fee  # coincidence: matches


def test_transaction_platform_fee_is_positive() -> None:
    """Fees are stored as positive amounts, not negative."""
    txn = Transaction(
        id=1,
        type="charge",
        gross=Decimal("29.99"),
        platform_fee=Decimal("0.87"),
        net=Decimal("29.12"),
        date="2026-10-15",
        platform="stripe",
    )
    assert txn.platform_fee > ZERO


def test_transaction_all_types_constructable() -> None:
    """All four TxnType values should be constructable."""
    for txn_type in ("charge", "refund", "chargeback", "payout"):
        txn = Transaction(
            id=1,
            type=txn_type,  # type: ignore[arg-type]
            gross=Decimal("10"),
            platform_fee=Decimal("0"),
            net=Decimal("10"),
            date="2026-10-15",
            platform="direct",
        )
        assert txn.type == txn_type


def test_transaction_equality_via_dataclass() -> None:
    """Two transactions with identical fields compare equal."""
    kwargs = {
        "id": 1, "type": "charge", "gross": Decimal("29.99"),
        "platform_fee": Decimal("0.87"), "net": Decimal("29.12"),
        "date": "2026-10-15", "platform": "stripe",
    }
    a = Transaction(**kwargs)
    b = Transaction(**kwargs)
    assert a == b

    c = Transaction(**{**kwargs, "gross": Decimal("49.99")})
    assert a != c

# Expense()
def test_expense_requires_four_fields() -> None:
    """id, amount, category, date are all required."""
    with pytest.raises(TypeError):
        Expense()  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        Expense(id=1, amount=Decimal("100"))  # type: ignore[call-arg]  missing category, date


def test_expense_constructs_with_required_fields_only() -> None:
    """Four required fields — everything else defaults."""
    expense = Expense(
        id=1,
        amount=Decimal("120"),
        category="infra",
        date="2026-10-15",
    )
    assert expense.id == 1
    assert expense.amount == Decimal("120")
    assert expense.category == "infra"
    assert expense.date == "2026-10-15"
    assert expense.is_cogs is False
    assert expense.is_recurring is False
    assert expense.recur_period is None
    assert expense.vendor is None
    assert expense.note is None


def test_expense_is_cogs_defaults_to_false() -> None:
    """Most expenses aren't COGS — the default reflects that."""
    expense = Expense(
        id=1, amount=Decimal("21"), category="tools", date="2026-10-15"
    )
    assert expense.is_cogs is False


def test_expense_marked_cogs_for_usage_scaling_cost() -> None:
    """Hosting that scales with users is COGS."""
    expense = Expense(
        id=1,
        amount=Decimal("120"),
        category="infra",
        date="2026-10-15",
        is_cogs=True,
        vendor="Vercel",
    )
    assert expense.is_cogs is True
    assert expense.vendor == "Vercel"


def test_expense_not_cogs_for_flat_tools() -> None:
    """A flat monthly fee is not COGS."""
    expense = Expense(
        id=1,
        amount=Decimal("21"),
        category="tools",
        date="2026-10-15",
        is_cogs=False,
        vendor="GitHub",
    )
    assert expense.is_cogs is False


def test_expense_recurring_with_period() -> None:
    """A recurring monthly expense has recur_period set."""
    expense = Expense(
        id=1,
        amount=Decimal("120"),
        category="infra",
        date="2026-10-15",
        is_cogs=True,
        is_recurring=True,
        recur_period="monthly",
        vendor="Vercel",
    )
    assert expense.is_recurring is True
    assert expense.recur_period == "monthly"


def test_expense_recurring_yearly_period() -> None:
    """Yearly recurring expenses are valid too."""
    expense = Expense(
        id=1,
        amount=Decimal("12"),
        category="tools",
        date="2026-10-15",
        is_recurring=True,
        recur_period="yearly",
        vendor="Domain registrar",
    )
    assert expense.is_recurring is True
    assert expense.recur_period == "yearly"


def test_expense_one_time_has_no_period() -> None:
    """One-time purchases have is_recurring=False and no period."""
    expense = Expense(
        id=1,
        amount=Decimal("899"),
        category="hardware",
        date="2026-10-15",
        is_recurring=False,
        vendor="Apple",
    )
    assert expense.is_recurring is False
    assert expense.recur_period is None


def test_expense_amount_is_decimal() -> None:
    """Amount must be Decimal, not float."""
    expense = Expense(
        id=1, amount=Decimal("120"), category="infra", date="2026-10-15"
    )
    assert isinstance(expense.amount, Decimal)


def test_expense_all_categories_constructable() -> None:
    """All nine ExpenseCategory values should work."""
    valid_categories = [
        "infra",
        "tools",
        "hardware",
        "marketing",
        "education",
        "office",
        "tax",
        "other",
    ]
    for cat in valid_categories:
        expense = Expense(
            id=1,
            amount=Decimal("10"),
            category=cat,  # type: ignore[arg-type]
            date="2026-10-15",
        )
        assert expense.category == cat


def test_expense_equality_via_dataclass() -> None:
    """Two expenses with identical fields compare equal."""
    kwargs = {
        "id": 1, "amount": Decimal("120"), "category": "infra", "date": "2026-10-15",
        "is_cogs": True, "vendor": "Vercel",
    }
    a = Expense(**kwargs)
    b = Expense(**kwargs)
    assert a == b

    c = Expense(**{**kwargs, "amount": Decimal("130")})
    assert a != c

# Lead()
def test_lead_requires_four_fields() -> None:
    """id, date, source, cost are all required."""
    with pytest.raises(TypeError):
        Lead()  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        Lead(id=1, date="2026-10-15", source="twitter")  # type: ignore[call-arg]  missing cost


def test_lead_constructs_with_required_fields_only() -> None:
    """Four required fields — everything else defaults."""
    lead = Lead(
        id=1,
        date="2026-10-15",
        source="twitter",
        cost=Decimal("250"),
    )
    assert lead.id == 1
    assert lead.date == "2026-10-15"
    assert lead.source == "twitter"
    assert lead.cost == Decimal("250")
    assert lead.converted_customer_id is None
    assert lead.note is None


def test_lead_organic_with_zero_cost() -> None:
    """Organic leads cost zero but still get recorded."""
    lead = Lead(
        id=1,
        date="2026-10-15",
        source="organic",
        cost=Decimal("0"),
    )
    assert lead.source == "organic"
    assert lead.cost == ZERO
    assert isinstance(lead.cost, Decimal)


def test_lead_converted_to_customer() -> None:
    """A converted lead points to the resulting customer."""
    lead = Lead(
        id=1,
        date="2026-10-15",
        source="twitter",
        cost=Decimal("250"),
        converted_customer_id=42,
    )
    assert lead.converted_customer_id == 42


def test_lead_not_converted() -> None:
    """Most leads don't convert — converted_customer_id stays None."""
    lead = Lead(
        id=1,
        date="2026-10-15",
        source="ads",
        cost=Decimal("1400"),
    )
    assert lead.converted_customer_id is None


def test_lead_source_is_open_ended() -> None:
    """source is str, not Literal — new channels appear all the time."""
    channels = ["organic", "twitter", "ads", "producthunt", "referral", "podcast-sponsorship"]
    for channel in channels:
        lead = Lead(id=1, date="2026-10-15", source=channel, cost=Decimal("100"))
        assert lead.source == channel


def test_lead_cost_is_decimal() -> None:
    """cost must be Decimal, not float."""
    lead = Lead(
        id=1, date="2026-10-15", source="ads", cost=Decimal("250")
    )
    assert isinstance(lead.cost, Decimal)


def test_lead_equality_via_dataclass() -> None:
    """Two leads with identical fields compare equal."""
    kwargs = {
        "id": 1, "date": "2026-10-15", "source": "twitter", "cost": Decimal("250"),
    }
    a = Lead(**kwargs)
    b = Lead(**kwargs)
    assert a == b

    c = Lead(**{**kwargs, "cost": Decimal("500")})
    assert a != c

# AppState()
def test_appstate_constructs_with_all_defaults() -> None:
    """AppState() with no arguments gives a valid empty state."""
    state = AppState()
    assert state.version == "0.0.1"
    assert isinstance(state.settings, Settings)
    assert state.products == []
    assert state.customers == []
    assert state.subscriptions == []
    assert state.transactions == []
    assert state.expenses == []
    assert state.leads == []


def test_appstate_lists_are_not_shared_between_instances() -> None:
    """THE critical test — two AppState objects must have separate lists."""
    a = AppState()
    b = AppState()

    a.products.append(Product(id=1, name="X"))

    assert len(a.products) == 1
    assert len(b.products) == 0   # b is unaffected


def test_appstate_settings_are_not_shared_between_instances() -> None:
    """Two AppStates must have independent Settings objects."""
    a = AppState()
    b = AppState()

    a.settings.currency = "PKR"

    assert a.settings.currency == "PKR"
    assert b.settings.currency == "USD"   # b is unaffected


def test_appstate_holds_entities() -> None:
    """AppState can hold entities of every type."""
    state = AppState(
        products=[Product(id=1, name="X")],
        customers=[Customer(id=1, email="a@b.com", product_id=1)],
        subscriptions=[
            Subscription(
                id=1,
                customer_id=1,
                plan="monthly",
                gross_price=Decimal("29.99"),
                started_date="2025-08-12",
                platform="stripe",
            )
        ],
        transactions=[
            Transaction(
                id=1,
                type="charge",
                gross=Decimal("29.99"),
                platform_fee=Decimal("0.87"),
                net=Decimal("29.12"),
                date="2026-10-15",
                platform="stripe",
            )
        ],
        expenses=[
            Expense(
                id=1,
                amount=Decimal("120"),
                category="infra",
                date="2026-10-15",
            )
        ],
        leads=[
            Lead(
                id=1,
                date="2026-10-15",
                source="twitter",
                cost=Decimal("250"),
            )
        ],
    )
    assert len(state.products) == 1
    assert len(state.customers) == 1
    assert len(state.subscriptions) == 1
    assert len(state.transactions) == 1
    assert len(state.expenses) == 1
    assert len(state.leads) == 1


def test_appstate_version_is_overridable() -> None:
    """The version field exists for future migrations."""
    state = AppState(version="0.2.0")
    assert state.version == "0.2.0"


def test_appstate_default_version() -> None:
    """A fresh AppState starts at the current schema version."""
    state = AppState()
    assert state.version == "0.0.1"


def test_appstate_equality_via_dataclass() -> None:
    """Two empty AppStates compare equal."""
    a = AppState()
    b = AppState()
    assert a == b

    c = AppState(version="0.2.0")
    assert a != c

# next_id()
def test_next_id_empty_list_returns_1() -> None:
    """First entity gets ID 1."""
    assert next_id([]) == 1


def test_next_id_single_item() -> None:
    """With one item of id=1, next should be 2."""
    assert next_id([Product(id=1, name="X")]) == 2


def test_next_id_multiple_items_contiguous() -> None:
    """Contiguous IDs: next after 1, 2, 3 is 4."""
    items = [
        Product(id=1, name="A"),
        Product(id=2, name="B"),
        Product(id=3, name="C"),
    ]
    assert next_id(items) == 4


def test_next_id_with_gaps_uses_max_not_count() -> None:
    """If ids are 1, 3, 5, next should be 6 (max + 1), NOT 4 (len + 1)."""
    items = [
        Product(id=1, name="A"),
        Product(id=3, name="B"),
        Product(id=5, name="C"),
    ]
    assert next_id(items) == 6


def test_next_id_after_deletion_uses_max_not_count() -> None:
    """After deleting id=2 from [1, 2, 3], remaining is [1, 3], next should be 4."""
    items = [
        Product(id=1, name="A"),
        Product(id=3, name="C"),
    ]
    # len(items) + 1 would be 3 (collision!). max + 1 is correct.
    assert next_id(items) == 4


def test_next_id_works_for_customers() -> None:
    """next_id works with any entity type, not just Product."""
    items = [
        Customer(id=1, email="a@b.com", product_id=1),
        Customer(id=2, email="c@d.com", product_id=1),
    ]
    assert next_id(items) == 3


def test_next_id_works_for_transactions() -> None:
    """next_id works with Transaction."""
    items = [
        Transaction(
            id=10,
            type="charge",
            gross=Decimal("29.99"),
            platform_fee=Decimal("0.87"),
            net=Decimal("29.12"),
            date="2026-10-15",
            platform="stripe",
        )
    ]
    assert next_id(items) == 11


def test_next_id_with_large_ids() -> None:
    """Large ids work fine."""
    items = [Product(id=999999, name="X")]
    assert next_id(items) == 1000000
