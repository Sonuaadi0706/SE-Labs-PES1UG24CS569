COUPONS = {"SAVE50": 50, "WELCOME": 100}


def delivery_charge(distance_km, order_value, is_raining):
    if distance_km <= 0 or distance_km > 15:
        raise ValueError("out of delivery range")
    if order_value >= 500:
        charge = 0
    elif distance_km <= 3:
        charge = 20
    elif distance_km <= 8:
        charge = 40
    else:
        charge = 60
    if is_raining:
        charge += 30
    return charge


def apply_coupon(order_value, code, is_first_order):
    if code is None:
        return order_value
    if code not in COUPONS:
        raise ValueError("invalid coupon")
    if code == "WELCOME" and not is_first_order:
        raise ValueError("coupon only for first order")
    if order_value < 200:
        return order_value
    return order_value - COUPONS[code]


def estimated_time(distance_km, is_peak_hour, restaurant_busy):
    minutes = 15 + distance_km * 4
    if is_peak_hour:
        minutes += 10
    if restaurant_busy:
        minutes += 15
        if is_peak_hour:
            minutes += 5
    return minutes
