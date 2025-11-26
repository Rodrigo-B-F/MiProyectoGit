# Plan de Implementación: Vista de Lotes en Inventario TUI

## Objetivo

Permitir que al hacer clic en una fila de producto en las vistas de inventario, se muestre una lista desplegable (modal) con los lotes asociados a ese producto, mostrando:
- Nro. Lote
- Cantidad (del lote)
- Fecha de Adquisición  
- Fecha de Vencimiento

## Análisis del Código Existente

### Modelo ProductBatch
Ubicación: `src/models/batch.py`

Campos disponibles:
- `id`: AutoField
- `product`: ForeignKey a Product
- `quantity`: IntegerField (cantidad en el lote)
- `expiration_date`: DateField (nullable)
- `purchase_date`: DateTimeField (fecha de adquisición)
- `purchase_price`: DecimalField
- `batch_number`: IntegerField (número secuencial por producto)
- `active`: BooleanField

### Vista Actual
- `InventoryViewerScreen` en `src/views/tui.py` (línea ~398)
- Usa `DataTable` widget de Textual
- Ya tiene el evento `on_data_table_row_selected` disponible en Textual

## Cambios Propuestos

### 1. Controller - Nueva Función

**Archivo:** `src/controllers/inventory_controller.py`

**Función a crear:**
```python
def list_batches_for_product(product_barcode):
    """
    Lista todos los lotes activos de un producto específico.
    
    Args:
        product_barcode: Código de barras del producto
        
    Returns:
        Lista de diccionarios con información de lotes
    """
    try:
        db.connect()
        product = Product.get(Product.barcode == product_barcode)
        
        batches = (ProductBatch
                  .select()
                  .where(
                      (ProductBatch.product == product) &
                      (ProductBatch.active == True)
                  )
                  .order_by(ProductBatch.expiration_date.asc(nulls='LAST')))
        
        data = []
        for batch in batches:
            data.append({
                "batch_number": batch.batch_number,
                "quantity": batch.quantity,
                "purchase_date": batch.purchase_date.strftime('%Y-%m-%d %H:%M') if batch.purchase_date else "N/A",
                "expiration_date": batch.expiration_date.strftime('%Y-%m-%d') if batch.expiration_date else "Sin vencimiento"
            })
        return data
    except Product.DoesNotExist:
        return []
    except Exception as e:
        print(f"Error al listar lotes: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()
```

### 2. TUI - Nueva Pantalla Modal

**Archivo:** `src/views/tui.py`

**Nueva clase a agregar:**
```python
class ProductBatchesModal(ModalScreen):
    """Modal para mostrar los lotes de un producto."""
    
    CSS_PATH = "tui.css"
    BINDINGS = [("escape", "dismiss", "Cerrar (ESC)")]
    
    def __init__(self, product_name: str, product_barcode: str, **kwargs):
        super().__init__(**kwargs)
        self.product_name = product_name
        self.product_barcode = product_barcode
    
    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(f"Lotes de: [b]{self.product_name}[/b]", id="modal-title"),
            DataTable(id="batches_table"),
            Button("Cerrar", id="close_batches", variant="primary"),
            id="batches-modal-container"
        )
    
    def on_mount(self) -> None:
        self.load_batches()
    
    def load_batches(self) -> None:
        table = self.query_one("#batches_table", DataTable)
        table.cursor_type = "row"
        
        # Columnas
        table.add_column("Nro. Lote", key="batch_number")
        table.add_column("Cantidad", key="quantity")
        table.add_column("Fecha de Adquisición", key="purchase_date")
        table.add_column("Fecha de Vencimiento", key="expiration_date")
        
        # Cargar datos
        batches = list_batches_for_product(self.product_barcode)
        
        if not batches:
            table.add_row("N/A", "No hay lotes", "N/A", "N/A")
        else:
            for batch in batches:
                table.add_row(
                    batch["batch_number"],
                    batch["quantity"],
                    batch["purchase_date"],
                    batch["expiration_date"]
                )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_batches":
            self.dismiss()
```

### 3. TUI - Modificar InventoryViewerScreen

**Ubicación:** Clase `InventoryViewerScreen` en `src/views/tui.py`

**Agregar método:**
```python
def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    """Maneja la selección de una fila para mostrar los lotes del producto."""
    table = self.query_one(DataTable)
    row_key = event.row_key
    
    # Obtener los datos de la fila seleccionada
    try:
        # La fila contiene los datos en el orden del header_map
        # Necesitamos el nombre (columna 0) y código de barras (columna 1)
        row_data = table.get_row(row_key)
        
        if len(row_data) >= 2:
            product_name = str(row_data[0])  # Primera columna: Nombre
            product_barcode = str(row_data[1])  # Segunda columna: Código de Barras
            
            # Abrir modal con los lotes
            self.app.push_screen(ProductBatchesModal(
                product_name=product_name,
                product_barcode=product_barcode
            ))
    except Exception as e:
        self.app.push_screen(NotificationScreen(f"Error al abrir lotes: {e}"))
```

### 4. TUI - Imports

**Ubicación:** Inicio de `src/views/tui.py`

**Agregar import:**
```python
from controllers.inventory_controller import (
    record_purchase,
    list_products_inventory,
    list_available_products,
    list_out_of_stock_products,
    list_expiring_products,
    list_categories,
    list_products_by_category,
    update_category,
    list_batches_for_product  # <-- NUEVO
)
```

### 5. CSS (Opcional)

**Archivo:** `src/views/tui.css`

Si se desea estilizar el modal:
```css
#batches-modal-container {
    align: center middle;
    width: 80%;
    height: 60%;
    border: thick $primary;
    background: $surface;
    padding: 1;
}

#modal-title {
    text-align: center;
    padding: 1;
    background: $primary;
    color: $text;
}
```

## Consideraciones Importantes

1. **Orden de Columnas:** El código asume que en el `STANDARD_INVENTORY_COLUMNS` las primeras dos columnas son "Nombre" y "Código de Barras" (en ese orden), lo cual es correcto según la implementación actual.

2. **Compatibilidad:** Esta funcionalidad aplica automáticamente a todas las vistas que usan `InventoryViewerScreen`:
   - PRODUCTOS ACTIVOS
   - PRODUCTOS INACTIVOS
   - PRODUCTOS CON STOCK
   - PRODUCTOS SIN STOCK
   -VER PRÓXIMOS A VENCER

3. **Vistas que NO se modifican automáticamente:**
   - BUSCAR PRODUCTO (usa `SearchProductScreen`)
   - VER POR CATEGORÍA (usa `ViewByCategoryScreen`)
   
   Estas necesitarían agregar el mismo método `on_data_table_row_selected` si se quiere la misma funcionalidad.

## Verificación

1. Compilar sintaxis: `python -m py_compile src/views/tui.py`
2. Compilar sintaxis: `python -m py_compile src/controllers/inventory_controller.py`
3. Ejecutar TUI: `python src/views/tui.py`
4. Navegar a VER → PRODUCTOS ACTIVOS
5. Hacer clic en una fila de producto
6. Verificar que se muestra el modal con los lotes

## Orden de Implementación

1. Agregar función `list_batches_for_product` en `inventory_controller.py`
2. Agregar import de la función en `tui.py`
3. Crear clase `ProductBatchesModal` en `tui.py`
4. Agregar método `on_data_table_row_selected` a `InventoryViewerScreen`
5. (Opcional) Agregar el mismo método a `SearchProductScreen` y `ViewByCategoryScreen`
6. Probar
