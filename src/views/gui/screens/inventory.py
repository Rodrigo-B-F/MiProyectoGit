"""
Inventory Screen
Manage stock levels and add stock
"""

import tkinter as tk
from tkinter import messagebox
from ..components import Card, ModernTable, StyledButton, FormField, StyledLabel, StyledEntry
from ..styles import COLORS, FONTS, SPACING
from controllers import (
    list_products_inventory,
    add_stock,
    find_product_by_name_or_barcode,
    list_categories,
    list_products_by_category
)
from utils.translations import PRODUCT_FIELDS


class InventoryScreen(tk.Frame):
    """Inventory management screen"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        # Title
        title = StyledLabel(self, text="Gestion de Inventario", style='title')
        title.pack(anchor='w', padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Main container
        main_container = tk.Frame(self, bg=COLORS['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=SPACING['lg'], pady=SPACING['md'])
        
        # Left side - Inventory table
        left_frame = tk.Frame(main_container, bg=COLORS['bg_primary'])
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, SPACING['sm']))
        
        # Search field with filter button
        search_frame = tk.Frame(left_frame, bg=COLORS['bg_primary'])
        search_frame.pack(fill='x', pady=(0, SPACING['md']))
        
        # Search field container
        search_container = tk.Frame(search_frame, bg=COLORS['bg_primary'])
        search_container.pack(side='left', fill='both', expand=True, padx=(0, SPACING['sm']))
        
        # Label
        search_label = StyledLabel(search_container, text="Buscar Producto", style='body_bold')
        search_label.pack(anchor='w')
        
        # Entry field (same height as button)
        self.search_entry = StyledEntry(search_container, placeholder="Nombre, codigo o categoria...")
        self.search_entry.pack(fill='x', ipady=6)
        
        # Bind KeyRelease event for real-time search
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_products())
        
        # Action buttons (aligned to bottom)
        button_container = tk.Frame(search_frame, bg=COLORS['bg_primary'])
        button_container.pack(side='right', anchor='s')
        
        StyledButton(button_container, "Ajustar", style='secondary',
                    command=self.adjust_columns, width=8).pack(side='left', padx=(0, SPACING['xs']))
        self.filter_button = StyledButton(button_container, "Filtrar", style='primary',
                    command=self.show_filter_menu, width=8)
        self.filter_button.pack(side='left')
        
        # Inventory table
        table_card = Card(left_frame, title="Niveles de Stock")
        table_card.pack(fill='both', expand=True)
        
        columns = {
            'name': PRODUCT_FIELDS['name'],
            'barcode': PRODUCT_FIELDS['barcode'],
            'category_name': PRODUCT_FIELDS['category_name'],
            'quantity': PRODUCT_FIELDS['quantity'],
            'location': PRODUCT_FIELDS['location'],
        }
        
        self.table = ModernTable(table_card.content, columns, height=20)
        self.table.pack(fill='both', expand=True)
        
        # Right side - Add stock form
        right_frame = tk.Frame(main_container, bg=COLORS['bg_primary'], width=365)
        right_frame.pack(side='right', fill='y')
        right_frame.pack_propagate(False)
        
        form_card = Card(right_frame, title="Agregar Stock")
        form_card.pack(fill='both')
        
        # Form fields
        self.barcode_field = FormField(form_card.content, "Codigo de Barras", 
                                      placeholder="Codigo del producto")
        self.barcode_field.pack(fill='x', pady=SPACING['sm'])
        
        self.quantity_field = FormField(form_card.content, "Cantidad a Agregar", 
                                       placeholder="0")
        self.quantity_field.pack(fill='x', pady=SPACING['sm'])
        
        # Buttons
        btn_frame = tk.Frame(form_card.content, bg=COLORS['bg_secondary'])
        btn_frame.pack(fill='x', pady=SPACING['md'])
        
        StyledButton(btn_frame, "Agregar Stock", style='success', 
                    command=self.add_stock_action).pack(fill='x', pady=SPACING['xs'])
        StyledButton(btn_frame, "Limpiar", style='secondary', 
                    command=self.clear_form).pack(fill='x', pady=SPACING['xs'])
        
        # Load initial data
        self.load_inventory()
    
    def load_inventory(self):
        """Load inventory data"""
        products = list_products_inventory(1) or []
        self.table.insert_data(products)
    
    def search_products(self):
        """Search products in real-time"""
        query = self.search_entry.get_value().strip()
        if query:
            results = find_product_by_name_or_barcode(query) or []
            self.table.insert_data(results)
        else:
            self.load_inventory()
    
    def show_filter_menu(self):
        """Show category filter dropdown menu"""
        # Create dropdown menu
        menu = tk.Menu(self, tearoff=0, 
                      bg=COLORS['bg_secondary'],
                      fg=COLORS['text_primary'],
                      activebackground=COLORS['primary'],
                      activeforeground=COLORS['text_white'],
                      font=FONTS['body'])
        
        # Add "Todas" option
        menu.add_command(label="Todas las Categorias", 
                        command=lambda: self.filter_by_category(None))
        
        menu.add_separator()
        
        # Get and add categories
        categories = list_categories() or []
        
        if categories:
            for cat in categories:
                menu.add_command(label=cat['name'], 
                               command=lambda c=cat['id']: self.filter_by_category(c))
        else:
            menu.add_command(label="No hay categorias", state='disabled')
        
        # Show menu below the Filtrar button
        x = self.filter_button.winfo_rootx()
        y = self.filter_button.winfo_rooty() + self.filter_button.winfo_height()
        menu.post(x, y)
    
    def filter_by_category(self, category_id):
        """Filter products by category"""
        if category_id is None:
            # Show all products
            self.load_inventory()
        else:
            # Show products from selected category
            products = list_products_by_category(category_id) or []
            self.table.insert_data(products)
    
    def adjust_columns(self):
        """Adjust table columns to fit container"""
        self.table.auto_fit_columns()
    
    def add_stock_action(self):
        """Add stock to a product"""
        try:
            barcode = self.barcode_field.get_value()
            quantity = int(self.quantity_field.get_value() or 0)
            
            if not barcode:
                messagebox.showerror("Error", "Codigo de barras es obligatorio")
                return
            
            if quantity <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
            
            success, message = add_stock(barcode, quantity)
            
            if success:
                messagebox.showinfo("Exito", message)
                self.clear_form()
                self.load_inventory()
            else:
                messagebox.showerror("Error", message)
        
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un numero valido")
    
    def clear_form(self):
        """Clear form fields"""
        self.barcode_field.set_value("")
        self.quantity_field.set_value("")
    
    def refresh(self):
        """Refresh screen data"""
        self.load_inventory()
