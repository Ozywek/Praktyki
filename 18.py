def inventory_value(inventory):
    suma = 0
    for i in inventory:
        suma += inventory[i]["price"] * inventory[i]["qty"]
    return suma


def low_stock(inventory, threshold):
    low = []
    for i in inventory:
        if inventory[i]["qty"] < threshold:
            low.append(i)
    return low