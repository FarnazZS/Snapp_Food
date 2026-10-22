import os
import customtkinter as ctk
from PIL import Image
from app_platform import Platform
from data_manager import save_data, load_data, initialize_db, get_next_order_number

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

PINK = "#D12B5A"
WHITE = "#FFFFFF"
GRAY = "#1E1E1E"
DARK = "#2B2B2B"

IMAGES = [
    "burger", "cake", "chick_bucket", "choco_bar", "choco_truff",
    "cocktail", "coffee", "cookie", "cupcake", "donut",
    "fries", "icecream", "juice", "milkchoco", "pizza",
    "single_chick", "soda", "sushi", "taco"
]


def load_image(name, size=(60, 60)):
    path = os.path.join("assets", f"{name}.png")
    if os.path.exists(path):
        return ctk.CTkImage(Image.open(path), size=size)
    return None


class SnappFoodApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Snapp Food")
        self.geometry("1200x700")
        self.resizable(True, True)
        self.platform = Platform()
        initialize_db()
        load_data(self.platform)
        self._image_refs = []
        self.wm_state("zoomed")
        self.after(100, self.show_login_page)

    def clear(self):
        self._image_refs = []
        for widget in self.winfo_children():
            widget.destroy()

    
    def show_login_page(self):
        self.clear()

        self.update_idletasks()
        win_w = self.winfo_screenwidth()
        win_h = self.winfo_screenheight()
        img_w = int(win_w * 0.38)

        left = ctk.CTkFrame(self, fg_color=PINK, width=img_w)
        left.pack_propagate(False)
        left.pack(side="left", fill="y")

        bg_img = ctk.CTkImage(Image.open("assets/login_bg.png"), size=(img_w, win_h))
        self._image_refs.append(bg_img)
        bg_label = ctk.CTkLabel(left, image=bg_img, text="")
        bg_label.place(x=0, y=1, relwidth=1, relheight=1)

        right = ctk.CTkFrame(self, fg_color=GRAY)
        right.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right, text="Welcome Back!",
                     font=("Arial Black", 32, "bold"),
                     text_color=WHITE).pack(pady=(80, 5))
        ctk.CTkLabel(right, text="Sign in to continue",
                     font=("Arial", 14), text_color="#AAAAAA").pack(pady=(0, 25))

        tab_frame = ctk.CTkFrame(right, fg_color="transparent")
        tab_frame.pack(pady=(0, 20))

        self.login_role = ctk.StringVar(value="customer")

        self.tab_customer = ctk.CTkButton(tab_frame, text="🏠  Customer",
                                          width=160, height=40, corner_radius=8,
                                          fg_color=PINK, hover_color="#C0006E",
                                          text_color=WHITE,
                                          command=lambda: self.switch_login_tab("customer"))
        self.tab_customer.pack(side="left", padx=5)

        self.tab_manager = ctk.CTkButton(tab_frame, text="🍴  Restaurant Owner",
                                         width=160, height=40, corner_radius=8,
                                         fg_color="#444444", hover_color="#C0006E",
                                         text_color=WHITE,
                                         command=lambda: self.switch_login_tab("manager"))
        self.tab_manager.pack(side="left", padx=5)

        self.username_entry = ctk.CTkEntry(right, placeholder_text="Enter your Username",
                                           width=320, height=48, corner_radius=12)
        self.username_entry.pack(pady=8)

        pass_frame = ctk.CTkFrame(right, fg_color="transparent")
        pass_frame.pack(pady=8)
        self.password_entry = ctk.CTkEntry(pass_frame, placeholder_text="Enter your Password",
                                           show="*", width=275, height=48, corner_radius=12)
        self.password_entry.pack(side="left")
        self.show_pass = False
        ctk.CTkButton(pass_frame, text="👁", width=40, height=48,
                      corner_radius=12, fg_color="#444444", hover_color="#555555",
                      command=self.toggle_password).pack(side="left", padx=5)

        self.error_label = ctk.CTkLabel(right, text="", text_color="red",
                                        font=("Arial", 12))
        self.error_label.pack(pady=3)

        ctk.CTkButton(right, text="Sign In", fg_color=PINK, hover_color="#C0006E",
                      width=320, height=48, corner_radius=24,
                      font=("Arial", 15, "bold"),
                      command=self.sign_in).pack(pady=8)

        ctk.CTkButton(right, text="Create Account", fg_color="transparent",
                      border_color=PINK, border_width=2, text_color=PINK,
                      width=320, height=48, corner_radius=24,
                      hover_color="#2A2A2A",
                      command=self.show_signup_page).pack(pady=8)

    def switch_login_tab(self, role):
        self.login_role.set(role)
        if role == "customer":
            self.tab_customer.configure(fg_color=PINK, hover_color="#C0006E")
            self.tab_manager.configure(fg_color="#444444", hover_color="#C0006E")
        else:
            self.tab_manager.configure(fg_color=PINK, hover_color="#C0006E")
            self.tab_customer.configure(fg_color="#444444", hover_color="#C0006E")

    def toggle_password(self):
        self.show_pass = not self.show_pass
        self.password_entry.configure(show="" if self.show_pass else "*")

    def sign_in(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if self.platform.sign_in(username, password):
            user = self.platform.current_user
            if user.role != self.login_role.get():
                self.platform.current_user = None
                self.error_label.configure(text="Wrong role selected.")
                return
            if user.role == "manager":
                self.show_manager_dashboard()
            else:
                self.show_customer_dashboard()
        else:
            self.error_label.configure(text="Invalid username or password.")

    #================ Signup Page ==================
    def show_signup_page(self):
        self.clear()

        self.update_idletasks()
        win_w = self.winfo_screenwidth()
        win_h = self.winfo_screenheight()
        img_w = int(win_w * 0.38)

        left = ctk.CTkFrame(self, fg_color=PINK, width=img_w)
        left.pack_propagate(False)
        left.pack(side="left", fill="y")

        bg_img = ctk.CTkImage(Image.open("assets/login_bg.png"), size=(img_w, win_h))
        self._image_refs.append(bg_img)
        bg_label = ctk.CTkLabel(left, image=bg_img, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        right = ctk.CTkFrame(self, fg_color=GRAY)
        right.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right, text="Create Account",
                     font=("Arial Black", 32, "bold"),
                     text_color=WHITE).pack(pady=(40, 5))

        self.signup_first = ctk.CTkEntry(right, placeholder_text="First Name",
                                         width=320, height=45, corner_radius=12)
        self.signup_first.pack(pady=5)

        self.signup_last = ctk.CTkEntry(right, placeholder_text="Last Name",
                                        width=320, height=45, corner_radius=12)
        self.signup_last.pack(pady=5)

        self.signup_username = ctk.CTkEntry(right, placeholder_text="Username",
                                            width=320, height=45, corner_radius=12)
        self.signup_username.pack(pady=5)

        signup_pass_frame = ctk.CTkFrame(right, fg_color="transparent")
        signup_pass_frame.pack(pady=5)
        self.signup_password = ctk.CTkEntry(signup_pass_frame, placeholder_text="Password",
                                            show="*", width=275, height=45, corner_radius=12)
        self.signup_password.pack(side="left")
        self.show_signup_pass = False
        ctk.CTkButton(signup_pass_frame, text="👁", width=40, height=45,
                      corner_radius=12, fg_color="#444444", hover_color="#555555",
                      command=self.toggle_signup_password).pack(side="left", padx=5)

        self.role_var = ctk.StringVar(value="customer")
        role_frame = ctk.CTkFrame(right, fg_color="transparent")
        role_frame.pack(pady=5)
        ctk.CTkRadioButton(role_frame, text="Customer", variable=self.role_var,
                           value="customer", fg_color=PINK).pack(side="left", padx=20)
        ctk.CTkRadioButton(role_frame, text="Manager", variable=self.role_var,
                           value="manager", fg_color=PINK).pack(side="left", padx=20)

        self.restaurant_entry = ctk.CTkEntry(right, placeholder_text="Restaurant Name (if Manager)",
                                             width=320, height=45, corner_radius=12)
        self.restaurant_entry.pack(pady=5)

        self.signup_error = ctk.CTkLabel(right, text="", text_color="red",
                                         font=("Arial", 12))
        self.signup_error.pack(pady=3)

        ctk.CTkButton(right, text="Sign Up", fg_color=PINK, hover_color="#C0006E",
                      width=320, height=48, corner_radius=24,
                      font=("Arial", 15, "bold"),
                      command=self.sign_up).pack(pady=5)

        ctk.CTkButton(right, text="Back to Sign In", fg_color="transparent",
                      border_color=PINK, border_width=2, text_color=PINK,
                      width=320, height=48, corner_radius=24,
                      hover_color="#2A2A2A",
                      command=self.show_login_page).pack(pady=5)

    def toggle_signup_password(self):
        self.show_signup_pass = not self.show_signup_pass
        self.signup_password.configure(show="" if self.show_signup_pass else "*")

    def sign_up(self):
        first = self.signup_first.get().strip()
        last = self.signup_last.get().strip()
        username = self.signup_username.get().strip()
        password = self.signup_password.get().strip()
        role = self.role_var.get()
        restaurant = self.restaurant_entry.get().strip()

        if role == "manager" and not restaurant:
            self.signup_error.configure(text="Please enter a restaurant name.")
            return

        result = self.platform.sign_up(first, last, username, password, role, restaurant)
        if result:
            save_data(self.platform)
            self.show_login_page()
        else:
            if role == "manager" and restaurant and self.platform.find_restaurant(restaurant):
                self.signup_error.configure(text="A restaurant with this name already exists.")
            elif self.platform.find_user(username):
                self.signup_error.configure(text="Username already exists.")
            else:
                from models.user import User
                if not User.validate_name(first):
                    self.signup_error.configure(text="Invalid first name. Letters only, min 2 characters.")
                elif not User.validate_name(last):
                    self.signup_error.configure(text="Invalid last name. Letters only, min 2 characters.")
                elif not User.validate_username(username):
                    self.signup_error.configure(text="Invalid username. Letters and numbers only, min 4 characters.")
                elif not User.validate_password(password):
                    self.signup_error.configure(text="Invalid password. Min 6 characters.")
                else:
                    self.signup_error.configure(text="Sign up failed. Check your inputs.")
    

    #==================== Manager Dashboard ======================
    def show_manager_dashboard(self):
        self.clear()
        manager = self.platform.current_user

        sidebar = ctk.CTkFrame(self, fg_color="#1A1A1A", width=200)
        sidebar.pack_propagate(False)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="🍴", font=("Arial", 30)).pack(pady=(30, 5))
        ctk.CTkLabel(sidebar, text="Snapp Food",
                     font=("Arial Black", 14, "bold"),
                     text_color=PINK).pack(pady=(0, 30))

        ctk.CTkLabel(sidebar, text=f"👤  {manager.first_name}",
                     font=("Arial", 13), text_color=WHITE).pack(pady=5)
        ctk.CTkLabel(sidebar, text=f"🏪  {manager.restaurant.name}",
                     font=("Arial", 11), text_color="#AAAAAA",
                     wraplength=160).pack(pady=5)

        ctk.CTkButton(sidebar, text="📋  View Orders", fg_color="transparent",
                      hover_color="#333333", anchor="w", width=180,
                      command=self.show_orders).pack(pady=5, padx=10)

        ctk.CTkButton(sidebar, text="🚪  Sign Out", fg_color="transparent",
                      hover_color="#333333", anchor="w", width=180,
                      text_color="#FF6666",
                      command=self.sign_out).pack(side="bottom", pady=20, padx=10)

        main = ctk.CTkFrame(self, fg_color=GRAY)
        main.pack(side="right", fill="both", expand=True)

        top = ctk.CTkFrame(main, fg_color=PINK, height=60)
        top.pack_propagate(False)
        top.pack(fill="x")
        ctk.CTkLabel(top, text=f"Snapp Food  |  {manager.restaurant.name}",
                     font=("Arial Black", 18, "bold"),
                     text_color=WHITE).pack(side="left", padx=20, pady=10)

        body = ctk.CTkFrame(main, fg_color=GRAY)
        body.pack(fill="both", expand=True, padx=20, pady=20)

        left = ctk.CTkFrame(body, fg_color="#2A2A2A", corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(left, text="Menu", font=("Arial", 18, "bold"),
                     text_color=WHITE).pack(pady=15)

        self.menu_frame = ctk.CTkScrollableFrame(left, fg_color="#2A2A2A")
        self.menu_frame.pack(fill="both", expand=True, padx=10)

        self.refresh_menu()

        right = ctk.CTkFrame(body, fg_color="#2A2A2A", corner_radius=12, width=300)
        right.pack_propagate(False)
        right.pack(side="right", fill="y")

        ctk.CTkLabel(right, text="Add Item", font=("Arial", 18, "bold"),
                     text_color=WHITE).pack(pady=15)

        self.item_name_entry = ctk.CTkEntry(right, placeholder_text="Item Name",
                                            width=240, height=40, corner_radius=8)
        self.item_name_entry.pack(pady=6)

        ctk.CTkLabel(right, text="Select Image:", text_color="#AAAAAA",
                     font=("Arial", 12)).pack(pady=(6, 2))
        self.image_var = ctk.StringVar(value=IMAGES[0])
        self.image_dropdown = ctk.CTkOptionMenu(right, variable=self.image_var,
                                                values=IMAGES, width=240, height=40,
                                                fg_color="#444444", button_color=PINK,
                                                corner_radius=8)
        self.image_dropdown.pack(pady=6)

        self.item_price = ctk.CTkEntry(right, placeholder_text="Price",
                                       width=240, height=40, corner_radius=8)
        self.item_price.pack(pady=6)

        self.item_type = ctk.StringVar(value="food")
        type_frame = ctk.CTkFrame(right, fg_color="transparent")
        type_frame.pack(pady=6)
        for val, lbl in [("food", "Food"), ("drink", "Drink"), ("dessert", "Dessert")]:
            ctk.CTkRadioButton(type_frame, text=lbl, variable=self.item_type,
                               value=val, fg_color=PINK, width=80).pack(side="left", padx=6)

        self.add_item_error = ctk.CTkLabel(right, text="", text_color="red",
                                           font=("Arial", 11))
        self.add_item_error.pack()

        ctk.CTkButton(right, text="Add to Menu", fg_color=PINK, hover_color="#C0006E",
                      width=240, height=42, corner_radius=10,
                      font=("Arial", 13, "bold"),
                      command=self.add_item).pack(pady=8)

    def refresh_menu(self):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        manager = self.platform.current_user
        if not manager.restaurant.menu:
            ctk.CTkLabel(self.menu_frame, text="Menu is empty.",
                         text_color="#AAAAAA").pack(pady=20)
            return

        for item in manager.restaurant.menu:
            row = ctk.CTkFrame(self.menu_frame, fg_color="#3A3A3A", corner_radius=10)
            row.pack(fill="x", pady=4)

            if item.image:
                img = load_image(item.image, size=(50, 50))
                if img:
                    self._image_refs.append(img)
                    ctk.CTkLabel(row, image=img, text="").pack(side="left", padx=8, pady=6)

            ctk.CTkLabel(row, text=f"{item.name}  |  {item.item_type}  |  ${item.price:,}",
                         text_color=WHITE, font=("Arial", 13)).pack(side="left", padx=8, pady=10)

            status = "Available" if item.is_available else "Unavailable"
            color = "#00CC66" if item.is_available else "#FF4444"
            ctk.CTkLabel(row, text=status, text_color=color,
                         font=("Arial", 12)).pack(side="right", padx=10)

            ctk.CTkButton(row, text="Remove", fg_color="#AA0000", hover_color="#880000",
                          width=70, height=30, corner_radius=8,
                          command=lambda i=item: self.remove_item(i.name)).pack(side="right", padx=5)

            toggle_text = "Disable" if item.is_available else "Enable"
            ctk.CTkButton(row, text=toggle_text, fg_color="#555555", hover_color="#666666",
                          width=70, height=30, corner_radius=8,
                          command=lambda i=item: self.toggle_availability(i)).pack(side="right", padx=5)

            ctk.CTkButton(row, text="Edit", fg_color="#2255AA", hover_color="#1144AA",
                          width=55, height=30, corner_radius=8,
                          command=lambda i=item: self.show_edit_item_dialog(i)).pack(side="right", padx=5)

    def add_item(self):
        from models.menu_item import MenuItem
        name = self.item_name_entry.get().strip()
        image = self.image_var.get()
        price = self.item_price.get().strip()

        if not name:
            self.add_item_error.configure(text="Please enter an item name.")
            return
        if not price:
            self.add_item_error.configure(text="Please enter a price.")
            return
        if not price.isdigit():
            self.add_item_error.configure(text="Price must be a number.")
            return

        item = MenuItem(name, int(price), self.item_type.get(), image=image)
        self.platform.current_user.add_item(item)
        save_data(self.platform)
        self.item_name_entry.delete(0, "end")
        self.item_price.delete(0, "end")
        self.add_item_error.configure(text="")
        self.refresh_menu()

    def remove_item(self, item_name):
        self.platform.current_user.remove_item(item_name)
        save_data(self.platform)
        self.refresh_menu()

    def toggle_availability(self, item):
        item.is_available = not item.is_available
        save_data(self.platform)
        self.refresh_menu()

    def show_edit_item_dialog(self, item):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Item")
        dialog.geometry("360x340")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Edit: {item.name}",
                     font=("Arial", 16, "bold"), text_color=PINK).pack(pady=(20, 5))

        ctk.CTkLabel(dialog, text="New Name:", text_color="#AAAAAA",
                     font=("Arial", 12)).pack(pady=(10, 2))
        name_entry = ctk.CTkEntry(dialog, width=260, height=40, corner_radius=8)
        name_entry.insert(0, item.name)
        name_entry.pack()

        ctk.CTkLabel(dialog, text="New Price:", text_color="#AAAAAA",
                     font=("Arial", 12)).pack(pady=(10, 2))
        price_entry = ctk.CTkEntry(dialog, width=260, height=40, corner_radius=8)
        price_entry.insert(0, str(item.price))
        price_entry.pack()

        ctk.CTkLabel(dialog, text="Item Type:", text_color="#AAAAAA",
                     font=("Arial", 12)).pack(pady=(10, 2))
        type_var = ctk.StringVar(value=item.item_type)
        type_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        type_frame.pack()
        ctk.CTkRadioButton(type_frame, text="Food", variable=type_var,
                           value="food", fg_color=PINK).pack(side="left", padx=8)
        ctk.CTkRadioButton(type_frame, text="Drink", variable=type_var,
                           value="drink", fg_color=PINK).pack(side="left", padx=8)
        ctk.CTkRadioButton(type_frame, text="Dessert", variable=type_var,
                           value="dessert", fg_color=PINK).pack(side="left", padx=8)

        err_label = ctk.CTkLabel(dialog, text="", text_color="red", font=("Arial", 11))
        err_label.pack(pady=4)

        def save_edit():
            new_name = name_entry.get().strip()
            new_price = price_entry.get().strip()
            if not new_name:
                err_label.configure(text="Name cannot be empty.")
                return
            if not new_price.isdigit():
                err_label.configure(text="Price must be a number.")
                return
            old_name = item.name
            self.platform.current_user.edit_item(
                old_name,
                new_name=new_name,
                new_price=int(new_price),
                new_type=type_var.get()
            )   
            save_data(self.platform)
            self.refresh_menu()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Save", fg_color=PINK, hover_color="#C0006E",
                      width=260, height=40, corner_radius=10,
                      command=save_edit).pack(pady=8)

    def show_orders(self):
        orders = self.platform.current_user.restaurant.orders
        popup = ctk.CTkToplevel(self)
        popup.title("Orders")
        popup.geometry("550x450")

        ctk.CTkLabel(popup, text="Restaurant Orders",
                     font=("Arial", 18, "bold")).pack(pady=15)

        frame = ctk.CTkScrollableFrame(popup)
        frame.pack(fill="both", expand=True, padx=15, pady=10)

        if not orders:
            ctk.CTkLabel(frame, text="No orders yet.",
                         text_color="#AAAAAA").pack(pady=20)
            return

        for order in orders:
            box = ctk.CTkFrame(frame, fg_color="#333333", corner_radius=8)
            box.pack(fill="x", pady=5)
            ctk.CTkLabel(box, text=f"Order {order.order_id}  |  {order.time}  |  Total: ${order.get_total():,}",
                         text_color=WHITE, font=("Arial", 13)).pack(padx=10, pady=5)
            for item in order.items:
                ctk.CTkLabel(box, text=f"  - {item.name}  ${item.price:,}",
                             text_color="#AAAAAA", font=("Arial", 12)).pack(padx=20, pady=2)

    #===================== Customer Dashboard =====================
    def show_customer_dashboard(self):
        self.clear()
        customer = self.platform.current_user
        self.current_restaurant = None

        sidebar = ctk.CTkFrame(self, fg_color="#1A1A1A", width=200)
        sidebar.pack_propagate(False)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="🍴", font=("Arial", 30)).pack(pady=(30, 5))
        ctk.CTkLabel(sidebar, text="Snapp Food",
                     font=("Arial Black", 14, "bold"),
                     text_color=PINK).pack(pady=(0, 30))

        ctk.CTkLabel(sidebar, text=f"👤  {customer.first_name}",
                     font=("Arial", 13), text_color=WHITE).pack(pady=5)

        ctk.CTkButton(sidebar, text="📦  My Orders", fg_color="transparent",
                      hover_color="#333333", anchor="w", width=180,
                      command=self.show_order_history).pack(pady=5, padx=10)

        ctk.CTkButton(sidebar, text="🏠  Restaurants", fg_color="transparent",
                      hover_color="#333333", anchor="w", width=180,
                      command=self.show_customer_dashboard).pack(pady=5, padx=10)

        ctk.CTkButton(sidebar, text="🚪  Sign Out", fg_color="transparent",
                      hover_color="#333333", anchor="w", width=180,
                      text_color="#FF6666",
                      command=self.sign_out).pack(side="bottom", pady=20, padx=10)

        main = ctk.CTkFrame(self, fg_color=GRAY)
        main.pack(side="right", fill="both", expand=True)

        top = ctk.CTkFrame(main, fg_color=PINK, height=60)
        top.pack_propagate(False)
        top.pack(fill="x")
        ctk.CTkLabel(top, text=f"Snapp Food  |  Welcome, {customer.first_name}!",
                     font=("Arial Black", 18, "bold"),
                     text_color=WHITE).pack(side="left", padx=20, pady=10)

        body = ctk.CTkFrame(main, fg_color=GRAY)
        body.pack(fill="both", expand=True, padx=15, pady=15)

        left = ctk.CTkFrame(body, fg_color="#2A2A2A", corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        rest_label_frame = ctk.CTkFrame(left, fg_color="transparent")
        rest_label_frame.pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(rest_label_frame, text="🏪  Restaurants",
                     font=("Arial", 14, "bold"), text_color=WHITE).pack(side="left")

        rest_frame = ctk.CTkFrame(left, fg_color="transparent")
        rest_frame.pack(fill="x", padx=15, pady=(0, 10))

        for r in self.platform.restaurants:
            ctk.CTkButton(rest_frame, text=f"🍽  {r.name}",
                          fg_color="#3A3A3A", hover_color=PINK,
                          height=38, corner_radius=10,
                          command=lambda rest=r: self.show_restaurant_menu(rest)).pack(
                fill="x", pady=3)

        self.menu_display = ctk.CTkScrollableFrame(left, fg_color="#2A2A2A")
        self.menu_display.pack(fill="both", expand=True, padx=10, pady=5)

        right = ctk.CTkFrame(body, fg_color="#2A2A2A", corner_radius=12, width=270)
        right.pack_propagate(False)
        right.pack(side="right", fill="y")

        ctk.CTkLabel(right, text="🛒  Cart", font=("Arial", 18, "bold"),
                     text_color=WHITE).pack(pady=15)

        self.cart_frame = ctk.CTkScrollableFrame(right, fg_color="#2A2A2A", height=350)
        self.cart_frame.pack(fill="x", padx=10)

        self.total_label = ctk.CTkLabel(right, text="Total: $0",
                                        font=("Arial", 15, "bold"), text_color=WHITE)
        self.total_label.pack(pady=10)

        self.checkout_error = ctk.CTkLabel(right, text="", text_color="red",
                                           font=("Arial", 11))
        self.checkout_error.pack()

        ctk.CTkButton(right, text="✓  Checkout", fg_color=PINK, hover_color="#C0006E",
                      width=220, height=45, corner_radius=12,
                      font=("Arial", 14, "bold"),
                      command=self.checkout).pack(pady=10)

        self.refresh_cart()

    def show_restaurant_menu(self, restaurant):
        self.current_restaurant = restaurant

        for widget in self.menu_display.winfo_children():
            widget.destroy()


        ctk.CTkButton(self.menu_display, text="← Back to Restaurants",
                      fg_color="transparent", hover_color="#333333",
                      text_color="#AAAAAA", anchor="w", width=200,
                      command=self.back_to_restaurants).pack(anchor="w", pady=(5, 10))

        ctk.CTkLabel(self.menu_display, text=f"🍽  {restaurant.name}",
                     font=("Arial", 15, "bold"), text_color=PINK).pack(pady=5)

        foods = [i for i in restaurant.menu if i.item_type == "food"]
        drinks = [i for i in restaurant.menu if i.item_type == "drink"]
        desserts = [i for i in restaurant.menu if i.item_type == "dessert"]

        if foods:
            ctk.CTkLabel(self.menu_display, text="🍔  Food",
                         font=("Arial", 13, "bold"),
                         text_color="#AAAAAA").pack(anchor="w", padx=5, pady=(5, 2))
            self.create_grid(foods)

        if drinks:
            ctk.CTkLabel(self.menu_display, text="🥤  Drinks",
                         font=("Arial", 13, "bold"),
                         text_color="#AAAAAA").pack(anchor="w", padx=5, pady=(10, 2))
            self.create_grid(drinks)

        if desserts:
            ctk.CTkLabel(self.menu_display, text="🍰  Desserts",
                         font=("Arial", 13, "bold"),
                         text_color="#AAAAAA").pack(anchor="w", padx=5, pady=(10, 2))
            self.create_grid(desserts)

    def back_to_restaurants(self):
        """ بازگشت به لیست رستوران‌ها و پاک کردن نمایش منو"""
        for widget in self.menu_display.winfo_children():
            widget.destroy()
        self.current_restaurant = None
        ctk.CTkLabel(self.menu_display, text="Select a restaurant to view its menu.",
                     text_color="#AAAAAA", font=("Arial", 13)).pack(pady=30)

    def create_grid(self, items):
        customer = self.platform.current_user
        row_frame = None

        for i, item in enumerate(items):
            if i % 3 == 0:
                row_frame = ctk.CTkFrame(self.menu_display, fg_color="transparent")
                row_frame.pack(fill="x", pady=5)

            cart_count = sum(1 for c in customer.cart
                             if c.name == item.name and c.image == item.image)
            in_cart = cart_count > 0

            card = ctk.CTkFrame(row_frame,
                                fg_color="#2A2A2A" if not in_cart else "#1A2A1A",
                                corner_radius=14, width=200, height=250)
            card.pack_propagate(False)
            card.pack(side="left", padx=6)

            if item.image:
                img = load_image(item.image, size=(110, 110))
                if img:
                    self._image_refs.append(img)
                    ctk.CTkLabel(card, image=img, text="",
                                 fg_color="transparent").pack(pady=(15, 5))
            else:
                ctk.CTkLabel(card, text="🍽", font=("Arial", 50)).pack(pady=(15, 5))

            ctk.CTkLabel(card, text=item.name, font=("Arial", 12, "bold"),
                         text_color=WHITE, wraplength=180).pack(anchor="w", padx=10)

            ctk.CTkLabel(card, text=f"${item.price:,}", font=("Arial", 12, "bold"),
                         text_color=PINK).pack(anchor="w", padx=10, pady=2)

            if not item.is_available:
                ctk.CTkLabel(card, text="Unavailable", text_color="#FF4444",
                             font=("Arial", 10)).pack(pady=3)
            else:
                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(pady=3)

                ctk.CTkButton(btn_frame, text="+ Add", fg_color=PINK,
                              hover_color="#C0006E", width=80, height=28,
                              corner_radius=8,
                              command=lambda i=item: self.add_to_cart(i)).pack(side="left", padx=3)

                if in_cart:
                    ctk.CTkLabel(btn_frame, text=f"✓ {cart_count}",
                                 text_color="#00CC66",
                                 font=("Arial", 12, "bold")).pack(side="left", padx=5)

    def add_to_cart(self, item):
        self.platform.current_user.add_to_cart(item)
        if self.current_restaurant:
            item._restaurant = self.current_restaurant.name
        self.refresh_cart()
        if self.current_restaurant:
            self.show_restaurant_menu(self.current_restaurant)

    def remove_from_cart_and_refresh(self, item_name, item_restaurant):
        customer = self.platform.current_user
        for i, item in enumerate(customer.cart):
            if item.name == item_name and getattr(item, '_restaurant', '') == item_restaurant:
                customer.cart.pop(i)
                break
        self.refresh_cart()
        if self.current_restaurant:
            self.show_restaurant_menu(self.current_restaurant)

    def refresh_cart(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        customer = self.platform.current_user
        if not customer.cart:
            ctk.CTkLabel(self.cart_frame, text="Cart is empty.",
                         text_color="#AAAAAA").pack(pady=20)
            self.total_label.configure(text="Total: $0")
            return


        for item in customer.cart:
            row = ctk.CTkFrame(self.cart_frame, fg_color="#3A3A3A", corner_radius=8)
            row.pack(fill="x", pady=3)

            if item.image:
                img = load_image(item.image, size=(35, 35))
                if img:
                    self._image_refs.append(img)
                    ctk.CTkLabel(row, image=img, text="").pack(side="left", padx=6, pady=5)

            ctk.CTkLabel(row, text=f"{item.name}  ${item.price:,}",
                         text_color=WHITE, font=("Arial", 12)).pack(side="left", padx=6, pady=8)

            ctk.CTkButton(row, text="✕", fg_color="#AA0000", hover_color="#880000",
                          width=28, height=28, corner_radius=6,
                          command=lambda i=item: self.remove_from_cart_and_refresh(
                              i.name, getattr(i, '_restaurant', ''))).pack(side="right", padx=5)

        total = sum(i.price for i in customer.cart)
        self.total_label.configure(text=f"Total: ${total:,}")

    def checkout(self):
        customer = self.platform.current_user
        if not customer.cart:
            self.checkout_error.configure(text="Your cart is empty.")
            return

    
        from models.order import Order
        restaurant_items = {}
        for item in customer.cart:
            r_name = getattr(item, '_restaurant', None)
            if r_name is None and self.current_restaurant:
                r_name = self.current_restaurant.name
            if r_name not in restaurant_items:
                restaurant_items[r_name] = []
            restaurant_items[r_name].append(item)

        orders = []
        for r_name, items in restaurant_items.items():
            restaurant = next((r for r in self.platform.restaurants
                               if r.name == r_name), self.current_restaurant)
            if restaurant:
                order_id = f"ORD{get_next_order_number() + len(orders)}"
                order = Order(order_id, customer.username, restaurant.name)
                for item in items:
                    order.add_item(item)
                customer.order_history.append(order)
                restaurant.add_order(order)
                orders.append(order)

        customer.cart = []
        save_data(self.platform)
        self.checkout_error.configure(text="")
        self.refresh_cart()
        if self.current_restaurant:
            self.show_restaurant_menu(self.current_restaurant)
        self.show_invoice(orders)

    def show_invoice(self, orders):
        popup = ctk.CTkToplevel(self)
        popup.title("Invoice")
        popup.geometry("450x500")

        ctk.CTkLabel(popup, text="✓  Order Confirmed!",
                     font=("Arial", 22, "bold"), text_color="#00CC66").pack(pady=20)

        frame = ctk.CTkScrollableFrame(popup, height=300)
        frame.pack(fill="x", padx=20, pady=10)

        total_all = 0
        for order in orders:
            ctk.CTkLabel(frame, text=f"🏪  {order.restaurant}",
                         font=("Arial", 14, "bold"), text_color=PINK).pack(anchor="w", pady=(10, 2))
            ctk.CTkLabel(frame, text=f"Order ID: {order.order_id}  |  {order.time}",
                         font=("Arial", 11), text_color="#AAAAAA").pack(anchor="w")
            for item in order.items:
                ctk.CTkLabel(frame, text=f"  - {item.name}  ${item.price:,}",
                             font=("Arial", 12)).pack(anchor="w")
            ctk.CTkLabel(frame, text=f"Subtotal: ${order.get_total():,}",
                         font=("Arial", 12, "bold"), text_color=WHITE).pack(anchor="w", pady=3)
            total_all += order.get_total()

        ctk.CTkLabel(popup, text=f"Grand Total: ${total_all:,}",
                     font=("Arial", 18, "bold"), text_color=PINK).pack(pady=10)

        ctk.CTkButton(popup, text="Close", fg_color=PINK, hover_color="#C0006E",
                      corner_radius=10, command=popup.destroy).pack(pady=10)

    def show_order_history(self):
        customer = self.platform.current_user
        popup = ctk.CTkToplevel(self)
        popup.title("My Orders")
        popup.geometry("500x500")

        ctk.CTkLabel(popup, text="📦  My Order History",
                     font=("Arial", 18, "bold")).pack(pady=15)

        frame = ctk.CTkScrollableFrame(popup)
        frame.pack(fill="both", expand=True, padx=15, pady=10)

        if not customer.order_history:
            ctk.CTkLabel(frame, text="No previous orders.",
                         text_color="#AAAAAA").pack(pady=20)
            return

        for order in customer.order_history:
            box = ctk.CTkFrame(frame, fg_color="#333333", corner_radius=8)
            box.pack(fill="x", pady=5)
            ctk.CTkLabel(box, text=f"🏪  {order.restaurant}",
                         text_color=PINK, font=("Arial", 13, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
            ctk.CTkLabel(box, text=f"Order {order.order_id}  |  {order.time}  |  Total: ${order.get_total():,}",
                         text_color=WHITE, font=("Arial", 12)).pack(anchor="w", padx=10, pady=2)
            for item in order.items:
                ctk.CTkLabel(box, text=f"  - {item.name}  ${item.price:,}",
                             text_color="#AAAAAA", font=("Arial", 12)).pack(anchor="w", padx=20, pady=2)

    # ================== Sign Out =====================
    def sign_out(self):
        self.platform.sign_out()
        self.show_login_page()


def main():
    app = SnappFoodApp()
    app.mainloop()

if __name__ == "__main__":
    main()