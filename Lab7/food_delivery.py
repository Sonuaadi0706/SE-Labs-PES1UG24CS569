def parse_order(items_csv):
    order = {}
    for item in items_csv.split(','):
        name, qty = item.split(':')
        order[name.strip()] = int(qty)
    return order

def delivery_eta(distance_km):
    return int(15 + float(distance_km) * 4)

def coupon_discount(code):
    return int(code.upper().split('SAVE')[1])

def main():
    print("==== Running parse_order ====")
    user_input = input("Enter items as name:qty CSV (e.g. pizza:2,burger:1): ")
    result = parse_order(user_input)
    print("Order:", result)

    print("\n==== Running delivery_eta ====")
    user_input = input("Enter distance in km (e.g. 4.5): ")
    result = delivery_eta(user_input)
    print("ETA in Minutes:", result)

    print("\n==== Running coupon_discount ====")
    user_input = input("Enter a coupon code (e.g. SAVE50): ")
    result = coupon_discount(user_input)
    print("Discount:", result)

if __name__ == "__main__":
    main()
