"""
Conftest for pytest - Test fixtures and configuration
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models import db, Product, Category, Inventory, Sale, SaleItem


@pytest.fixture(scope='function')
def test_db():
    """Create a test database for each test"""
    # Use in-memory database for tests
    db.init(':memory:')
    
    # Ensure database is not connected before connecting
    if not db.is_closed():
        db.close()
    
    db.connect()
    db.create_tables([Product, Category, Inventory, Sale, SaleItem])
    
    yield db
    
    # Clean up
    db.drop_tables([Product, Category, Inventory, Sale, SaleItem])
    if not db.is_closed():
        db.close()


@pytest.fixture
def sample_category(test_db):
    """Create a sample category"""
    category = Category.create(
        name="Lácteos",
        description="Productos lácteos"
    )
    return category


@pytest.fixture
def sample_product(test_db, sample_category):
    """Create a sample product"""
    product = Product.create(
        name="Leche Descremada 1L",
        barcode="7501234567",
        category=sample_category,
        sale_price=25.50,
        location="Estante A1",
        active=True
    )
    return product


@pytest.fixture
def sample_inventory(test_db, sample_product):
    """Create sample inventory"""
    inventory = Inventory.create(
        product=sample_product,
        quantity=50,
        location="Estante A1"
    )
    # Close connection so controller functions can open it
    if not test_db.is_closed():
        test_db.close()
    return inventory
