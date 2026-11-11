"""Food delivery helpers - hardened against the inputs found by fuzz testing.

None of the three functions raises on bad input. Each returns a clear
"invalid" value instead, so callers can tell good input from bad:

    parse_order      -> {}    (empty order)
    delivery_eta     -> None  (no estimate)
    coupon_discount  -> 0     (no discount)
"""

import math
import re

MAX_QTY = 99            # most of one item allowed in a single order
MAX_DISTANCE_KM = 50    # delivery radius
MAX_DISCOUNT = 100      # largest discount a SAVE coupon can give
BASE_ETA_MIN = 15       # preparation time
MIN_PER_KM = 4          # travel time per km

_QTY_RE = re.compile(r"[0-9]{1,2}")
_DISTANCE_RE = re.compile(r"[0-9]{1,3}(\.[0-9]{1,6})?|\.[0-9]{1,6}")
_COUPON_RE = re.compile(r"SAVE([0-9]{1,3})")


def parse_order(items_csv):
    """Parse "name:qty,name:qty" into {name: qty}.

    Empty segments (e.g. a trailing comma) are ignored and repeated items are
    added together. Returns {} if the input is not a string, or if any item is
    malformed: no single ':', blank or non-printable name, or a quantity that
    is not a whole number from 1 to MAX_QTY.
    """
    if not isinstance(items_csv, str):
        return {}

    order = {}
    for item in items_csv.split(","):
        if not item.strip():
            continue
        parts = item.split(":")
        if len(parts) != 2:
            return {}
        name, qty_text = parts[0].strip(), parts[1].strip()
        if not name or not name.isprintable():
            return {}
        # fullmatch on ASCII digits rejects '-3', '+3', '1_0', ' ', 'two',
        # Unicode digits and huge numbers before int() ever sees them.
        if not _QTY_RE.fullmatch(qty_text):
            return {}
        qty = order.get(name, 0) + int(qty_text)
        if not 1 <= qty <= MAX_QTY:
            return {}
        order[name] = qty
    return order


def delivery_eta(distance_km):
    """Return the delivery time in whole minutes, rounded up.

    Accepts a number or a plain decimal string such as "4.5". Returns None
    for anything else, including None, booleans, NaN/infinity, "4.5 km",
    "1e3", and distances outside (0, MAX_DISTANCE_KM].
    """
    if isinstance(distance_km, bool):
        return None
    if isinstance(distance_km, str):
        text = distance_km.strip()
        if not _DISTANCE_RE.fullmatch(text):
            return None
        distance = float(text)
    elif isinstance(distance_km, (int, float)):
        distance = float(distance_km)
    else:
        return None

    if not math.isfinite(distance) or not 0 < distance <= MAX_DISTANCE_KM:
        return None
    return math.ceil(BASE_ETA_MIN + distance * MIN_PER_KM)


def coupon_discount(code):
    """Return the discount N for a "SAVEN" coupon code (any letter case).

    Surrounding spaces are ignored. Returns 0 for anything that is not exactly
    SAVE followed by a whole number from 1 to MAX_DISCOUNT - for example
    None, "FREEDEL", "SAVE", "SAVE-50", "XSAVE50" or "SAVE99999".
    """
    if not isinstance(code, str) or not code.isascii():
        return 0
    match = _COUPON_RE.fullmatch(code.strip().upper())
    if not match:
        return 0
    amount = int(match.group(1))
    return amount if 1 <= amount <= MAX_DISCOUNT else 0


def main():
    print("==== Running parse_order ====")
    user_input = input("Enter items as name:qty CSV (e.g. pizza:2,burger:1): ")
    result = parse_order(user_input)
    if result:
        print("Order:", result)
    else:
        print(f"Invalid order. Use name:qty pairs with quantities 1-{MAX_QTY}.")

    print("\n==== Running delivery_eta ====")
    user_input = input("Enter distance in km (e.g. 4.5): ")
    result = delivery_eta(user_input)
    if result is not None:
        print("ETA in Minutes:", result)
    else:
        print(f"Invalid distance. Enter a number above 0 and up to {MAX_DISTANCE_KM}.")

    print("\n==== Running coupon_discount ====")
    user_input = input("Enter a coupon code (e.g. SAVE50): ")
    result = coupon_discount(user_input)
    if result:
        print("Discount:", result)
    else:
        print("Invalid coupon code. No discount applied.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
