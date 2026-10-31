import pytest
from food_delivery import delivery_charge, apply_coupon, estimated_time

#Example test cases:
def test_nearby_small_order():
    assert delivery_charge(2, 200, False) == 20

def test_no_coupon():
    assert apply_coupon(300, None, False) == 300

#Write the rest of the test cases so that the code is 90- 100% covered.
