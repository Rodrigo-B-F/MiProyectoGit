"""
Products Screen
Manage products - view, add, edit, delete
"""

import tkinter as tk
from tkinter import messagebox
from ..components import Card, ModernTable, StyledButton, FormField, StyledLabel, StyledEntry, CategoryCombobox
from ..styles import COLORS, FONTS, SPACING
from controllers import (
    list_products_inventory,
    add_product,
    update_product_details,
    find_product_by_name_or_barcode
)
from utils.translations import PRODUCT_FIELDS


class ProductsScreen(tk.Frame):
    """Products management screen"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        # Title
        title = StyledLabel(self, text="Gestion de Productos", style='title')
        title.pack(anchor='w', padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Main container
        main_container = tk.Frame(self, bg=COLORS['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=SPACING['lg'], pady=SPACING['md'])
        
        # Left side - Product list
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
        self.search_entry.pack(fill='x', ipady=6)  # ipady adds internal padding for height
        
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
        
        # Products table
        table_card = Card(left_frame, title="Lista de Productos")
        table_card.pack(fill='both', expand=True)
        
        columns = {
            'name': PRODUCT_FIELDS['name'],
            'barcode': PRODUCT_FIELDS['barcode'],
            'category_name': PRODUCT_FIELDS['category_name'],
            'quantity': PRODUCT_FIELDS['quantity'],
            'sale_price': PRODUCT_FIELDS['sale_price'],
            'location': PRODUCT_FIELDS['location'],
        }
        
        self.table = ModernTable(table_card.content, columns, height=15)
        self.table.pack(fill='both', expand=True)
        
        # Bind double-click to populate edit form
        self.table.tree.bind('<Double-Button-1>', self.on_product_double_click)
        
        # Right side - Forms with RESPONSIVE WIDTH (240px min, 400px max)
        right_frame = tk.Frame(main_container, bg=COLORS['bg_primary'])
        right_frame.pack(side='right', fill='both')
        
        # Store reference for resize handler
        self.right_frame = right_frame
        self.min_form_width = 240
        self.max_form_width = 400
        
        # Bind to main container resize to adjust form width
        def adjust_form_width(event=None):
            if event and event.widget != main_container:
                return
            
            # Get available width
            total_width = main_container.winfo_width()
            if total_width <= 1:
                return  # Not yet rendered
            
            # Calculate form width (20-30% of total, between min and max)
            desired_width = int(total_width * 0.25)
            form_width = max(self.min_form_width, min(desired_width, self.max_form_width))
            
            # Update frame width
            right_frame.config(width=form_width)
        
        main_container.bind('<Configure>', adjust_form_width)
        
        # Set initial width
        right_frame.config(width=self.min_form_width)
        right_frame.pack_propagate(False)
        
        # Tab buttons - BOTH BUTTONS IN ONE ROW
        tab_frame = tk.Frame(right_frame, bg=COLORS['bg_primary'])
        tab_frame.pack(fill='x', pady=(0, SPACING['sm']))
        
        # Make buttons fill the width equally
        self.add_tab_btn = StyledButton(tab_frame, "Agregar Producto", style='primary',
                                       command=lambda: self.switch_tab('add'))
        self.add_tab_btn.pack(side='left', fill='x', expand=True, padx=(0, SPACING['xs']))
        
        self.edit_tab_btn = StyledButton(tab_frame, "Modificar Producto", style='secondary',
                                        command=lambda: self.switch_tab('edit'))
        self.edit_tab_btn.pack(side='left', fill='x', expand=True)
        
        # Unbind default hover events and add custom ones
        self.add_tab_btn.unbind('<Enter>')
        self.add_tab_btn.unbind('<Leave>')
        self.edit_tab_btn.unbind('<Enter>')
        self.edit_tab_btn.unbind('<Leave>')
        
        # Add custom hover for tabs
        self.add_tab_btn.bind('<Enter>', lambda e: self._on_tab_hover(self.add_tab_btn, 'add'))
        self.add_tab_btn.bind('<Leave>', lambda e: self._on_tab_leave(self.add_tab_btn, 'add'))
        self.edit_tab_btn.bind('<Enter>', lambda e: self._on_tab_hover(self.edit_tab_btn, 'edit'))
        self.edit_tab_btn.bind('<Leave>', lambda e: self._on_tab_leave(self.edit_tab_btn, 'edit'))
        
        # Forms container
        self.forms_container = tk.Frame(right_frame, bg=COLORS['bg_primary'])
        self.forms_container.pack(fill='both', expand=True)
        
        # Create both forms
        self.create_add_form()
        self.create_edit_form()
        
        # Show add form by default
        self.current_tab = 'add'
        self.switch_tab('add')
        
        # Load initial data
        self.load_products()
    
    def create_add_form(self):
        """Create add product form"""
        self.add_form = tk.Frame(self.forms_container, bg=COLORS['bg_primary'])
        
        form_card = Card(self.add_form, title="Agregar Producto")
        form_card.pack(fill='both', expand=True)
        
        # Form fields
        self.name_field = FormField(form_card.content, "Nombre", placeholder="Nombre del producto")
        self.name_field.pack(fill='x', pady=SPACING['sm'])
        
        self.barcode_field = FormField(form_card.content, "Código", placeholder="Código del producto")
        self.barcode_field.pack(fill='x', pady=SPACING['sm'])
        
        self.category_combobox = CategoryCombobox(form_card.content, "Categoria")
        self.category_combobox.pack(fill='x', pady=SPACING['sm'])
        
        self.location_field = FormField(form_card.content, "Ubicacion", placeholder="Ej: Pasillo A")
        self.location_field.pack(fill='x', pady=SPACING['sm'])
        
        self.price_field = FormField(form_card.content, "Precio de Venta", placeholder="0.00")
        self.price_field.pack(fill='x', pady=SPACING['sm'])
        
        self.quantity_field = FormField(form_card.content, "Cantidad Inicial", placeholder="0")
        self.quantity_field.pack(fill='x', pady=SPACING['sm'])
        
        # Buttons - side by side
        btn_frame = tk.Frame(form_card.content, bg=COLORS['bg_secondary'])
        btn_frame.pack(fill='x', pady=SPACING['md'])
        
        StyledButton(btn_frame, "Agregar", style='success',
                    command=self.add_product).pack(side='left', fill='x', expand=True, padx=(0, SPACING['xs']))
        StyledButton(btn_frame, "Limpiar", style='secondary',
                    command=self.clear_add_form).pack(side='left', fill='x', expand=True)
    
    def create_edit_form(self):
        """Create edit product form"""
        from tkinter import ttk
        
        self.edit_form = tk.Frame(self.forms_container, bg=COLORS['bg_primary'])
        
        form_card = Card(self.edit_form, title="Modificar Producto")
        form_card.pack(fill='both', expand=True)
        
        # Name field with search button
        name_container = tk.Frame(form_card.content, bg=COLORS['bg_secondary'])
        name_container.pack(fill='x', pady=SPACING['sm'])
        
        self.edit_name_field = FormField(name_container, "Nombre", placeholder="Nombre del producto")
        self.edit_name_field.pack(side='left', fill='x', expand=True, padx=(0, SPACING['xs']))
        
        StyledButton(name_container, "🔍", style='primary', width=3,
                    command=self.search_by_name).pack(side='right')
        
        # Barcode field with search button
        barcode_container = tk.Frame(form_card.content, bg=COLORS['bg_secondary'])
        barcode_container.pack(fill='x', pady=SPACING['sm'])
        
        self.edit_barcode_field = FormField(barcode_container, "Codigo de Barras", placeholder="Codigo unico")
        self.edit_barcode_field.pack(side='left', fill='x', expand=True, padx=(0, SPACING['xs']))
        
        StyledButton(barcode_container, "🔍", style='primary', width=3,
                    command=self.search_by_barcode).pack(side='right')
        
        # Category
        self.edit_category_combobox = CategoryCombobox(form_card.content, "Categoria")
        self.edit_category_combobox.pack(fill='x', pady=SPACING['sm'])
        
        # Stock
        self.edit_stock_field = FormField(form_card.content, "Stock", placeholder="0")
        self.edit_stock_field.pack(fill='x', pady=SPACING['sm'])
        
        # Price
        self.edit_price_field = FormField(form_card.content, "Precio de Venta", placeholder="0.00")
        self.edit_price_field.pack(fill='x', pady=SPACING['sm'])
        
        # Location
        self.edit_location_field = FormField(form_card.content, "Ubicacion", placeholder="Ej: Pasillo A")
        self.edit_location_field.pack(fill='x', pady=SPACING['sm'])
        
        # Status dropdown (readonly)
        status_label = StyledLabel(form_card.content, text="Estado", style='body_bold')
        status_label.pack(anchor='w', pady=(SPACING['sm'], SPACING['xs']))
        
        self.edit_status_combo = ttk.Combobox(form_card.content, values=['Activo', 'Inactivo'],
                                             state='readonly', font=FONTS['body'])
        self.edit_status_combo.pack(fill='x', pady=(0, SPACING['sm']))
        self.edit_status_combo.set('Activo')
        
        # Buttons - side by side
        btn_frame = tk.Frame(form_card.content, bg=COLORS['bg_secondary'])
        btn_frame.pack(fill='x', pady=SPACING['md'])
        
        StyledButton(btn_frame, "Actualizar", style='success',
                    command=self.update_product).pack(side='left', fill='x', expand=True, padx=(0, SPACING['xs']))
        StyledButton(btn_frame, "Limpiar", style='secondary',
                    command=self.clear_edit_form).pack(side='left', fill='x', expand=True)
        
        # Store current product ID
        self.current_product_id = None
    
    def switch_tab(self, tab):
        """Switch between add and edit forms"""
        if tab == 'add':
            self.edit_form.pack_forget()
            self.add_form.pack(fill='both', expand=True)
            self.add_tab_btn.config(bg=COLORS['primary'], fg=COLORS['text_white'])
            self.edit_tab_btn.config(bg=COLORS['bg_secondary'], fg=COLORS['text_primary'])
        else:  # edit
            self.add_form.pack_forget()
            self.edit_form.pack(fill='both', expand=True)
            self.add_tab_btn.config(bg=COLORS['bg_secondary'], fg=COLORS['text_primary'])
            self.edit_tab_btn.config(bg=COLORS['primary'], fg=COLORS['text_white'])
        
        self.current_tab = tab
    
    def _on_tab_hover(self, button, tab):
        """Handle tab button hover - only for inactive tabs"""
        if self.current_tab != tab:
            # Darken inactive tab on hover
            button.config(bg='#d0d0d0')  # Slightly darker gray
    
    def _on_tab_leave(self, button, tab):
        """Handle tab button leave - restore colors"""
        if self.current_tab == tab:
            # Active tab stays primary color
            button.config(bg=COLORS['primary'])
        else:
            # Inactive tab returns to secondary color
            button.config(bg=COLORS['bg_secondary'])
    
    def load_products(self):
        """Load all products into the table"""
        products = list_products_inventory(1) or []
        self.table.insert_data(products)
    
    def on_product_double_click(self, event):
        """Handle double-click on product row - populate edit form if edit tab is active"""
        # Only work if edit tab is active
        if self.current_tab != 'edit':
            return
        
        # Check if click was in the cell region (not heading)
        region = self.table.tree.identify_region(event.x, event.y)
        if region != 'cell':
            return
        
        # Check if click was on an actual row (not empty space)
        row_id = self.table.tree.identify_row(event.y)
        if not row_id:
            return
        
        # Get selected item
        selection = self.table.tree.selection()
        if not selection:
            return
        
        # Get item values
        item = self.table.tree.item(selection[0])
        values = item['values']
        
        if not values or len(values) < 2:
            return
        
        # Extract product name and barcode from table
        product_name = values[0]  # NOMBRE column
        product_barcode = str(values[1])  # CÓDIGO column - convert to string
        
        # Search for product by barcode (includes inactive products for editing)
        from controllers import find_product_for_edit
        results = find_product_for_edit(product_barcode)
        
        if results and len(results) > 0:
            # Populate edit form with first result
            product = results[0]
            self.populate_edit_form(product)
        else:
            messagebox.showerror("Error", f"No se pudo cargar el producto: {product_name}")
    
    def search_products(self):
        """Search products in real-time"""
        query = self.search_entry.get_value().strip()
        if query:
            # Search by name or barcode (controller already searches both)
            results = find_product_by_name_or_barcode(query) or []
            self.table.insert_data(results)
        else:
            self.load_products()
    
    def search_by_name(self):
        """Search product by name and populate edit form"""
        from controllers import find_product_for_edit
        
        name = self.edit_name_field.get_value().strip()
        if not name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para buscar")
            return
        
        results = find_product_for_edit(name)  # Includes inactive products
        if results and len(results) > 0:
            # Take first result
            product = results[0]
            self.populate_edit_form(product)
        else:
            messagebox.showerror("Error", f"No se encontro producto con nombre: {name}")
    
    def search_by_barcode(self):
        """Search product by barcode and populate edit form"""
        from controllers import find_product_for_edit
        
        barcode = self.edit_barcode_field.get_value().strip()
        if not barcode:
            messagebox.showwarning("Advertencia", "Ingrese un codigo de barras para buscar")
            return
        
        results = find_product_for_edit(barcode)  # Includes inactive products
        if results and len(results) > 0:
            # Take first result
            product = results[0]
            self.populate_edit_form(product)
        else:
            messagebox.showerror("Error", f"No se encontro producto con codigo: {barcode}")
    
    def populate_edit_form(self, product):
        """Populate edit form with product data"""
        self.current_product_id = product['id']
        
        # Populate all fields
        self.edit_name_field.set_value(product['name'])
        self.edit_barcode_field.set_value(product['barcode'])
        self.edit_category_combobox.set_value(product['category_name'])
        self.edit_stock_field.set_value(str(product['quantity']))
        self.edit_price_field.set_value(str(product['sale_price']))
        self.edit_location_field.set_value(product['location'] or '')
        
        # Set status
        status = 'Activo' if product['active'] else 'Inactivo'
        self.edit_status_combo.set(status)
    
    def update_product(self):
        """Update product with edit form data"""
        if not self.current_product_id:
            messagebox.showerror("Error", "Primero busque un producto para modificar")
            return
        
        try:
            # Get values
            name = self.edit_name_field.get_value()
            barcode = self.edit_barcode_field.get_value()
            category = self.edit_category_combobox.get_value()
            new_stock = int(self.edit_stock_field.get_value() or 0)
            price = float(self.edit_price_field.get_value() or 0)
            location = self.edit_location_field.get_value()
            status = self.edit_status_combo.get() == 'Activo'
            
            if not name or not barcode:
                messagebox.showerror("Error", "Nombre y codigo de barras son obligatorios")
                return
            
            # Update product details
            success, message = update_product_details(
                self.current_product_id,
                name=name,
                new_barcode=barcode,
                category_name=category,
                location=location,
                sale_price=price,
                active_status=status
            )
            
            if success:
                # Update stock if needed
                self.update_stock(self.current_product_id, new_stock)
                
                messagebox.showinfo("Exito", "Producto actualizado correctamente")
                self.load_products()
                self.clear_edit_form()
            else:
                messagebox.showerror("Error", message)
        
        except ValueError:
            messagebox.showerror("Error", "Stock y precio deben ser numeros validos")
    
    def update_stock(self, product_id, new_quantity):
        """Update product stock directly"""
        from models import db, Product, Inventory, StockMovement
        import datetime
        
        try:
            if db.is_closed():
                db.connect()
            
            with db.atomic():
                product = Product.get_by_id(product_id)
                inventory = Inventory.get(Inventory.product == product)
                
                # Calculate change
                old_quantity = inventory.quantity
                change = new_quantity - old_quantity
                
                if change != 0:
                    # Update inventory
                    inventory.quantity = new_quantity
                    inventory.last_updated = datetime.datetime.now()
                    inventory.save()
                    
                    # Create stock movement record
                    reason = 'stock_correction' if change < 0 else 'stock_adjustment'
                    reference = f'Ajuste manual: {old_quantity} -> {new_quantity}'
                    
                    StockMovement.create(
                        product=product,
                        change=change,
                        reason=reason,
                        reference=reference
                    )
        
        except Exception as e:
            print(f"Error al actualizar stock: {e}")
        
        finally:
            if not db.is_closed():
                db.close()
    
    def add_product(self):
        """Add new product"""
        try:
            name = self.name_field.get_value()
            barcode = self.barcode_field.get_value()
            category = self.category_combobox.get_value()
            location = self.location_field.get_value()
            price = float(self.price_field.get_value() or 0)
            quantity = int(self.quantity_field.get_value() or 0)
            
            if not name or not barcode:
                messagebox.showerror("Error", "Nombre y codigo de barras son obligatorios")
                return
            
            success, message = add_product(name, barcode, category, location, price, quantity)
            
            if success:
                messagebox.showinfo("Exito", message)
                self.clear_add_form()
                self.load_products()
            else:
                messagebox.showerror("Error", message)
        
        except ValueError:
            messagebox.showerror("Error", "Precio y cantidad deben ser numeros validos")
    
    def clear_add_form(self):
        """Clear add product form"""
        self.name_field.set_value("")
        self.barcode_field.set_value("")
        self.category_combobox.set_value("")
        self.location_field.set_value("")
        self.price_field.set_value("")
        self.quantity_field.set_value("")
    
    def clear_edit_form(self):
        """Clear edit form - only name and barcode, others become empty"""
        self.edit_name_field.set_value("")
        self.edit_barcode_field.set_value("")
        self.edit_category_combobox.set_value("")
        self.edit_stock_field.set_value("")
        self.edit_price_field.set_value("")
        self.edit_location_field.set_value("")
        self.edit_status_combo.set('')  # Empty instead of 'Activo'
        self.current_product_id = None
    
    def show_filter_menu(self):
        """Show category filter dropdown menu"""
        from controllers import list_categories
        
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
        
        # Add "Activos" option
        menu.add_command(label="Activos", 
                        command=lambda: self.filter_by_category("active"))
        
        # Add "Inactivos" option
        menu.add_command(label="Inactivos", 
                        command=lambda: self.filter_by_category("inactive"))
        
        # Add "Sin Categoría" option
        menu.add_command(label="Sin Categoría", 
                        command=lambda: self.filter_by_category("no_category"))
        
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
        """Filter products by category or status"""
        from controllers import list_products_by_category, list_products_without_category, list_products_inventory
        
        if category_id is None:
            # Show all products
            self.load_products()
        elif category_id == "active":
            # Show only active products
            products = list_products_inventory(1) or []  # 1 = active
            self.table.insert_data(products)
        elif category_id == "inactive":
            # Show only inactive products
            products = list_products_inventory(0) or []  # 0 = inactive
            self.table.insert_data(products)
        elif category_id == "no_category":
            # Show products without category
            products = list_products_without_category() or []
            self.table.insert_data(products)
        else:
            # Show products from selected category
            products = list_products_by_category(category_id) or []
            self.table.insert_data(products)
    
    def adjust_columns(self):
        """Adjust table columns to fit container"""
        self.table.auto_fit_columns()
    
    def refresh(self):
        """Refresh screen data"""
        self.load_products()
