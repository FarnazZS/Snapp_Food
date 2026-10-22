from models.user import User, Manager, Customer
from models.restaurant import Restaurant

class Platform:
    def __init__(self):
        self.users = []
        self.restaurants = []
        self.current_user = None

    def find_user(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None

    def find_restaurant(self, restaurant_name):
        for restaurant in self.restaurants:
            if restaurant.name.lower() == restaurant_name.lower():
                return restaurant
        return None

    def sign_up(self, first_name, last_name, username, password, role, restaurant_name=None):
        if not User.validate_name(first_name):
            print("Invalid first name.")
            return False
        if not User.validate_name(last_name):
            print("Invalid last name.")
            return False
        if not User.validate_username(username):
            print("Invalid username. At least 4 characters, letters and numbers only.")
            return False
        if not User.validate_password(password):
            print("Invalid password. At least 6 characters.")
            return False
        if self.find_user(username):
            print("Username already exists.")
            return False

        if role == "manager":
            if not restaurant_name:
                print("Restaurant name is required for managers.")
                return False
            if self.find_restaurant(restaurant_name):
                print("A restaurant with this name already exists.")
                return False
            user = Manager(first_name, last_name, username, password)
            restaurant = Restaurant(restaurant_name, username)
            user.restaurant = restaurant
            self.restaurants.append(restaurant)
        else:
            user = Customer(first_name, last_name, username, password)

        self.users.append(user)
        print(f"Account created! Welcome, {first_name}.")
        return True

    def sign_in(self, username, password):
        user = self.find_user(username)
        if user and user.password == password:
            self.current_user = user
            print(f"Welcome back, {user.first_name}!")
            return True
        print("Invalid username or password.")
        return False

    def sign_out(self): 
        self.current_user = None
        print("Signed out successfully.")