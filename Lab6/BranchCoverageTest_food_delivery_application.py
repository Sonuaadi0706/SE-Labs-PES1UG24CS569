"""Branch coverage tests for food_delivery.py.

Goal: take BOTH outcomes (True and False) of every decision in the application
(target >= 90 %), and test the boundary value on each side of every comparison,
because that is where wrong operators (< vs <=) hide.

Decisions in food_delivery.py
    delivery_charge : distance <= 0 | distance > 15 | order_value >= 500 |
                      distance <= 3 | distance <= 8 | is_raining
    apply_coupon    : code is None | code not in COUPONS |
                      WELCOME and not first order | order_value < 200
    estimated_time  : is_peak_hour | restaurant_busy | is_peak_hour (if busy)

Run:
    coverage run --branch -m pytest BranchCoverageTest_food_delivery_application.py
    coverage report -m
"""
import pytest

from food_delivery import apply_coupon, delivery_charge, estimated_time


# ====================================================================== delivery_charge
class TestDeliveryRange:
    """`if distance_km <= 0 or distance_km > 15` - both operands, both outcomes."""

    @pytest.mark.parametrize("distance", [0, -1, -0.5])
    def test_zero_or_negative_distance_rejected(self, distance):
        with pytest.raises(ValueError, match="out of delivery range"):
            delivery_charge(distance, 200, False)

    @pytest.mark.parametrize("distance", [15.01, 16, 100])
    def test_distance_over_limit_rejected(self, distance):
        with pytest.raises(ValueError, match="out of delivery range"):
            delivery_charge(distance, 200, False)

    @pytest.mark.parametrize("distance, expected", [(0.1, 20), (15, 60)])
    def test_range_boundaries_are_accepted(self, distance, expected):
        assert delivery_charge(distance, 200, False) == expected

    def test_range_is_checked_before_free_delivery_and_rain(self):
        with pytest.raises(ValueError):
            delivery_charge(0, 1000, True)
        with pytest.raises(ValueError):
            delivery_charge(20, 1000, True)


class TestDeliveryFeeTiers:
    """`order_value >= 500` and the distance tiers `<= 3`, `<= 8`, else."""

    @pytest.mark.parametrize("order_value", [500, 501, 1000])
    def test_free_delivery_at_or_above_500(self, order_value):
        assert delivery_charge(2, order_value, False) == 0

    def test_free_delivery_applies_to_the_longest_distance_too(self):
        assert delivery_charge(15, 500, False) == 0

    @pytest.mark.parametrize("order_value", [499.99, 499, 0])
    def test_no_free_delivery_below_500(self, order_value):
        assert delivery_charge(2, order_value, False) == 20

    @pytest.mark.parametrize(
        "distance, expected",
        [
            (1, 20),      # first tier
            (3, 20),      # upper boundary of the first tier (<= 3)
            (3.01, 40),   # just past it
            (5, 40),      # second tier
            (8, 40),      # upper boundary of the second tier (<= 8)
            (8.01, 60),   # just past it
            (15, 60),     # third tier, furthest deliverable distance
        ],
    )
    def test_distance_tiers(self, distance, expected):
        assert delivery_charge(distance, 200, False) == expected


class TestDeliveryRainSurcharge:
    """`if is_raining` - True and False for every tier."""

    @pytest.mark.parametrize(
        "distance, dry, wet",
        [(2, 20, 50), (5, 40, 70), (10, 60, 90)],
    )
    def test_rain_adds_30_to_every_tier(self, distance, dry, wet):
        assert delivery_charge(distance, 200, False) == dry
        assert delivery_charge(distance, 200, True) == wet

    def test_rain_surcharge_applies_even_when_delivery_is_free(self):
        assert delivery_charge(2, 600, True) == 30


# ====================================================================== apply_coupon
class TestNoCoupon:
    """`if code is None` - True branch."""

    @pytest.mark.parametrize("is_first_order", [True, False])
    @pytest.mark.parametrize("order_value", [0, 50, 300])
    def test_order_value_unchanged_without_coupon(self, order_value, is_first_order):
        assert apply_coupon(order_value, None, is_first_order) == order_value


class TestInvalidCoupon:
    """`if code not in COUPONS` - True branch (and False for valid codes below)."""

    @pytest.mark.parametrize("code", ["BOGUS", "", "save50", "Welcome", "SAVE 50"])
    def test_unknown_or_miscased_code_rejected(self, code):
        with pytest.raises(ValueError, match="invalid coupon"):
            apply_coupon(300, code, True)

    def test_validity_is_checked_before_first_order_rule(self):
        with pytest.raises(ValueError, match="invalid coupon"):
            apply_coupon(300, "BOGUS", False)


class TestWelcomeCoupon:
    """`if code == "WELCOME" and not is_first_order` - each operand decides once."""

    @pytest.mark.parametrize("order_value", [50, 300])
    def test_rejected_for_repeat_customer_regardless_of_order_value(self, order_value):
        with pytest.raises(ValueError, match="coupon only for first order"):
            apply_coupon(order_value, "WELCOME", False)

    def test_accepted_for_first_order(self):
        assert apply_coupon(300, "WELCOME", True) == 200

    def test_minimum_order_boundary_exactly_200(self):
        assert apply_coupon(200, "WELCOME", True) == 100


class TestSave50Coupon:
    """SAVE50 is not first-order-only, so the `code == "WELCOME"` operand is False."""

    @pytest.mark.parametrize("is_first_order", [True, False])
    def test_accepted_for_any_customer(self, is_first_order):
        assert apply_coupon(300, "SAVE50", is_first_order) == 250

    def test_minimum_order_boundary_exactly_200(self):
        assert apply_coupon(200, "SAVE50", False) == 150


class TestCouponMinimumOrder:
    """`if order_value < 200` - True branch (no discount) and False branch (discount)."""

    @pytest.mark.parametrize("code, is_first_order", [("SAVE50", False), ("WELCOME", True)])
    @pytest.mark.parametrize("order_value", [0, 150, 199, 199.99])
    def test_no_discount_below_200(self, order_value, code, is_first_order):
        assert apply_coupon(order_value, code, is_first_order) == order_value

    def test_discount_just_above_threshold(self):
        assert apply_coupon(200.01, "SAVE50", False) == pytest.approx(150.01)


# ====================================================================== estimated_time
class TestEstimatedTime:
    """Base is 15 + 4 min/km; peak adds 10, busy adds 15, busy *and* peak adds 5 more.

    Covers `if is_peak_hour` (T/F), `if restaurant_busy` (T/F) and the nested
    `if is_peak_hour` (T/F) - all four peak x busy combinations.
    """

    @pytest.mark.parametrize(
        "is_peak_hour, restaurant_busy, expected",
        [
            (False, False, 35),                # 15 + 5*4
            (True, False, 35 + 10),            # peak only
            (False, True, 35 + 15),            # busy only: nested peak check is False
            (True, True, 35 + 10 + 15 + 5),    # busy and peak
        ],
    )
    def test_peak_and_busy_combinations(self, is_peak_hour, restaurant_busy, expected):
        assert estimated_time(5, is_peak_hour, restaurant_busy) == expected

    @pytest.mark.parametrize(
        "distance, expected",
        [(0, 15), (2.5, 25), (15, 75)],
    )
    def test_distance_scales_the_base_time(self, distance, expected):
        assert estimated_time(distance, False, False) == expected

    def test_longest_delivery_in_the_worst_conditions(self):
        assert estimated_time(15, True, True) == 75 + 30
