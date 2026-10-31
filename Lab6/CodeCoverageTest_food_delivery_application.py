"""Code (line) coverage tests for food_delivery.py.

Goal: execute every statement of the application at least once (target >= 90 %).
Each test notes which lines of food_delivery.py it exercises.

Run:
    coverage run -m pytest CodeCoverageTest_food_delivery_application.py
    coverage report -m
"""
import pytest

from food_delivery import apply_coupon, delivery_charge, estimated_time


# ---------------------------------------------------------------- delivery_charge
def test_nearby_small_order():  # starter test - line 10 (<= 3 km tier)
    assert delivery_charge(2, 200, False) == 20


def test_distance_out_of_range_is_rejected():  # lines 5-6
    with pytest.raises(ValueError, match="out of delivery range"):
        delivery_charge(0, 200, False)


def test_free_delivery_for_large_order():  # line 8
    assert delivery_charge(2, 600, False) == 0


def test_mid_distance_with_rain_surcharge():  # lines 12 and 16 (3-8 km tier + rain)
    assert delivery_charge(5, 200, True) == 40 + 30


def test_far_distance_tier():  # line 14 (> 8 km tier)
    assert delivery_charge(10, 200, False) == 60


# ---------------------------------------------------------------- apply_coupon
def test_no_coupon():  # starter test - lines 21-22
    assert apply_coupon(300, None, False) == 300


def test_unknown_coupon_is_rejected():  # lines 23-24
    with pytest.raises(ValueError, match="invalid coupon"):
        apply_coupon(300, "BOGUS", False)


def test_welcome_coupon_rejected_for_repeat_customer():  # lines 25-26
    with pytest.raises(ValueError, match="coupon only for first order"):
        apply_coupon(300, "WELCOME", False)


def test_welcome_coupon_on_first_order():  # line 29
    assert apply_coupon(300, "WELCOME", True) == 300 - 100


def test_coupon_ignored_below_minimum_order():  # lines 27-28
    assert apply_coupon(150, "SAVE50", False) == 150


# ---------------------------------------------------------------- estimated_time
def test_estimated_time_peak_hour_and_busy_restaurant():  # lines 33-39
    # 15 + 5 km * 4 = 35, +10 peak, +15 busy, +5 busy-and-peak
    assert estimated_time(5, True, True) == 65
