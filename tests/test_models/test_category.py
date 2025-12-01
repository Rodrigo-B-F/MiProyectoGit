"""
Pruebas unitarias para el modelo Category.
"""

import pytest
from models.category import Category
from peewee import IntegrityError


@pytest.mark.unit
@pytest.mark.database
class TestCategory:
    """Pruebas para el modelo Category."""
    
    def test_create_category(self, test_db):
        """Prueba crear una categoría básica."""
        # Arrange & Act
        category = Category.create(
            name="Bebidas",
            description="Bebidas y refrescos"
        )
        
        # Assert
        assert category.id is not None
        assert category.name == "Bebidas"
        assert category.description == "Bebidas y refrescos"
    
    def test_create_category_without_description(self, test_db):
        """Prueba crear una categoría sin descripción."""
        # Arrange & Act
        category = Category.create(
            name="Limpieza",
            description=None
        )
        
        # Assert
        assert category.id is not None
        assert category.name == "Limpieza"
        assert category.description is None
    
    def test_category_unique_name(self, test_db, sample_category):
        """Prueba que el nombre de categoría debe ser único."""
        # Act & Assert
        with pytest.raises(IntegrityError):
            Category.create(
                name=sample_category.name,  # Nombre duplicado
                description="Otra descripción"
            )
    
    def test_list_all_categories(self, test_db, sample_category, sample_category_2):
        """Prueba listar todas las categorías."""
        # Act
        categories = list(Category.select())
        
        # Assert
        assert len(categories) == 2
        assert sample_category in categories
        assert sample_category_2 in categories
    
    def test_update_category(self, test_db, sample_category):
        """Prueba actualizar una categoría."""
        # Arrange
        new_description = "Productos tecnológicos y electrónicos"
        
        # Act
        sample_category.description = new_description
        sample_category.save()
        
        # Assert
        updated_category = Category.get_by_id(sample_category.id)
        assert updated_category.description == new_description
    
    def test_delete_category(self, test_db, sample_category):
        """Prueba eliminar una categoría."""
        # Arrange
        category_id = sample_category.id
        
        # Act
        sample_category.delete_instance()
        
        # Assert
        with pytest.raises(Category.DoesNotExist):
            Category.get_by_id(category_id)
    
    def test_category_with_products(self, test_db, sample_category, sample_product):
        """Prueba que una categoría puede tener productos asociados."""
        # Act
        products = list(sample_category.products)
        
        # Assert
        assert len(products) == 1
        assert products[0] == sample_product
