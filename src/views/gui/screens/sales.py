"""
Sales Screen
Process sales and view sales history with cart table
"""

import tkinter as tk
from tkinter import messagebox, ttk
from ..components import Card, ModernTable, StyledButton, FormField, StyledLabel
from ..styles import COLORS, FONTS, SPACING
from controllers import (
    record_sale,
    list_sales_history,
    find_product_by_name_or_barcode
)
from utils.translations import PRODUCT_FIELDS


class SalesScreen(tk.Frame):
    """Sales management screen"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        # Title
        title = StyledLabel(self, text="Gestion de Ventas", style='title')
        title.pack(anchor='w', padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Main container
        main_container = tk.Frame(self, bg=COLORS['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=SPACING['lg'], pady=SPACING['md'])
        
        # Left side - Sales form with RESPONSIVE WIDTH (240px min, 400px max)
        left_frame = tk.Frame(main_container, bg=COLORS['bg_primary'])
        left_frame.pack(side='left', fill='both', padx=(0, SPACING['sm']))
        
        # Store reference for resize handler
        self.left_frame = left_frame
        self.min_form_width = 240
        self.max_form_width = 400
        
        # Bind to main container resize to adjust form width
        def adjust_form_width(event=None):
            if event and event.widget != main_container:
                return
            
            total_width = main_container.winfo_width()
            if total_width <= 1:
                return
            
            desired_width = int(total_width * 0.25)
            form_width = max(self.min_form_width, min(desired_width, self.max_form_width))
            left_frame.config(width=form_width)
        
        main_container.bind('<Configure>', adjust_form_width)
        left_frame.config(width=self.min_form_width)
        left_frame.pack_propagate(False)
        
        form_card = Card(left_frame, title="Nueva Venta")
        form_card.pack(fill='both', expand=True)
        
        # Cart items
        self.cart = []
        self.current_history_view = 'detailed'  # Track current view
        
        # Product search
        self.barcode_field = FormField(form_card.content, "Nombre/Código", 
                                      placeholder="Buscar producto...")
        self.barcode_field.pack(fill='x', pady=SPACING['sm'])
        
        # Bind KeyRelease for autocomplete
        self.barcode_field.input.bind('<KeyRelease>', self.autocomplete_product)
        
        self.quantity_field = FormField(form_card.content, "Cantidad", placeholder="0")
        self.quantity_field.pack(fill='x', pady=SPACING['sm'])
        
        # Cart display with buttons
        cart_header_frame = tk.Frame(form_card.content, bg=COLORS['bg_secondary'])
        cart_header_frame.pack(fill='x', pady=(SPACING['md'], SPACING['xs']))
        
        # Buttons side by side - expand dynamically
        btn_container = tk.Frame(cart_header_frame, bg=COLORS['bg_secondary'])
        btn_container.pack(fill='x', expand=True)
        
        StyledButton(btn_container, "Agregar al Carrito", style='primary',
                    command=self.add_to_cart).pack(side='left', fill='x', expand=True, padx=(0, SPACING['xs']))
        StyledButton(btn_container, "Ajustar", style='secondary',
                    command=self.adjust_cart_columns).pack(side='left', fill='x', expand=True)
        
        # Create Treeview for cart
        cart_container = tk.Frame(form_card.content, bg=COLORS['bg_primary'])
        cart_container.pack(fill='both', expand=True, pady=SPACING['sm'])
        
        # Scrollbars
        vsb = ttk.Scrollbar(cart_container, orient="vertical")
        vsb.pack(side='right', fill='y')
        
        hsb = ttk.Scrollbar(cart_container, orient="horizontal")
        hsb.pack(side='bottom', fill='x')
        
        # Treeview
        columns = ('producto', 'cantidad', 'precio', 'subtotal')
        self.cart_tree = ttk.Treeview(cart_container, columns=columns, show='headings',
                                      height=5, 
                                      yscrollcommand=vsb.set,
                                      xscrollcommand=hsb.set)
        
        # Configure scrollbars
        vsb.config(command=self.cart_tree.yview)
        hsb.config(command=self.cart_tree.xview)
        
        # Define headings
        self.cart_tree.heading('producto', text='PRODUCTO')
        self.cart_tree.heading('cantidad', text='CANT')
        self.cart_tree.heading('precio', text='P.UNIT')
        self.cart_tree.heading('subtotal', text='SUBTOTAL')
        
        # Define column widths
        self.cart_tree.column('producto', width=170, anchor='w')
        self.cart_tree.column('cantidad', width=65, anchor='center')
        self.cart_tree.column('precio', width=65, anchor='e')
        self.cart_tree.column('subtotal', width=110, anchor='e')
        
        self.cart_tree.pack(side='left', fill='both', expand=True)
        
        # Bind double-click to remove item (only on actual rows)
        self.cart_tree.bind('<Double-Button-1>', self.on_cart_double_click)
        
        # Total
        self.total_label = StyledLabel(form_card.content, text="Total: Bs 0.00", style='heading')
        self.total_label.pack(anchor='e', pady=SPACING['sm'])
        
        # Action buttons - side by side
        btn_frame = tk.Frame(form_card.content, bg=COLORS['bg_secondary'])
        btn_frame.pack(fill='x', pady=SPACING['sm'])
        
        StyledButton(btn_frame, "Completar", style='success',
                    command=self.complete_sale).pack(side='left', fill='x', expand=True, padx=(0, SPACING['xs']))
        StyledButton(btn_frame, "Limpiar", style='danger',
                    command=self.clear_cart).pack(side='left', fill='x', expand=True)
        
        # Right side - Sales history
        right_frame = tk.Frame(main_container, bg=COLORS['bg_primary'])
        right_frame.pack(side='right', fill='both', expand=True)
        
        # History header with toggle button
        history_header = tk.Frame(right_frame, bg=COLORS['bg_primary'])
        history_header.pack(fill='x', pady=(0, SPACING['sm']))
        
        history_label = StyledLabel(history_header, text="Historial de Ventas", style='heading')
        history_label.pack(side='left')
        
        self.history_button = StyledButton(history_header, "VER", style='primary',
                                           command=self.show_history_menu, width=12)
        self.history_button.pack(side='right')
        
        history_card = Card(right_frame, title="")
        history_card.pack(fill='both', expand=True)
        
        columns = {
            'timestamp': PRODUCT_FIELDS['timestamp'],
            'product': PRODUCT_FIELDS['product'],
            'quantity': "CANTIDAD",
            'unit_price': "P. UNIT",
            'subtotal': PRODUCT_FIELDS['subtotal']
        }
        
        self.history_table = ModernTable(history_card.content, columns, height=20)
        self.history_table.pack(fill='both', expand=True)
        
        # Configure column widths and alignment - all left aligned
        self.history_table.tree.column('timestamp', width=145, anchor='w')
        self.history_table.tree.column('product', width=230, anchor='w')
        self.history_table.tree.column('quantity', width=95, anchor='w')
        self.history_table.tree.column('unit_price', width=90, anchor='w')
        self.history_table.tree.column('subtotal', width=100, anchor='w')
        
        # Align headers to left
        self.history_table.tree.heading('timestamp', anchor='w')
        self.history_table.tree.heading('product', anchor='w')
        self.history_table.tree.heading('quantity', anchor='w')
        self.history_table.tree.heading('unit_price', anchor='w')
        self.history_table.tree.heading('subtotal', anchor='w')

        # Load sales history
        self.load_history_detailed()
    
    def add_to_cart(self):
        """Add product to cart"""
        try:
            barcode = self.barcode_field.get_value()
            quantity = int(self.quantity_field.get_value() or 1)
            
            if not barcode:
                messagebox.showerror("Error", "Ingrese un codigo de barras")
                return
            
            # Find product
            products = find_product_by_name_or_barcode(barcode)
            if not products:
                messagebox.showerror("Error", "Producto no encontrado")
                return
            
            product = products[0]
            
            # Check stock
            if product['quantity'] < quantity:
                messagebox.showerror("Error", f"Stock insuficiente. Disponible: {product['quantity']}")
                return
            
            # Check if product already exists in cart
            existing_item = None
            for item in self.cart:
                if item['barcode'] == product['barcode']:
                    existing_item = item
                    break
            
            if existing_item:
                # Sum quantities
                new_quantity = existing_item['quantity'] + quantity
                
                # Check if total quantity exceeds stock
                if product['quantity'] < new_quantity:
                    messagebox.showerror("Error", f"Stock insuficiente. Disponible: {product['quantity']}, en carrito: {existing_item['quantity']}")
                    return
                
                existing_item['quantity'] = new_quantity
            else:
                # Add new item to cart
                self.cart.append({
                    'barcode': product['barcode'],
                    'name': product['name'],
                    'quantity': quantity,
                    'price': product['sale_price']
                })
            
            self.update_cart_display()
            self.barcode_field.set_value("")
            self.quantity_field.set_value("1")
        
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser un numero valido")
        
    def autocomplete_product(self, event):
        """Provide autocomplete suggestions for product search"""
        from controllers import find_product_by_name_or_barcode
        
        # Ignore delete/backspace keys - let user delete freely
        if event.keysym in ('BackSpace', 'Delete'):
            return
        
        # Get current input
        current_input = self.barcode_field.get_value().strip()
        
        # If input is empty, return
        if not current_input:
            return
        
        # Search for products matching current input
        results = find_product_by_name_or_barcode(current_input)
        
        if results and len(results) > 0:
            # Get first match
            first_match = results[0]['name']
            
            # Check if first match starts with current input (case insensitive)
            if first_match.lower().startswith(current_input.lower()):
                # Calculate remaining part
                remaining = first_match[len(current_input):]
                
                # Get current cursor position
                cursor_pos = self.barcode_field.input.index(tk.INSERT)
                
                # Only show suggestion if cursor is at end
                if cursor_pos == len(current_input):
                    # Insert suggestion
                    self.barcode_field.input.insert(tk.END, remaining)
                    # Select the suggested part
                    self.barcode_field.input.select_range(len(current_input), tk.END)
                    self.barcode_field.input.icursor(len(current_input))

    def update_cart_display(self):
        """Update cart display"""
        # Clear treeview
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        total = 0
        
        # Add items to treeview
        for index, item in enumerate(self.cart):
            subtotal = item['quantity'] * item['price']
            total += subtotal
            
            # Truncate name if too long
            name = item['name'][:25] + "..." if len(item['name']) > 25 else item['name']
            
            self.cart_tree.insert('', 'end', iid=str(index), values=(
                name,
                item['quantity'],
                f"{item['price']:.2f}",
                f"{subtotal:.2f}"
            ))
        
        # Update total with Bs (Bolivianos)
        self.total_label.config(text=f"Total: Bs {total:.2f}")
    
    def on_cart_double_click(self, event):
        """Handle double-click on cart item to remove it"""
        # Get the item that was clicked (not just selected)
        item_id = self.cart_tree.identify_row(event.y)
        
        # Only remove if clicked on an actual row
        if item_id:
            index = int(item_id)
            self.remove_from_cart(index)
    
    def remove_from_cart(self, index):
        """Remove item from cart by index"""
        if 0 <= index < len(self.cart):
            self.cart.pop(index)
            self.update_cart_display()
    
    def complete_sale(self):
        """Complete the sale"""
        if not self.cart:
            messagebox.showerror("Error", "El carrito esta vacio")
            return
        
        # Prepare sale data
        sale_data = [{'barcode': item['barcode'], 'quantity': item['quantity']} for item in self.cart]
        
        success, message = record_sale(sale_data)
        
        if success:
            messagebox.showinfo("Exito", message)
            self.clear_cart()
            self.load_history_detailed()
        else:
            messagebox.showerror("Error", message)
    
    def clear_cart(self):
        """Clear the cart"""
        self.cart = []
        self.update_cart_display()
    
    def adjust_cart_columns(self):
        """Reset cart table columns to default widths"""
        self.cart_tree.column('producto', width=170)
        self.cart_tree.column('cantidad', width=65)
        self.cart_tree.column('precio', width=65)
        self.cart_tree.column('subtotal', width=110)
    
    def load_history_detailed(self):
        """Load detailed sales history"""
        # Update table columns for detailed view
        columns = {
            'timestamp': PRODUCT_FIELDS['timestamp'],
            'product': PRODUCT_FIELDS['product'],
            'quantity': "CANTIDAD",
            'unit_price': "P. UNIT",
            'subtotal': PRODUCT_FIELDS['subtotal']
        }
        
        # Recreate table with detailed columns
        self.history_table.destroy()
        self.history_table = ModernTable(self.history_table.master, columns, height=20)
        self.history_table.pack(fill='both', expand=True)
        
        # Configure column widths and alignment - all left aligned
        self.history_table.tree.column('timestamp', width=145, anchor='w')
        self.history_table.tree.column('product', width=230, anchor='w')
        self.history_table.tree.column('quantity', width=95, anchor='w')
        self.history_table.tree.column('unit_price', width=90, anchor='w')
        self.history_table.tree.column('subtotal', width=100, anchor='w')
        
        # Align headers to left
        self.history_table.tree.heading('timestamp', anchor='w')
        self.history_table.tree.heading('product', anchor='w')
        self.history_table.tree.heading('quantity', anchor='w')
        self.history_table.tree.heading('unit_price', anchor='w')
        self.history_table.tree.heading('subtotal', anchor='w')
        
        # Load data
        history = list_sales_history() or []
        
        # Format data for display with Bs prefix
        formatted_data = []
        for row in history:
            formatted_data.append({
                'timestamp': row['timestamp'],
                'product': row['product'],
                'quantity': row['quantity'],
                'unit_price': f"Bs {row['unit_price']:.2f}",
                'subtotal': f"Bs {row['subtotal']:.2f}"
            })
        
        self.history_table.insert_data(formatted_data)
    
    def show_history_menu(self):
        """Show history view dropdown menu"""
        # Create dropdown menu
        menu = tk.Menu(self, tearoff=0, 
                      bg=COLORS['bg_secondary'],
                      fg=COLORS['text_primary'],
                      activebackground=COLORS['primary'],
                      activeforeground=COLORS['text_white'],
                      font=FONTS['body'])
        
        menu.add_command(label="Detallado", 
                        command=lambda: self.switch_history_view('detailed'))
        menu.add_command(label="Por Fecha", 
                        command=lambda: self.switch_history_view('date'))
        
        # Show menu below button
        x = self.history_button.winfo_rootx()
        y = self.history_button.winfo_rooty() + self.history_button.winfo_height()
        menu.post(x, y)
    
    def switch_history_view(self, view_type):
        """Switch between detailed and date-grouped history views"""
        self.current_history_view = view_type
        
        if view_type == 'detailed':
            self.load_history_detailed()
        else:
            self.load_history_by_date()
    
    def load_history_by_date(self):
        """Load date-grouped sales history"""
        from controllers import sales_summary_by_date
        
        # Update table columns for date view
        columns = {
            'date': 'FECHA',
            'total_sales': 'VENTAS',
            'total_amount': 'MONTO TOTAL'
        }
        
        # Recreate table with new columns
        self.history_table.destroy()
        self.history_table = ModernTable(self.history_table.master, columns, height=20)
        self.history_table.pack(fill='both', expand=True)
        
        # Configure column widths and alignment - all left aligned
        self.history_table.tree.column('date', width=200, anchor='w')
        self.history_table.tree.column('total_sales', width=150, anchor='w')
        self.history_table.tree.column('total_amount', width=200, anchor='w')
        
        # Align headers to left
        self.history_table.tree.heading('date', anchor='w')
        self.history_table.tree.heading('total_sales', anchor='w')
        self.history_table.tree.heading('total_amount', anchor='w')
        
        # Load data
        data = sales_summary_by_date() or []
        
        # Format data for display
        formatted_data = []
        for row in data:
            formatted_data.append({
                'date': row['date'],
                'total_sales': row['total_sales'],
                'total_amount': f"Bs {row['total_amount']:.2f}"
            })
        
        self.history_table.insert_data(formatted_data)
    
    def refresh(self):
        """Refresh screen data"""
        if self.current_history_view == 'detailed':
            self.load_history_detailed()
        else:
            self.load_history_by_date()
