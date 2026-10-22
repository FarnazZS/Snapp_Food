class Restaurant:
    def __init__(self, name, manager_username):
        self.name = name
        self.manager_username = manager_username
        self.menu = []
        self.orders = []

    def display_menu(self):
        print(f"\n=== {self.name} Menu ===")
        if not self.menu:
            print("Menu is empty.")
            return
        for i, item in enumerate(self.menu, 1):
            print(f"  {i}.", end=" ")
            item.display()

    def display_orders(self):
        print(f"\n=== {self.name} Orders ===")
        if not self.orders:
            print("No orders yet.")
            return
        for order in self.orders:
            order.display()

    def add_order(self, order):
        self.orders.append(order)

    def find_item(self, item_name):
        for item in self.menu:
            if item.name.lower() == item_name.lower():
                return item
        return None

    def to_dict(self):
        return {
            "name": self.name,
            "manager_username": self.manager_username,
            "menu": [item.to_dict() for item in self.menu],
            "orders": [order.to_dict() for order in self.orders]
        }