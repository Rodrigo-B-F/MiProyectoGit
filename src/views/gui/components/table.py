"""
Modern Data Table Component
Styled Treeview with search and sorting capabilities
"""

import tkinter as tk
from tkinter import ttk
from ..styles import COLORS, FONTS, SPACING


class ModernTable(tk.Frame):
    """Modern styled data table with Treeview"""
    
    def __init__(self, parent, columns, **kwargs):
        super().__init__(parent, bg=COLORS['bg_secondary'])
        
        self.columns = columns
        
        # Create Treeview
        self.tree = ttk.Treeview(self, columns=list(columns.keys()), show='headings', **kwargs)
        
        # Configure columns - Ultra compact for 800x600
        column_widths = {
            'name': 90,            # Very compact for product names
            'barcode': 50,         # Minimal for codes
            'category_name': 60,   # Minimal for categories
            'quantity': 45,        # Minimal for numbers
            'sale_price': 50,      # Minimal for prices
            'location': 60,        # Minimal for locations
            'active': 50,          # Minimal for status
            'id': 35,              # Very compact for IDs
            'description': 80,     # Compact for descriptions
            'sale_id': 50,         # Minimal for sale IDs
            'timestamp': 95,       # Compact for dates
            'product': 90,         # Compact for product names
            'unit_price': 50,      # Minimal for prices
            'subtotal': 50,        # Minimal for totals
        }
        
        for col_id, col_name in columns.items():
            self.tree.heading(col_id, text=col_name, anchor='w', command=lambda c=col_id: self._sort_column(c))
            # Use specific width if defined, otherwise default to 80
            width = column_widths.get(col_id, 80)
            self.tree.column(col_id, anchor='w', width=width, minwidth=40)
        
        # Store default widths for reset functionality
        self.default_widths = {}
        for col_id in self.columns.keys():
            width = column_widths.get(col_id, 150)
            self.default_widths[col_id] = width
            
        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Configure tags for alternating colors
        self.tree.tag_configure('oddrow', background=COLORS['bg_secondary'])
        self.tree.tag_configure('evenrow', background=COLORS['bg_primary'])
        
        # Apply custom style
        self._configure_style()
    
    def _configure_style(self):
        """Configure ttk style for the treeview"""
        style = ttk.Style()
        
        # Set theme to 'clam' for better color support
        style.theme_use('clam')
        
        # Treeview style
        style.configure("Treeview",
                       background=COLORS['bg_secondary'],
                       foreground=COLORS['text_primary'],
                       fieldbackground=COLORS['bg_secondary'],
                       font=FONTS['body'],
                       rowheight=35)
        
        # Treeview heading style
        style.configure("Treeview.Heading",
                       background=COLORS['bg_sidebar'],
                       foreground=COLORS['text_white'],
                       font=FONTS['body_bold'],
                       relief='flat',
                       borderwidth=1)
        
        style.map("Treeview.Heading",
                 background=[('active', COLORS['bg_hover'])],
                 relief=[('active', 'flat')])
        
        # Selected row style
        style.map('Treeview',
                 background=[('selected', COLORS['primary_light'])],
                 foreground=[('selected', COLORS['text_white'])])
    
    def insert_data(self, data):
        """Insert data into the table"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new data with alternating colors
        for i, row in enumerate(data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            # Map values for display
            values = []
            for col in self.columns.keys():
                value = row.get(col, '')
                # Map boolean values to Activo/Inactivo
                if isinstance(value, bool):
                    value = 'Activo' if value else 'Inactivo'
                elif value is True:
                    value = 'Activo'
                elif value is False:
                    value = 'Inactivo'
                elif str(value).lower() == 'true':
                    value = 'Activo'
                elif str(value).lower() == 'false':
                    value = 'Inactivo'
                values.append(value)
            self.tree.insert('', 'end', values=values, tags=(tag,))
    
    def get_selected(self):
        """Get selected row data"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            return dict(zip(self.columns.keys(), values))
        return None
    
    def _sort_column(self, col):
        """Sort table by column"""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        items.sort()
        
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.item(item, tags=(tag,))
    
    def auto_fit_columns(self):
        """Reset columns to default widths"""
        for col_id in self.columns.keys():
            default_width = self.default_widths.get(col_id, 150)
            self.tree.column(col_id, width=default_width, minwidth=80)
    
    def clear(self):
        """Clear all data from the table"""
        for item in self.tree.get_children():
            self.tree.delete(item)
