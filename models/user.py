class User:
    def __init__(self, first_name, last_name, username, password, role):
        self.user_id = self._generate_id(role)
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.role = role

    def _generate_id(self, role):
        import uuid
        prefix = "m" if role == "manager" else "c"
        return f"{prefix}{uuid.uuid4().hex[:8]}"

    @staticmethod
    def validate_name(name):
        return name.isalpha() and len(name) >= 2

    @staticmethod
    def validate_username(username):
        return username.isalnum() and len(username) >= 4

    @staticmethod
    def validate_password(password):
        return len(password) >= 6

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "password": self.password,
            "role": self.role
        }
    
class Manager(User):
    def __init__(self, first_name, last_name, username, password):
        super().__init__(first_name, last_name, username, password, role="manager")
        self.restaurant = None

    def add_item(self, item):
        self.restaurant.menu.append(item)
        print(f"  '{item.name}' added to menu.")

    def edit_item(self, item_name, new_name=None, new_price=None, new_availability=None, new_type=None):
        item = self.restaurant.find_item(item_name)
        if item:
            if new_name:
                item.name = new_name
            if new_price is not None:
                item.price = new_price
            if new_availability is not None:
                item.is_available = new_availability
            if new_type:
                item.item_type = new_type
            print(f"  '{item_name}' updated.")
            return True
        print(f"  Item '{item_name}' not found.")
        return False

    def remove_item(self, item_name):
        item = self.restaurant.find_item(item_name)
        if item:
            self.restaurant.menu.remove(item)
            print(f"  '{item_name}' removed from menu.")
        else:
            print(f"  Item '{item_name}' not found.")

    def to_dict(self):
        data = super().to_dict()
        data["restaurant"] = self.restaurant.name if self.restaurant else None
        return data
    
class Customer(User):
    def __init__(self, first_name, last_name, username, password):
        super().__init__(first_name, last_name, username, password, role="customer")
        self.cart = []
        self.order_history = []

    def add_to_cart(self, item):
        if item.is_available:
            self.cart.append(item)
            print(f" '{item.name}' added to cart.")
        else:
            print(f" '{item.name}' is not available.")

    def remove_from_cart(self, item_name):
        for item in self.cart:
            if item.name.lower() == item_name.lower():
                self.cart.remove(item)
                print(f" '{item_name}' removed from cart.")
                return
        print(f" '{item_name}' not found in cart.")

    def checkout(self, restaurant):
        from models.order import Order
        if not self.cart:
            print("Your cart is empty.")
            return None
        order_id = f"ORD{len(self.order_history) + 1}"
        order = Order(order_id, self.username, restaurant.name)
        for item in self.cart:
            order.add_item(item)
        self.order_history.append(order)
        restaurant.add_order(order)
        self.cart = []
        print(f"\n Order placed! Total: ${order.get_total()}")
        order.display()
        return order

    def view_order_history(self):
        if not self.order_history:
            print("No previous orders.")
            return
        for order in self.order_history:
            order.display()

    def to_dict(self):
        data = super().to_dict()
        data["order_history"] = [o.to_dict() for o in self.order_history]
        return data