from datetime import datetime

class Order:
    def __init__(self, order_id, customer, restaurant):
        self.order_id = order_id
        self.customer = customer
        self.restaurant = restaurant
        self.items = []
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M")

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item_name):
        for item in self.items:
            if item.name == item_name:
                self.items.remove(item)
                return True
        return False

    def get_total(self):
        return sum(item.price for item in self.items)

    def display(self):
        print(f"\n  Order ID : {self.order_id}")
        print(f"  Time   : {self.time}")
        print(f"  Items  :")
        for item in self.items:
            print(f" - {item.name} | ${item.price}")
        print(f"Total : ${self.get_total()}")

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer": self.customer,
            "restaurant": self.restaurant,
            "items": [item.to_dict() for item in self.items],
            "time": self.time
        }