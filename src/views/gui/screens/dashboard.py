"""
Dashboard Screen
Overview statistics and product sales analytics
"""

import tkinter as tk
from tkinter import ttk
from ..components import Card, ModernTable, StyledLabel
from ..styles import COLORS, FONTS, SPACING
from controllers import (
    list_products_inventory,
    list_available_products,
    list_out_of_stock_products,
    get_top_selling_products,
    get_least_selling_products,
    get_unsold_products
)


class DashboardScreen(tk.Frame):
    """Dashboard with overview statistics and sales analytics"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        # Title
        title = StyledLabel(self, text="Dashboard", style='title')
        title.pack(anchor='w', padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Main container
        main_container = tk.Frame(self, bg=COLORS['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Configure 3-column grid for stat cards
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_columnconfigure(2, weight=1)
        
        # Row 0: Stat cards
        self.create_stat_cards(main_container)
        
        # Row 1: Single unified product table with filters
        self.create_product_table(main_container)
        
        # Load initial data
        self.load_statistics()
    
    def create_stat_cards(self, parent):
        """Create statistics cards"""
        # Get data
        all_products = list_products_inventory(1) or []
        available = list_available_products() or []
        out_of_stock = list_out_of_stock_products() or []
        
        stats = [
            ("Total Productos", len(all_products), COLORS['primary']),
            ("Con Stock", len(available), COLORS['success']),
            ("Sin Stock", len(out_of_stock), COLORS['danger']),
        ]
        
        # Store references to value labels for updating
        self.stat_labels = []
        
        for i, (label, value, color) in enumerate(stats):
            card = tk.Frame(parent, bg=COLORS['bg_secondary'], 
                           relief='flat', border=1, borderwidth=1)
            card.grid(row=0, column=i, padx=SPACING['sm'], pady=(0, SPACING['md']), sticky='ew')
            
            # Value
            value_label = tk.Label(card,
                                  text=str(value),
                                  font=('Segoe UI', 20, 'bold'),
                                  bg=COLORS['bg_secondary'],
                                  fg=color)
            value_label.pack(pady=(SPACING['sm'], SPACING['xs']))
            
            # Store reference for updating
            self.stat_labels.append(value_label)
            
            # Label
            text_label = tk.Label(card,
                                 text=label,
                                 font=FONTS['body'],
                                 bg=COLORS['bg_secondary'],
                                 fg=COLORS['text_secondary'])
            text_label.pack(pady=(0, SPACING['sm']))
    
    def create_product_table(self, parent):
        """Create unified product table with filters"""
        # Configure row 1 to expand
        parent.grid_rowconfigure(1, weight=1)
        
        # Card for products table
        products_card = Card(parent, title="")
        products_card.grid(row=1, column=0, columnspan=3, padx=SPACING['sm'], sticky='nsew')
        
        # Filter controls frame
        filter_frame = tk.Frame(products_card.content, bg=COLORS['bg_secondary'])
        filter_frame.pack(fill='x', pady=(0, SPACING['sm']))
        
        # Label
        tk.Label(filter_frame, text="Productos", font=FONTS['subheading'],
                bg=COLORS['bg_secondary'], fg=COLORS['text_primary']).pack(side='left', padx=(0, SPACING['md']))
        
        # Type dropdown
        tk.Label(filter_frame, text="Tipo:", font=FONTS['body'],
                bg=COLORS['bg_secondary'], fg=COLORS['text_primary']).pack(side='left', padx=(0, SPACING['xs']))
        
        self.type_var = tk.StringVar(value="Más Vendidos")
        type_combo = ttk.Combobox(filter_frame, textvariable=self.type_var, 
                                 values=["Más Vendidos", "Menos Vendidos", "No Vendidos"],
                                 state='readonly', width=15, font=FONTS['body'])
        type_combo.pack(side='left', padx=(0, SPACING['md']))
        type_combo.bind('<<ComboboxSelected>>', lambda e: self.load_products())
        
        # Top dropdown
        tk.Label(filter_frame, text="Top:", font=FONTS['body'],
                bg=COLORS['bg_secondary'], fg=COLORS['text_primary']).pack(side='left', padx=(0, SPACING['xs']))
        
        self.top_var = tk.StringVar(value="10")
        top_combo = ttk.Combobox(filter_frame, textvariable=self.top_var,
                                values=["10", "20", "30", "50", "100"],
                                state='readonly', width=5, font=FONTS['body'])
        top_combo.pack(side='left')
        top_combo.bind('<<ComboboxSelected>>', lambda e: self.load_products())
        
        # Products table
        columns = {
            'name': 'Producto',
            'quantity': 'Vendidos',
            'sale_price': 'Precio'
        }
        
        self.products_table = ModernTable(products_card.content, columns, height=12)
        self.products_table.pack(fill='both', expand=True)
    
    def load_statistics(self):
        """Load and display statistics"""
        # Update stat cards
        all_products = list_products_inventory(1) or []
        available = list_available_products() or []
        out_of_stock = list_out_of_stock_products() or []
        
        self.stat_labels[0].config(text=str(len(all_products)))
        self.stat_labels[1].config(text=str(len(available)))
        self.stat_labels[2].config(text=str(len(out_of_stock)))
        
        # Load products table
        self.load_products()
    
    def load_products(self):
        """Load products based on selected filters"""
        product_type = self.type_var.get()
        top_n = int(self.top_var.get())
        
        # Get data based on type
        if product_type == "Más Vendidos":
            products = get_top_selling_products(top_n) or []
        elif product_type == "Menos Vendidos":
            products = get_least_selling_products(top_n) or []
        else:  # No Vendidos
            products = get_unsold_products(top_n) or []
        
        # Clear table
        self.products_table.clear()
        
        # Populate table
        for product in products:
            # Controllers return 'product' and 'total_sold' keys
            product_name = product.get('product', 'N/A')
            quantity_sold = product.get('total_sold', 0)
            price = product.get('sale_price', 0.0)
            
            self.products_table.tree.insert('', 'end', values=(
                product_name,
                quantity_sold,
                f"{price:.2f}"
            ))
    
    def refresh(self):
        """Refresh dashboard data"""
        self.load_statistics()
