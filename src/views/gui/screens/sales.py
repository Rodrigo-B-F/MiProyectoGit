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
        
        # Left side - Sales form
        left_frame = tk.Frame(main_container, bg=COLORS['bg_primary'], width=450)
        left_frame.pack(side='left', fill='y', padx=(0, SPACING['sm']))
        left_frame.pack_propagate(False)
        
        form_card = Card(left_frame, title="Nueva Venta")
        form_card.pack(fill='both', expand=True)
        
        # Cart items
        self.cart = []
        
        # Product search
        self.barcode_field = FormField(form_card.content, "Codigo de Barras", 
                                      placeholder="Buscar producto...")
        self.barcode_field.pack(fill='x', pady=SPACING['sm'])
        
        self.quantity_field = FormField(form_card.content, "Cantidad", placeholder="1")
        self.quantity_field.pack(fill='x', pady=SPACING['sm'])
        
        StyledButton(form_card.content, "Agregar al Carrito", style='primary',
                    command=self.add_to_cart).pack(fill='x', pady=SPACING['sm'])
        
        # Cart display
        cart_label = StyledLabel(form_card.content, text="Carrito de Compra", style='subheading')
        cart_label.pack(anchor='w', pady=(SPACING['md'], SPACING['xs']))
        
        # Create Treeview for cart
        cart_container = tk.Frame(form_card.content, bg=COLORS['bg_primary'])
        cart_container.pack(fill='both', expand=True, pady=SPACING['sm'])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(cart_container)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        columns = ('producto', 'cantidad', 'precio', 'subtotal')
        self.cart_tree = ttk.Treeview(cart_container, columns=columns, show='headings',
                                      height=2, yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.cart_tree.yview)
        
        # Define headings
        self.cart_tree.heading('producto', text='PRODUCTO')
        self.cart_tree.heading('cantidad', text='CANT')
        self.cart_tree.heading('precio', text='P.UNIT')
        self.cart_tree.heading('subtotal', text='SUBTOTAL')
        
        # Define column widths
        self.cart_tree.column('producto', width=180, anchor='w')
        self.cart_tree.column('cantidad', width=60, anchor='center')
        self.cart_tree.column('precio', width=90, anchor='e')
        self.cart_tree.column('subtotal', width=100, anchor='e')
        
        self.cart_tree.pack(side='left', fill='both', expand=True)
        
        # Bind double-click to remove item (only on actual rows)
        self.cart_tree.bind('<Double-Button-1>', self.on_cart_double_click)
        
        # Total
        self.total_label = StyledLabel(form_card.content, text="Total: Bs 0.00", style='heading')
        self.total_label.pack(anchor='e', pady=SPACING['sm'])
        
        # Action buttons
        btn_frame = tk.Frame(form_card.content, bg=COLORS['bg_secondary'])
        btn_frame.pack(fill='x', pady=SPACING['sm'])
        
        StyledButton(btn_frame, "Completar Venta", style='success',
                    command=self.complete_sale).pack(fill='x', pady=SPACING['xs'])
        StyledButton(btn_frame, "Limpiar Carrito", style='danger',
                    command=self.clear_cart).pack(fill='x', pady=SPACING['xs'])
        
        # Right side - Sales history
        right_frame = tk.Frame(main_container, bg=COLORS['bg_primary'])
        right_frame.pack(side='right', fill='both', expand=True)
        
        history_card = Card(right_frame, title="Historial de Ventas")
        history_card.pack(fill='both', expand=True)
        
        columns = {
            'sale_id': PRODUCT_FIELDS['sale_id'],
            'timestamp': PRODUCT_FIELDS['timestamp'],
            'product': PRODUCT_FIELDS['product'],
            'quantity': PRODUCT_FIELDS['quantity'],
            'unit_price': PRODUCT_FIELDS['unit_price'],
            'subtotal': PRODUCT_FIELDS['subtotal']
        }
        
        self.history_table = ModernTable(history_card.content, columns, height=20)
        self.history_table.pack(fill='both', expand=True)
        
        # Load sales history
        self.load_history()
    
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
            self.load_history()
        else:
            messagebox.showerror("Error", message)
    
    def clear_cart(self):
        """Clear the cart"""
        self.cart = []
        self.update_cart_display()
    
    def load_history(self):
        """Load sales history"""
        history = list_sales_history() or []
        self.history_table.insert_data(history)
    
    def refresh(self):
        """Refresh screen data"""
        self.load_history()
