class Product:
    def __init__(self, name, price, qty):
        self.name = name
        self.price = price
        self.qty = qty

    def total_value(self):
        return self.price*self.qty

    def is_available(self):
        if self.qty > 0:
            return True
        else: return False

    def sell(self, amount):
        if amount > self.qty:
            return False
        else:
            self.qty = self.qty - amount
            return True

def inventory_value(inventory):
    sum = 0
    for i in inventory:
        sum += i.total_value()
    return sum

def available_products(inventory):
    available = []
    for i in inventory:
        if i.is_available():
            available.append(i.name)
    return available

def low_stock(inventory, threshold):
    low = []
    for i in inventory:
        if i.qty < threshold:
            low.append(i.name)
    return low

def most_valuable(inventory):
    val = inventory[0].total_value()
    name = inventory[0].name
    for i in inventory:
        if i.total_value()>val:
            val = i.total_value()
            name = i.name
    return name

def find_by_name(inventory, name):
    for i in inventory:
        if i.name == name:
            return i

inventory = [
    Product("chleb", 5, 12),
    Product("mleko", 3, 0),
    Product("mas?o", 9, 3),
    Product("ser", 24, 7),
]

print(inventory_value(inventory))
print(available_products(inventory))
print(low_stock(inventory, 4))
print(most_valuable(inventory))



print(inventory_value(inventory))
bread = find_by_name(inventory, "chleb")
bread.sell(2)
print(inventory_value(inventory))

