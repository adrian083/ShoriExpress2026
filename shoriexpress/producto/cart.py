class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, producto):
        producto_id = str(producto.pk)
        if producto_id not in self.cart.keys():
            self.cart[producto_id] = {
                "producto_id": producto.pk,
                "nombre": producto.nombre_producto,
                "precio": str(producto.precio_venta),
                "cantidad": 1,
                "total": str(producto.precio_venta),
            }
        else:
            self.cart[producto_id]["cantidad"] += 1
            self.cart[producto_id]["total"] = str(
                float(self.cart[producto_id]["total"]) + float(producto.precio_venta)
            )
        self.save()

    def save(self):
        self.session["cart"] = self.cart
        self.session.modified = True

    def remove(self, producto):
        producto_id = str(producto.pk)
        if producto_id in self.cart:
            del self.cart[producto_id]
            self.save()

    def decrement(self, producto):
        producto_id = str(producto.pk)
        if producto_id in self.cart.keys():
            self.cart[producto_id]["cantidad"] -= 1
            self.cart[producto_id]["total"] = str(
                float(self.cart[producto_id]["total"]) - float(producto.precio_venta)
            )
            if self.cart[producto_id]["cantidad"] <= 0:
                self.remove(producto)
            else:
                self.save()

    def set_quantity(self, producto, cantidad):
        producto_id = str(producto.pk)
        precio = float(producto.precio_venta)
        if cantidad <= 0:
            self.remove(producto)
            return
        self.cart[producto_id] = {
            "producto_id": producto.pk,
            "nombre": producto.nombre_producto,
            "precio": str(producto.precio_venta),
            "cantidad": cantidad,
            "total": str(precio * cantidad),
        }
        self.save()

    def clear(self):
        self.session["cart"] = {}
        self.session.modified = True