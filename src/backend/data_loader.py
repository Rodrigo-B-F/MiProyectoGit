from models import Category, Product, Inventory

def load_sample_data():
    """Carga categorías, productos e inventario de ejemplo en la BD."""
    # Crear categorías
    bebidas = Category.create(name="Bebidas", description="Líquidos envasados")
    lacteos = Category.create(name="Lácteos", description="Productos lácteos")
    aseo = Category.create(name="Aseo", description="Artículos de limpieza")

    # Crear productos
    agua = Product.create(
        name="Agua Mineral",
        barcode="44444444",
        category=bebidas,
        unit="botella",
        purchase_price=2.50,
        sale_price=4.00
    )
    leche = Product.create(
        name="Leche Entera",
        barcode="55555555",
        category=lacteos,
        unit="litro",
        purchase_price=5.00,
        sale_price=7.00
    )
    detergente = Product.create(
        name="Detergente en Polvo",
        barcode="66666666",
        category=aseo,
        unit="bolsa",
        purchase_price=12.00,
        sale_price=18.00
    )

    # Crear inventario inicial
    Inventory.create(product=agua, quantity=50)
    Inventory.create(product=leche, quantity=30)
    Inventory.create(product=detergente, quantity=20)

    print("Datos de ejemplo cargados en la base de datos.")

if __name__ == "__main__":
    load_sample_data()