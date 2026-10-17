"""Money primitives for MizanZarb.

Money is Decimal internally. Float is forbidden. Strings are the only
safe boundary for parsing. Formatting produces display strings only.
"""
from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
from typing import Final

from .errors import InvalidAmountError, InvalidPercentError

CENT: Final[Decimal] = Decimal("0.01")
ZERO: Final[Decimal] = Decimal("0") # pyright: ignore[reportInvalidTypeForm]
ONE: Final[Decimal] = Decimal("1")

CURRENCY_SYMBOLS: Final[dict[str:str]] = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "PKR": "₨",
    "INR": "₹",
    "AED": "د.إ",
    "SAR": "﷼",
}

def to_decimal(value: int | str | Decimal) -> Decimal:
    """Convert a safe input to Decimal."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        raise InvalidAmountError(f"Boolean is not a valid amount: {value!r}")
    if isinstance(value, float):
        raise InvalidAmountError(
            "Float is not accepted for money. Use a string like '29.99'."
        )
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "").replace(" ", "")
        if not cleaned:
            raise InvalidAmountError("Empty string is not a valid amount.")
        try:
            return Decimal(cleaned)
        except InvalidOperation as exc:
            raise InvalidAmountError(f"Invalid amount: {value!r}") from exc
    raise InvalidAmountError(f"Unsupported type for amount: {type(value).__name__}")

def round_money(value: Decimal) -> Decimal:
    """Round to 2 decimal places using banker's rounding."""
    return value.quantize(CENT, rounding=ROUND_HALF_EVEN)

def is_positive(value: Decimal) -> bool:
    """True if value is strictly greater than zero."""
    return value > ZERO

def is_non_negative(value: Decimal) -> bool:
    """True if value is zero or greater."""
    return value >= ZERO

def require_positive(value: Decimal, *, field: str = "amount") -> Decimal:
    """Returns value if positive, otherwise raise InvalidAmountError."""
    if not is_positive(value):
        raise InvalidAmountError(f"{field} must be grater than zero, got {value}")
    return value

def require_non_negative(value: Decimal, *, field: str = "amount") -> Decimal:
    """Return value if non-negative, otherwise raise InvalidAmountError."""
    if not is_non_negative(value):
        raise InvalidAmountError(f"{field} cannot be negative, got {value}")
    return value

def require_percent(value: Decimal, *, field: str = "percent") -> Decimal:
    """Validate a value is in [0, 1]. Returns it unchanged."""
    if value < ZERO or value > ONE:
        raise InvalidPercentError(f"{field} must be in [0, 1], got {value}")
    return value

# Safe Math
def safe_div(numerator: Decimal, denominator: Decimal) -> Decimal | None:
    """Divide, returning None when denominator is zero."""
    if denominator is ZERO:
        return None
    return numerator / denominator

def safe_percent(part: Decimal, whole: Decimal) -> Decimal | None:
    """Return part / whole as a Decimal or None if whole is zero."""
    return safe_div(part, whole)

def pct(value: Decimal) -> Decimal:
    """Convert a ratio (0.842) to a percentage value (84.2)."""
    return value * Decimal("100")

def format_money(
        amount: Decimal,
        *,
        currency: str = "USD",
        show_symbol: bool = True,
        show_sign: bool = False
    ) -> str:
    """Format a Decimal as a display string."""
    rounded = round_money(amount)
    symbol = CURRENCY_SYMBOLS.get(currency, currency) if show_symbol else ""
    sign = ""
    if show_sign and rounded > ZERO:
        sign = "+"
    body = f"{abs(rounded):,.2f}"
    if rounded < ZERO:
        body = f"-{body}"
    if symbol:
        return f"{sign}{symbol} {body}"
    return f"{sign}{body}"

def format_percent(
    ratio: Decimal | None,
    *,
    decimals: int = 1,
    fallback: str = "—",
) -> str:
    """Format a ratio as a percentage string. None becomes fallback."""
    if ratio is None:
        return fallback
    value = pct(ratio)
    return f"{value:.{decimals}f}%"

