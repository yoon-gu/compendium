"""The shopping cart. A cart is a dict of sku -> quantity."""
from catalog.products import in_stock, price_of


class Cart:
    def __init__(self):
        self.lines = {}

    def add(self, sku, qty=1):
        if not in_stock(sku, self.lines.get(sku, 0) + qty):
            raise ValueError(f"not enough stock for {sku}")
        self.lines[sku] = self.lines.get(sku, 0) + qty

    def remove(self, sku):
        self.lines.pop(sku, None)

    def subtotal(self):
        return sum(price_of(sku) * qty for sku, qty in self.lines.items())

    def is_empty(self):
        return not self.lines
