class MenuItem:
    def __init__(self, name, price, item_type, is_available=True, image=None):
        self.name = name
        self.price = price
        self.item_type = item_type
        self.is_available = is_available
        self.image = image

    def display(self):
        status = "Available" if self.is_available else "Not Available"
        print(f"{self.name} | {self.item_type} | ${self.price} | {status}")

    def to_dict(self):
        return{
            "name": self.name,
            "price": self.price,
            "item_type": self.item_type,
            "is_available": self.is_available,
            "image" : self.image
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            data["price"],
            data["item_type"],
            data["is_available"],
            data.get("image", None)
        )