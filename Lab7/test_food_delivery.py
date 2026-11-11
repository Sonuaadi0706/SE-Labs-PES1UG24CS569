from hypothesis import given, strategies as st
from food_delivery import parse_order, delivery_eta, coupon_discount

@given(st.text() | st.none())
def test_parse_order_no_crash(s):

@given(st.text() | st.none())
def test_delivery_eta_no_crash(s):

@given(st.text() | st.none())
def test_coupon_discount_no_crash(s):
