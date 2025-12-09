"""
Categories Screen
View and manage product categories
"""

import tkinter as tk
from tkinter import messagebox
from ..components import Card, ModernTable, StyledButton, FormField, StyledLabel, StyledEntry
from ..styles import COLORS, FONTS, SPACING
from controllers import (
    list_categories,
    update_category,
    delete_category
)


class CategoriesScreen(tk.Frame):
    """Categories management screen"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        # Title
        title = StyledLabel(self, text="Gestion de Categorias", style='title')
        title.pack(anchor='w', padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Main container
        main_container = tk.Frame(self, bg=COLORS['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=SPACING['lg'], pady=SPACING['md'])
        
        # Left side - Categories table
        left_frame = tk.Frame(main_container, bg=COLORS['bg_primary'])
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, SPACING['sm']))
        
        # Search field with adjust button
        search_frame = tk.Frame(left_frame, bg=COLORS['bg_primary'])
        search_frame.pack(fill='x', pady=(0, SPACING['md']))
        
        # Search field container
        search_container = tk.Frame(search_frame, bg=COLORS['bg_primary'])
        search_container.pack(side='left', fill='both', expand=True, padx=(0, SPACING['sm']))
        
        # Label
        search_label = StyledLabel(search_container, text="Buscar Categoria", style='body_bold')
        search_label.pack(anchor='w')
        
        # Entry field
        self.search_entry = StyledEntry(search_container, placeholder="Nombre o descripcion...")
        self.search_entry.pack(fill='x', ipady=6)
        
        # Bind KeyRelease event for real-time search
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_categories())
        
        # Adjust button (aligned to bottom)
        button_container = tk.Frame(search_frame, bg=COLORS['bg_primary'])
        button_container.pack(side='right', anchor='s')
        
        StyledButton(button_container, "Ajustar", style='secondary',
                    command=self.adjust_columns, width=8).pack(side='left')
        
        # Categories table
        table_card = Card(left_frame, title="Lista de Categorias")
        table_card.pack(fill='both', expand=True)
        
        columns = {
            'name': 'NOMBRE',
            'description': 'DESCRIPCION',
        }
        
        self.table = ModernTable(table_card.content, columns, height=20)
        self.table.pack(fill='both', expand=True)
        
        # Configure column widths
        self.table.tree.column('name', width=140, minwidth=100)
        self.table.tree.column('description', width=665, minwidth=300)
        
        # Bind row selection
        self.table.tree.bind('<<TreeviewSelect>>', self.on_category_select)
        
        # Right side - Edit form
        right_frame = tk.Frame(main_container, bg=COLORS['bg_primary'], width=365)
        right_frame.pack(side='right', fill='y')
        right_frame.pack_propagate(False)
        
        edit_card = Card(right_frame, title="Editar Categoria")
        edit_card.pack(fill='both', expand=True)
        
        # Store current category ID
        self.current_category_id = None
        
        # Name field
        self.name_field = FormField(edit_card.content, "Nombre", placeholder="Nombre de categoria")
        self.name_field.pack(fill='x', pady=SPACING['sm'])
        
        # Description field
        desc_label = StyledLabel(edit_card.content, text="Descripcion", style='body_bold')
        desc_label.pack(anchor='w', pady=(SPACING['sm'], SPACING['xs']))
        
        self.desc_text = tk.Text(edit_card.content, height=6, font=FONTS['body'],
                                bg=COLORS['bg_primary'], fg=COLORS['text_primary'],
                                relief='solid', borderwidth=1, wrap='word')
        self.desc_text.pack(fill='x', pady=SPACING['sm'])
        
        # Buttons frame
        buttons_frame = tk.Frame(edit_card.content, bg=COLORS['bg_secondary'])
        buttons_frame.pack(fill='x', pady=SPACING['md'])
        
        # Update button
        StyledButton(buttons_frame, "Actualizar", style='primary',
                    command=self.update_category_data).pack(fill='x', pady=SPACING['xs'])
        
        # Delete button
        StyledButton(buttons_frame, "Eliminar", style='danger',
                    command=self.confirm_delete).pack(fill='x', pady=SPACING['xs'])
        
        # Info text
        info_text = tk.Label(edit_card.content,
                            text="Selecciona una categoria de la tabla\n"
                                 "para editar o eliminar.",
                            font=FONTS['small'],
                            bg=COLORS['bg_secondary'],
                            fg=COLORS['text_secondary'],
                            justify='left')
        info_text.pack(anchor='w', pady=SPACING['md'])
        
        # Load initial data
        self.load_categories()
    
    def load_categories(self):
        """Load all categories"""
        categories = list_categories() or []
        
        # Format data: remove ID from display and replace None with "Sin descripción"
        formatted_categories = []
        for cat in categories:
            formatted_cat = {
                'id': cat.get('id'),  # Keep for internal use
                'name': cat.get('name', ''),
                'description': cat.get('description') if cat.get('description') else 'Sin descripción'
            }
            formatted_categories.append(formatted_cat)
        
        self.table.insert_data(formatted_categories)
        # Store all categories for search
        self.all_categories = formatted_categories
    
    def search_categories(self):
        """Search categories in real-time"""
        query = self.search_entry.get_value().strip().lower()
        if query:
            # Filter categories by name or description
            filtered = [
                cat for cat in self.all_categories
                if query in cat.get('name', '').lower() or 
                   query in cat.get('description', '').lower()
            ]
            self.table.insert_data(filtered)
        else:
            self.table.insert_data(self.all_categories)
    
    def adjust_columns(self):
        """Reset table columns to default widths"""
        self.table.tree.column('name', width=140)
        self.table.tree.column('description', width=665)
    
    def on_category_select(self, event):
        """Handle category selection from table"""
        selection = self.table.tree.selection()
        if not selection:
            return
        
        # Get selected item
        item = self.table.tree.item(selection[0])
        values = item['values']
        
        if values:
            # Find the category in all_categories by name
            name = values[0]  # First column is now name
            description = values[1] if len(values) > 1 else ""
            
            # Find ID from stored categories
            for cat in self.all_categories:
                if cat['name'] == name:
                    self.current_category_id = cat['id']
                    break
            
            # Populate form
            self.name_field.set_value(name)
            self.desc_text.delete('1.0', tk.END)
            if description and description != "Sin descripción":
                self.desc_text.insert('1.0', description)
    
    def update_category_data(self):
        """Update category with form data"""
        if not self.current_category_id:
            messagebox.showerror("Error", "Selecciona una categoria primero")
            return
        
        try:
            new_name = self.name_field.get_value()
            new_description = self.desc_text.get('1.0', tk.END).strip()
            
            if not new_name:
                messagebox.showerror("Error", "El nombre no puede estar vacio")
                return
            
            # Update category
            success, message = update_category(
                self.current_category_id,
                name=new_name,
                description=new_description if new_description else None
            )
            
            if success:
                messagebox.showinfo("Exito", "Categoria actualizada correctamente")
                self.load_categories()
                self.clear_form()
            else:
                messagebox.showerror("Error", message)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def confirm_delete(self):
        """Show confirmation dialog before deleting"""
        if not self.current_category_id:
            messagebox.showerror("Error", "Selecciona una categoria primero")
            return
        
        # Get category name
        category_name = self.name_field.get_value()
        
        result = messagebox.askquestion(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar la categoría '{category_name}'?\n\n"
            "ADVERTENCIA: Los productos asociados a esta categoría\n"
            "quedarán sin categoría asignada.",
            icon='warning'
        )
        
        if result == 'yes':
            self.delete_category_data()
    
    def delete_category_data(self):
        """Delete category"""
        try:
            success, message = delete_category(self.current_category_id)
            
            if success:
                messagebox.showinfo("Éxito", message)
                self.load_categories()
                self.clear_form()
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
    
    def clear_form(self):
        """Clear edit form"""
        self.current_category_id = None
        self.name_field.set_value("")
        self.desc_text.delete('1.0', tk.END)
    
    def refresh(self):
        """Refresh screen data"""
        self.load_categories()
