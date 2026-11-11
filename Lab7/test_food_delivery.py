"""Hypothesis fuzz tests for food_delivery.py (Lab 7 - Fuzz Testing).

Two kinds of tests are used for each of the three functions:

* "no crash" tests feed random text, None and other junk and require that the
  function never raises - invalid input must be rejected gracefully;
* property tests check that valid input still gives the correct answer and
  that every result stays inside a sensible range.

The expected behaviour (the contract the fixed module must meet):

* parse_order(items_csv)   -> dict of {item name: quantity}; quantities are
                              whole numbers from 1 to 99; {} if the input is invalid
* delivery_eta(distance_km) -> whole minutes, rounded up (15 + 4 per km) for a
                              distance in (0, 50] km; None if the input is invalid
* coupon_discount(code)    -> the N in a "SAVEN" code (1 to 100, any letter case);
                              0 if the code is invalid
"""

import math
import string

from hypothesis import example, given, settings, strategies as st

from food_delivery import coupon_discount, delivery_eta, parse_order

MAX_QTY = 99
MAX_DISTANCE_KM = 50
MAX_DISCOUNT = 100

FUZZ = settings(max_examples=500, deadline=None)

# Any value a caller might pass in, not just strings.
junk = (
    st.text()
    | st.none()
    | st.integers()
    | st.floats(allow_nan=True, allow_infinity=True)
    | st.booleans()
    | st.lists(st.text(), max_size=3)
)

# Text built mostly from the characters the parsers care about, so the fuzzer
# reaches the deeper branches instead of failing on the first character.
order_like = st.text(alphabet="pizaburge :,-+_.0123456789 ", max_size=40)
distance_like = st.text(alphabet="0123456789.-+eEinfa_ km", max_size=20)
coupon_like = st.builds(
    lambda prefix, body: prefix + body,
    st.sampled_from(["", "SAVE", "save", "Save", "xSAVE", "SAVESAVE"]),
    st.text(alphabet="0123456789-+_.SAVE ", max_size=12),
)


# --------------------------------------------------------------------------
# parse_order
# --------------------------------------------------------------------------

@FUZZ
@given(st.text() | st.none())
def test_parse_order_no_crash(s):
    try:
        parse_order(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"parse_order crashed with: {e!r}"


@FUZZ
@given(junk | order_like)
@example("pizza:two")            # non-numeric quantity
@example("pizza:2,,burger:1")    # empty item in the middle
@example("pizza:-3")             # negative quantity
@example("pizza:" + "9" * 5000)  # hits int()'s 4300-digit limit
def test_parse_order_returns_valid_order(s):
    try:
        order = parse_order(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"parse_order crashed with: {e!r}"
    assert isinstance(order, dict)
    for name, qty in order.items():
        assert isinstance(name, str) and name and name == name.strip()
        assert type(qty) is int and 1 <= qty <= MAX_QTY, f"bad quantity {qty!r}"


item_names = st.text(alphabet=string.ascii_letters + " ", min_size=1, max_size=15).filter(
    lambda n: n.strip()
)


@FUZZ
@given(st.dictionaries(item_names.map(str.strip), st.integers(1, MAX_QTY), min_size=1, max_size=6))
def test_parse_order_round_trip(expected):
    csv = ",".join(f"{name}:{qty}" for name, qty in expected.items())
    assert parse_order(csv) == expected


@FUZZ
@given(item_names.map(str.strip), st.integers(1, 40), st.integers(1, 40))
def test_parse_order_merges_duplicate_items(name, q1, q2):
    assert parse_order(f"{name}:{q1},{name}:{q2}") == {name: q1 + q2}


# --------------------------------------------------------------------------
# delivery_eta
# --------------------------------------------------------------------------

@FUZZ
@given(st.text() | st.none())
def test_delivery_eta_no_crash(s):
    try:
        delivery_eta(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"delivery_eta crashed with: {e!r}"


@FUZZ
@given(junk | distance_like)
@example("4.5 km")  # unit typed after the number
@example("nan")
@example("inf")
@example("-5")
@example(1e308)
def test_delivery_eta_result_in_range(d):
    try:
        eta = delivery_eta(d)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"delivery_eta crashed with: {e!r}"
    assert eta is None or (
        type(eta) is int and 15 <= eta <= 15 + 4 * MAX_DISTANCE_KM
    ), f"impossible ETA {eta!r} for input {d!r}"


distances = st.floats(min_value=0.01, max_value=MAX_DISTANCE_KM, allow_nan=False)


@FUZZ
@given(distances)
def test_delivery_eta_correct_for_valid_distance(d):
    expected = math.ceil(15 + d * 4)
    assert delivery_eta(d) == expected
    assert delivery_eta(f"{d:.2f}") == math.ceil(15 + float(f"{d:.2f}") * 4)


@FUZZ
@given(distances, distances)
def test_delivery_eta_never_shorter_for_longer_trip(a, b):
    near, far = sorted((a, b))
    assert delivery_eta(near) <= delivery_eta(far)


# --------------------------------------------------------------------------
# coupon_discount
# --------------------------------------------------------------------------

@FUZZ
@given(st.text() | st.none())
def test_coupon_discount_no_crash(s):
    try:
        coupon_discount(s)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"coupon_discount crashed with: {e!r}"


@FUZZ
@given(junk | coupon_like)
@example("FREEDEL")    # no 'SAVE' in the code
@example("SAVE-50")    # negative discount
@example("SAVE99999")  # absurdly large discount
@example("XSAVE50")    # junk before the code
def test_coupon_discount_result_in_range(code):
    try:
        discount = coupon_discount(code)
    except Exception as e:  # pylint: disable=broad-except
        assert False, f"coupon_discount crashed with: {e!r}"
    assert type(discount) is int and 0 <= discount <= MAX_DISCOUNT, (
        f"discount {discount!r} for code {code!r}"
    )


@FUZZ
@given(st.integers(1, MAX_DISCOUNT), st.sampled_from([str.upper, str.lower, str.title]))
def test_coupon_discount_valid_codes(n, case):
    assert coupon_discount(case(f"SAVE{n}")) == n
    assert coupon_discount(f"  SAVE{n}  ") == n
