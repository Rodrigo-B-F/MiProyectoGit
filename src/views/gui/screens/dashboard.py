"""
Dashboard Screen
Overview statistics and product sales analytics
"""

import tkinter as tk
from ..components import Card, ModernTable, StyledLabel, StyledButton
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
        
        # Main container for EVERYTHING - ensures alignment
        main_container = tk.Frame(self, bg=COLORS['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Configure 3-column grid for entire dashboard
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_columnconfigure(2, weight=1)
        
        # Row 0: Stat cards
        self.create_stat_cards(main_container)
        
        # Independent top N values for each table
        self.top_n_most = 10
        self.top_n_least = 10
        self.top_n_unsold = 10
        
        # Row 1: Statistics tables
        self.create_statistics_tables(main_container)
        
        # Load initial data
        self.load_statistics()
    
    def create_stat_cards(self, parent):
        """Create statistics cards in row 0"""
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
            
            # Value - reduced font size
            value_label = tk.Label(card,
                                  text=str(value),
                                  font=('Segoe UI', 24, 'bold'),
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
    
    def create_statistics_tables(self, parent):
        """Create sales statistics tables in row 1"""
        # Configure row 1 to expand
        parent.grid_rowconfigure(1, weight=1)
        
        # Most sold products
        most_sold_card = Card(parent, title="")
        most_sold_card.grid(row=1, column=0, padx=SPACING['sm'], sticky='nsew')
        
        # Header with title and filter button
        most_header = tk.Frame(most_sold_card.content, bg=COLORS['bg_secondary'])
        most_header.pack(fill='x', pady=(0, SPACING['xs']))
        
        StyledLabel(most_header, text="Más Vendidos", style='subheading').pack(side='left')
        self.most_filter_btn = StyledButton(most_header, f"Top {self.top_n_most}", style='secondary',
                                           command=lambda: self.show_filter_menu('most'), width=8)
        self.most_filter_btn.pack(side='right')
        
        most_sold_columns = {
            'product': 'PRODUCTO',
            'total_sold': 'VENDIDOS'
        }
        self.most_sold_table = ModernTable(most_sold_card.content, most_sold_columns, height=12)
        self.most_sold_table.pack(fill='both', expand=True)
        self.most_sold_table.tree.column('product', width=200, anchor='w')
        self.most_sold_table.tree.column('total_sold', width=100, anchor='center')
        
        # Least sold products
        least_sold_card = Card(parent, title="")
        least_sold_card.grid(row=1, column=1, padx=SPACING['sm'], sticky='nsew')
        
        # Header with title and filter button
        least_header = tk.Frame(least_sold_card.content, bg=COLORS['bg_secondary'])
        least_header.pack(fill='x', pady=(0, SPACING['xs']))
        
        StyledLabel(least_header, text="Menos Vendidos", style='subheading').pack(side='left')
        self.least_filter_btn = StyledButton(least_header, f"Top {self.top_n_least}", style='secondary',
                                            command=lambda: self.show_filter_menu('least'), width=8)
        self.least_filter_btn.pack(side='right')
        
        least_sold_columns = {
            'product': 'PRODUCTO',
            'total_sold': 'VENDIDOS'
        }
        self.least_sold_table = ModernTable(least_sold_card.content, least_sold_columns, height=12)
        self.least_sold_table.pack(fill='both', expand=True)
        self.least_sold_table.tree.column('product', width=200, anchor='w')
        self.least_sold_table.tree.column('total_sold', width=100, anchor='center')
        
        # Unsold products
        unsold_card = Card(parent, title="")
        unsold_card.grid(row=1, column=2, padx=SPACING['sm'], sticky='nsew')
        
        # Header with title and filter button
        unsold_header = tk.Frame(unsold_card.content, bg=COLORS['bg_secondary'])
        unsold_header.pack(fill='x', pady=(0, SPACING['xs']))
        
        StyledLabel(unsold_header, text="Sin Ventas", style='subheading').pack(side='left')
        self.unsold_filter_btn = StyledButton(unsold_header, f"Top {self.top_n_unsold}", style='secondary',
                                             command=lambda: self.show_filter_menu('unsold'), width=8)
        self.unsold_filter_btn.pack(side='right')
        
        unsold_columns = {
            'product': 'PRODUCTO',
            'total_sold': 'VENDIDOS'
        }
        self.unsold_table = ModernTable(unsold_card.content, unsold_columns, height=12)
        self.unsold_table.pack(fill='both', expand=True)
        self.unsold_table.tree.column('product', width=200, anchor='w')
        self.unsold_table.tree.column('total_sold', width=100, anchor='center')
    
    def show_filter_menu(self, table_type):
        """Show top N filter dropdown menu for specific table"""
        menu = tk.Menu(self, tearoff=0, 
                      bg=COLORS['bg_secondary'],
                      fg=COLORS['text_primary'],
                      activebackground=COLORS['primary'],
                      activeforeground=COLORS['text_white'],
                      font=FONTS['body'])
        
        for n in [10, 20, 30, 40, 50]:
            menu.add_command(label=f"Top {n}", 
                            command=lambda x=n, t=table_type: self.set_top_n(x, t))
        
        # Show menu below appropriate button
        if table_type == 'most':
            btn = self.most_filter_btn
        elif table_type == 'least':
            btn = self.least_filter_btn
        else:
            btn = self.unsold_filter_btn
        
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        menu.post(x, y)
    
    def set_top_n(self, n, table_type):
        """Set top N filter for specific table and reload its data"""
        if table_type == 'most':
            self.top_n_most = n
            self.most_filter_btn.config(text=f"Top {n}")
            most_sold = get_top_selling_products(n) or []
            self.most_sold_table.insert_data(most_sold)
        elif table_type == 'least':
            self.top_n_least = n
            self.least_filter_btn.config(text=f"Top {n}")
            least_sold = get_least_selling_products(n) or []
            self.least_sold_table.insert_data(least_sold)
        else:  # unsold
            self.top_n_unsold = n
            self.unsold_filter_btn.config(text=f"Top {n}")
            unsold = get_unsold_products(n) or []
            self.unsold_table.insert_data(unsold)
    
    def load_statistics(self):
        """Load sales statistics with current top N filters"""
        # Most sold
        most_sold = get_top_selling_products(self.top_n_most) or []
        self.most_sold_table.insert_data(most_sold)
        
        # Least sold
        least_sold = get_least_selling_products(self.top_n_least) or []
        self.least_sold_table.insert_data(least_sold)
        
        # Unsold
        unsold = get_unsold_products(self.top_n_unsold) or []
        self.unsold_table.insert_data(unsold)
    
    def refresh(self):
        """Refresh dashboard data"""
        # Get updated data
        all_products = list_products_inventory(1) or []
        available = list_available_products() or []
        out_of_stock = list_out_of_stock_products() or []
        
        # Update stat labels
        if hasattr(self, 'stat_labels') and len(self.stat_labels) >= 3:
            self.stat_labels[0].config(text=str(len(all_products)))
            self.stat_labels[1].config(text=str(len(available)))
            self.stat_labels[2].config(text=str(len(out_of_stock)))
        
        # Refresh sales statistics
        self.load_statistics()
