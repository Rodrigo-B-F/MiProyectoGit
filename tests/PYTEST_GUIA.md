# Guía de Pruebas Unitarias con Pytest

Esta guía proporciona toda la información necesaria para crear y ejecutar pruebas unitarias en el proyecto utilizando **pytest**.

## Tabla de Contenidos

1. [Instalación](#instalación)
2. [Estructura de Pruebas](#estructura-de-pruebas)
3. [Configuración Inicial](#configuración-inicial)
4. [Escribiendo Pruebas Básicas](#escribiendo-pruebas-básicas)
5. [Fixtures](#fixtures)
6. [Pruebas de Base de Datos](#pruebas-de-base-de-datos)
7. [Mocking y Patching](#mocking-y-patching)
8. [Parametrización de Pruebas](#parametrización-de-pruebas)
9. [Ejecutando las Pruebas](#ejecutando-las-pruebas)
10. [Cobertura de Código](#cobertura-de-código)
11. [Mejores Prácticas](#mejores-prácticas)
12. [Ejemplos Específicos del Proyecto](#ejemplos-específicos-del-proyecto)

---

## Instalación

### 1. Instalar pytest y dependencias relacionadas

```bash
pip install pytest pytest-cov pytest-mock
```

### 2. Actualizar requirements.txt

Agrega las siguientes líneas a tu archivo `requirements.txt`:

```
pytest==8.0.0
pytest-cov==4.1.0
pytest-mock==3.12.0
```

---

## Estructura de Pruebas

Organiza tus pruebas siguiendo la estructura del código fuente:

```
MiProyectoGit/
├── src/
│   ├── models/
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── inventory.py
│   │   ├── sale.py
│   │   └── batch.py
│   ├── controllers/
│   │   ├── product/
│   │   ├── inventory/
│   │   ├── sale/
│   │   └── batch/
│   └── views/
│       ├── tui/
│       └── cli/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures compartidas
│   ├── PYTEST_GUIA.md           # Esta guía
│   ├── test_models/
│   │   ├── __init__.py
│   │   ├── test_product.py
│   │   ├── test_category.py
│   │   ├── test_inventory.py
│   │   ├── test_sale.py
│   │   └── test_batch.py
│   └── test_controllers/
│       ├── __init__.py
│       ├── test_product_controller.py
│       ├── test_inventory_controller.py
│       ├── test_sale_controller.py
│       └── test_batch_controller.py
└── pytest.ini                   # Configuración de pytest
```

---

## Configuración Inicial

### 1. Crear archivo `pytest.ini`

Crea un archivo `pytest.ini` en la raíz del proyecto:

```ini
[pytest]
# Directorio donde pytest buscará las pruebas
testpaths = tests

# Patrón de archivos de prueba
python_files = test_*.py

# Patrón de clases de prueba
python_classes = Test*

# Patrón de funciones de prueba
python_functions = test_*

# Opciones adicionales
addopts = 
    -v                    # Verbose (más detalles)
    --strict-markers      # Errores si se usan markers no registrados
    --tb=short            # Traceback corto
    --disable-warnings    # Deshabilitar warnings

# Markers personalizados
markers =
    slow: marca pruebas que son lentas
    integration: marca pruebas de integración
    unit: marca pruebas unitarias
    database: marca pruebas que requieren base de datos
```

### 2. Crear archivo `conftest.py`

El archivo `conftest.py` contiene fixtures compartidas entre todas las pruebas:

```python
import pytest
import sys
import os
from peewee import SqliteDatabase

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Importar modelos
from models.product import Product
from models.category import Category
from models.batch import Batch
from models.sale import Sale
from models.sale_detail import SaleDetail

# Lista de todos los modelos
MODELS = [Category, Product, Batch, Sale, SaleDetail]

@pytest.fixture
def test_db():
    """
    Fixture que crea una base de datos de prueba en memoria.
    Se ejecuta antes de cada prueba y se limpia después.
    """
    # Crear base de datos en memoria
    test_database = SqliteDatabase(':memory:')
    
    # Vincular modelos a la base de datos de prueba
    test_database.bind(MODELS, bind_refs=False, bind_backrefs=False)
    
    # Crear tablas
    test_database.create_tables(MODELS)
    
    yield test_database
    
    # Limpiar después de la prueba
    test_database.drop_tables(MODELS)
    test_database.close()


@pytest.fixture
def sample_category(test_db):
    """Fixture que crea una categoría de ejemplo."""
    return Category.create(
        name="Electrónica",
        description="Productos electrónicos"
    )


@pytest.fixture
def sample_product(test_db, sample_category):
    """Fixture que crea un producto de ejemplo."""
    return Product.create(
        name="Laptop HP",
        description="Laptop HP 15 pulgadas",
        price=1500.00,
        category=sample_category,
        is_active=True
    )


@pytest.fixture
def sample_batch(test_db, sample_product):
    """Fixture que crea un lote de ejemplo."""
    from datetime import datetime, timedelta
    
    return Batch.create(
        product=sample_product,
        quantity=10,
        acquisition_date=datetime.now(),
        expiration_date=datetime.now() + timedelta(days=365)
    )
```

---

## Escribiendo Pruebas Básicas

### Anatomía de una Prueba

```python
import pytest

def test_nombre_descriptivo():
    """Docstring que describe qué prueba esta función."""
    # 1. ARRANGE (Preparar): Configurar datos y estado inicial
    valor_esperado = 10
    
    # 2. ACT (Actuar): Ejecutar la función/método a probar
    resultado = funcion_a_probar(5, 5)
    
    # 3. ASSERT (Afirmar): Verificar que el resultado es el esperado
    assert resultado == valor_esperado
```

### Ejemplo: Prueba de Modelo Product

Crea el archivo `tests/test_models/test_product.py`:

```python
import pytest
from models.product import Product
from models.category import Category


class TestProduct:
    """Pruebas para el modelo Product."""
    
    def test_create_product(self, test_db, sample_category):
        """Prueba la creación de un producto."""
        # Arrange
        name = "Mouse Logitech"
        price = 25.50
        
        # Act
        product = Product.create(
            name=name,
            description="Mouse inalámbrico",
            price=price,
            category=sample_category,
            is_active=True
        )
        
        # Assert
        assert product.name == name
        assert product.price == price
        assert product.category == sample_category
        assert product.is_active is True
    
    def test_product_str_representation(self, test_db, sample_product):
        """Prueba la representación en string del producto."""
        # Act
        result = str(sample_product)
        
        # Assert
        assert "Laptop HP" in result
    
    def test_deactivate_product(self, test_db, sample_product):
        """Prueba la desactivación de un producto."""
        # Arrange
        assert sample_product.is_active is True
        
        # Act
        sample_product.is_active = False
        sample_product.save()
        
        # Assert
        updated_product = Product.get_by_id(sample_product.id)
        assert updated_product.is_active is False
    
    def test_product_price_validation(self, test_db, sample_category):
        """Prueba que el precio no puede ser negativo."""
        # Act & Assert
        with pytest.raises(Exception):
            Product.create(
                name="Producto Inválido",
                description="Test",
                price=-10.00,  # Precio negativo
                category=sample_category,
                is_active=True
            )
```

---

## Fixtures

Las fixtures son funciones que proporcionan datos o configuración para las pruebas.

### Tipos de Scope

```python
@pytest.fixture(scope="function")  # Default: se ejecuta para cada función de prueba
def fixture_function():
    pass

@pytest.fixture(scope="class")  # Se ejecuta una vez por clase
def fixture_class():
    pass

@pytest.fixture(scope="module")  # Se ejecuta una vez por módulo
def fixture_module():
    pass

@pytest.fixture(scope="session")  # Se ejecuta una vez por sesión de pruebas
def fixture_session():
    pass
```

### Ejemplo de Fixture con Setup y Teardown

```python
@pytest.fixture
def database_connection():
    """Fixture con setup y teardown."""
    # Setup: código que se ejecuta antes de la prueba
    db = create_database_connection()
    db.connect()
    
    yield db  # Proporciona el objeto a la prueba
    
    # Teardown: código que se ejecuta después de la prueba
    db.close()
```

---

## Pruebas de Base de Datos

### Ejemplo: Pruebas de Controlador de Inventario

Crea el archivo `tests/test_controllers/test_inventory_controller.py`:

```python
import pytest
from datetime import datetime, timedelta
from controllers.inventory_controller import (
    add_product,
    list_products_inventory,
    add_stock,
    get_product_stock
)


class TestInventoryController:
    """Pruebas para el controlador de inventario."""
    
    def test_add_product(self, test_db, sample_category):
        """Prueba agregar un producto nuevo."""
        # Arrange
        product_data = {
            'name': 'Teclado Mecánico',
            'description': 'Teclado RGB',
            'price': 80.00,
            'category_id': sample_category.id
        }
        
        # Act
        product = add_product(**product_data)
        
        # Assert
        assert product is not None
        assert product.name == product_data['name']
        assert product.price == product_data['price']
    
    def test_list_products_inventory(self, test_db, sample_product, sample_batch):
        """Prueba listar productos con inventario."""
        # Act
        products = list_products_inventory()
        
        # Assert
        assert len(products) > 0
        assert any(p['name'] == sample_product.name for p in products)
    
    def test_add_stock(self, test_db, sample_product):
        """Prueba agregar stock a un producto."""
        # Arrange
        quantity = 50
        acquisition_date = datetime.now()
        expiration_date = datetime.now() + timedelta(days=180)
        
        # Act
        batch = add_stock(
            product_id=sample_product.id,
            quantity=quantity,
            acquisition_date=acquisition_date,
            expiration_date=expiration_date
        )
        
        # Assert
        assert batch is not None
        assert batch.quantity == quantity
        assert batch.product == sample_product
    
    def test_get_product_stock(self, test_db, sample_product, sample_batch):
        """Prueba obtener el stock total de un producto."""
        # Act
        stock = get_product_stock(sample_product.id)
        
        # Assert
        assert stock == sample_batch.quantity
```

---

## Mocking y Patching

El mocking permite simular comportamientos de funciones o métodos sin ejecutar el código real.

### Usando pytest-mock

```python
import pytest
from unittest.mock import Mock, patch


def test_with_mock(mocker):
    """Ejemplo usando pytest-mock."""
    # Crear un mock
    mock_function = mocker.Mock(return_value=42)
    
    # Usar el mock
    result = mock_function()
    
    # Verificar
    assert result == 42
    mock_function.assert_called_once()


def test_with_patch(mocker):
    """Ejemplo usando patch para reemplazar una función."""
    # Patch de una función
    mocker.patch('controllers.inventory_controller.get_product_stock', return_value=100)
    
    # Ahora get_product_stock siempre retorna 100
    from controllers.inventory_controller import get_product_stock
    result = get_product_stock(1)
    
    assert result == 100
```

### Ejemplo: Mockear entrada de usuario

```python
def test_user_input_mock(mocker):
    """Prueba con input del usuario mockeado."""
    # Mockear la función input
    mocker.patch('builtins.input', return_value='test_input')
    
    # Ahora input() siempre retorna 'test_input'
    user_input = input("Ingrese algo: ")
    assert user_input == 'test_input'
```

---

## Parametrización de Pruebas

Permite ejecutar la misma prueba con diferentes datos de entrada.

```python
import pytest


@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 8),
])
def test_double(input_value, expected):
    """Prueba que una función duplica el valor."""
    result = input_value * 2
    assert result == expected


@pytest.mark.parametrize("price,discount,expected", [
    (100, 0.1, 90),
    (200, 0.2, 160),
    (50, 0.5, 25),
])
def test_apply_discount(price, discount, expected):
    """Prueba aplicar descuentos."""
    result = price * (1 - discount)
    assert result == expected
```

---

## Ejecutando las Pruebas

### Comandos Básicos

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar pruebas de un archivo específico
pytest tests/test_models/test_product.py

# Ejecutar una prueba específica
pytest tests/test_models/test_product.py::TestProduct::test_create_product

# Ejecutar pruebas con más detalle (verbose)
pytest -v

# Ejecutar pruebas y mostrar print statements
pytest -s

# Ejecutar solo las pruebas que fallaron la última vez
pytest --lf

# Ejecutar pruebas en paralelo (requiere pytest-xdist)
pytest -n auto
```

### Usando Markers

```bash
# Ejecutar solo pruebas unitarias
pytest -m unit

# Ejecutar solo pruebas de base de datos
pytest -m database

# Excluir pruebas lentas
pytest -m "not slow"
```

### Ejemplo de uso de markers en pruebas

```python
import pytest


@pytest.mark.unit
def test_simple_calculation():
    """Prueba unitaria simple."""
    assert 2 + 2 == 4


@pytest.mark.database
def test_database_query(test_db):
    """Prueba que requiere base de datos."""
    # ...


@pytest.mark.slow
def test_complex_operation():
    """Prueba que toma mucho tiempo."""
    # ...
```

---

## Cobertura de Código

La cobertura de código mide qué porcentaje del código está siendo probado.

### Generar Reporte de Cobertura

```bash
# Ejecutar pruebas con cobertura
pytest --cov=src

# Generar reporte detallado
pytest --cov=src --cov-report=html

# Generar reporte en terminal
pytest --cov=src --cov-report=term-missing

# Especificar porcentaje mínimo de cobertura
pytest --cov=src --cov-fail-under=80
```

### Configurar cobertura en pytest.ini

```ini
[pytest]
addopts = 
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
```

---

## Mejores Prácticas

### 1. Nomenclatura Clara

```python
# ✅ Bueno: nombre descriptivo
def test_product_creation_with_valid_data():
    pass

# ❌ Malo: nombre vago
def test_product():
    pass
```

### 2. Una Afirmación por Prueba (cuando sea posible)

```python
# ✅ Bueno
def test_product_name():
    product = create_product()
    assert product.name == "Test Product"

def test_product_price():
    product = create_product()
    assert product.price == 100.0

# ⚠️ Aceptable en algunos casos
def test_product_creation():
    product = create_product()
    assert product.name == "Test Product"
    assert product.price == 100.0
    assert product.is_active is True
```

### 3. Usar Fixtures para Datos Comunes

```python
# ✅ Bueno: usar fixtures
def test_product_update(sample_product):
    sample_product.name = "Updated Name"
    sample_product.save()
    assert sample_product.name == "Updated Name"

# ❌ Malo: crear datos en cada prueba
def test_product_update():
    product = Product.create(name="Test", price=100, ...)
    product.name = "Updated Name"
    product.save()
    assert product.name == "Updated Name"
```

### 4. Independencia de Pruebas

Cada prueba debe ser independiente y no depender del orden de ejecución.

```python
# ✅ Bueno: cada prueba crea sus propios datos
def test_delete_product(test_db):
    product = Product.create(name="Test", ...)
    product.delete_instance()
    assert Product.select().count() == 0

# ❌ Malo: depende de datos de otra prueba
def test_delete_product():
    # Asume que ya existe un producto
    product = Product.get()
    product.delete_instance()
```

### 5. Probar Casos Límite y Errores

```python
def test_product_with_empty_name(test_db, sample_category):
    """Prueba que no se puede crear producto sin nombre."""
    with pytest.raises(ValueError):
        Product.create(name="", price=100, category=sample_category)

def test_product_with_negative_price(test_db, sample_category):
    """Prueba que no se puede crear producto con precio negativo."""
    with pytest.raises(ValueError):
        Product.create(name="Test", price=-10, category=sample_category)
```

---

## Ejemplos Específicos del Proyecto

### Ejemplo 1: Prueba de Categoría

```python
# tests/test_models/test_category.py
import pytest
from models.category import Category


class TestCategory:
    """Pruebas para el modelo Category."""
    
    def test_create_category(self, test_db):
        """Prueba crear una categoría."""
        category = Category.create(
            name="Alimentos",
            description="Productos alimenticios"
        )
        
        assert category.name == "Alimentos"
        assert category.description == "Productos alimenticios"
    
    def test_category_unique_name(self, test_db, sample_category):
        """Prueba que el nombre de categoría es único."""
        with pytest.raises(Exception):
            Category.create(
                name=sample_category.name,  # Nombre duplicado
                description="Otra descripción"
            )
```

### Ejemplo 2: Prueba de Batch

```python
# tests/test_models/test_batch.py
import pytest
from datetime import datetime, timedelta
from models.batch import Batch


class TestBatch:
    """Pruebas para el modelo Batch."""
    
    def test_create_batch(self, test_db, sample_product):
        """Prueba crear un lote."""
        batch = Batch.create(
            product=sample_product,
            quantity=100,
            acquisition_date=datetime.now(),
            expiration_date=datetime.now() + timedelta(days=365)
        )
        
        assert batch.quantity == 100
        assert batch.product == sample_product
    
    def test_batch_expiration(self, test_db, sample_product):
        """Prueba verificar si un lote está vencido."""
        # Crear lote vencido
        expired_batch = Batch.create(
            product=sample_product,
            quantity=50,
            acquisition_date=datetime.now() - timedelta(days=400),
            expiration_date=datetime.now() - timedelta(days=1)
        )
        
        assert expired_batch.expiration_date < datetime.now()
```

### Ejemplo 3: Prueba de Ventas

```python
# tests/test_controllers/test_sales_controller.py
import pytest
from controllers.sales_controller import register_sale, get_sales_report


class TestSalesController:
    """Pruebas para el controlador de ventas."""
    
    def test_register_sale(self, test_db, sample_product, sample_batch):
        """Prueba registrar una venta."""
        # Arrange
        sale_items = [
            {
                'product_id': sample_product.id,
                'quantity': 2,
                'unit_price': sample_product.price
            }
        ]
        
        # Act
        sale = register_sale(sale_items)
        
        # Assert
        assert sale is not None
        assert sale.total > 0
    
    def test_sale_reduces_stock(self, test_db, sample_product, sample_batch):
        """Prueba que una venta reduce el stock."""
        # Arrange
        initial_stock = sample_batch.quantity
        quantity_sold = 3
        
        # Act
        sale_items = [{
            'product_id': sample_product.id,
            'quantity': quantity_sold,
            'unit_price': sample_product.price
        }]
        register_sale(sale_items)
        
        # Assert
        sample_batch = Batch.get_by_id(sample_batch.id)
        assert sample_batch.quantity == initial_stock - quantity_sold
```

---

## Comandos Útiles de Referencia Rápida

```bash
# Instalación
pip install pytest pytest-cov pytest-mock

# Ejecutar todas las pruebas
pytest

# Ejecutar con verbose
pytest -v

# Ejecutar archivo específico
pytest tests/test_models/test_product.py

# Ejecutar prueba específica
pytest tests/test_models/test_product.py::test_create_product

# Ejecutar con cobertura
pytest --cov=src --cov-report=html

# Ejecutar solo pruebas que fallaron
pytest --lf

# Ejecutar con output de print
pytest -s

# Ejecutar con markers
pytest -m unit
pytest -m "not slow"

# Ver fixtures disponibles
pytest --fixtures

# Generar reporte JUnit XML
pytest --junitxml=report.xml
```

---

## Recursos Adicionales

- **Documentación oficial de pytest**: https://docs.pytest.org/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **pytest-mock**: https://pytest-mock.readthedocs.io/
- **Real Python - Testing**: https://realpython.com/pytest-python-testing/

---

## Conclusión

Esta guía cubre los aspectos fundamentales para implementar pruebas unitarias con pytest en tu proyecto. Recuerda:

1. **Escribe pruebas desde el principio**: No esperes a terminar todo el código
2. **Mantén las pruebas simples**: Una prueba debe probar una sola cosa
3. **Usa fixtures**: Reutiliza código de configuración
4. **Busca alta cobertura**: Apunta a al menos 70-80% de cobertura
5. **Ejecuta las pruebas frecuentemente**: Idealmente antes de cada commit

¡Buena suerte con tus pruebas! 🚀
