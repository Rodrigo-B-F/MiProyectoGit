"""
Módulo de gestión de categorías.
Contiene funciones para listar, actualizar y eliminar categorías.
"""

from models import db, Category

def list_categories():
    """
    Lista todas las categorías existentes.
    """
    try:
        db.connect()
        categories = Category.select()
        return [{"id": c.id, "name": c.name, "description": c.description} for c in categories]
    except Exception as e:
        print(f"Error al listar categorías: {e}")
        return []
    finally:
        if not db.is_closed():
            db.close()

def update_category(category_id, name, description):
    """
    Actualiza una categoría.
    """
    try:
        db.connect()
        category = Category.get_by_id(category_id)
        category.name = name
        category.description = description
        category.save()
        return True, "Categoría actualizada."
    except Category.DoesNotExist:
        return False, "Categoría no encontrada."
    except Exception as e:
        return False, f"Error al actualizar categoría: {e}"
    finally:
        if not db.is_closed():
            db.close()

def delete_category(category_id):
    """
    Elimina una categoría.
    Los productos asociados quedarán sin categoría (NULL).
    """
    try:
        db.connect()
        category = Category.get_by_id(category_id)
        category_name = category.name
        category.delete_instance()
        return True, f"Categoría '{category_name}' eliminada correctamente."
    except Category.DoesNotExist:
        return False, "Categoría no encontrada."
    except Exception as e:
        return False, f"Error al eliminar categoría: {e}"
    finally:
        if not db.is_closed():
            db.close()
