"""
Dashboard Screen
Main overview with summary cards and quick stats
"""

import tkinter as tk
from ..components import Card, StyledLabel
from ..styles import COLORS, FONTS, SPACING
from controllers import (
    list_products_inventory,
    list_available_products,
    list_out_of_stock_products
)


class DashboardScreen(tk.Frame):
    """Dashboard with overview statistics"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        # Title
        title = StyledLabel(self, text="Dashboard", style='title')
        title.pack(anchor='w', padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Stats cards container
        self.stats_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        self.stats_frame.pack(fill='x', padx=SPACING['lg'], pady=SPACING['md'])
        
        # Create stat cards
        self.create_stat_cards()
        
        # Welcome message
        welcome_card = Card(self, title="Bienvenido")
        welcome_card.pack(fill='both', expand=True, padx=SPACING['lg'], pady=SPACING['md'])
        
        welcome_text = tk.Label(welcome_card.content,
                               text="Sistema de Gestion de Inventario\n\n"
                                    "Utiliza el menu lateral para navegar entre las diferentes secciones.\n"
                                    "Puedes gestionar productos, inventario, ventas y categorias.",
                               font=FONTS['body'],
                               bg=COLORS['bg_secondary'],
                               fg=COLORS['text_secondary'],
                               justify='left')
        welcome_text.pack(anchor='w')
    
    def create_stat_cards(self):
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
            card = tk.Frame(self.stats_frame, bg=COLORS['bg_secondary'], 
                           relief='flat', border=1, borderwidth=1)
            card.grid(row=0, column=i, padx=SPACING['sm'], sticky='ew')
            self.stats_frame.grid_columnconfigure(i, weight=1)
            
            # Value
            value_label = tk.Label(card,
                                  text=str(value),
                                  font=('Segoe UI', 32, 'bold'),
                                  bg=COLORS['bg_secondary'],
                                  fg=color)
            value_label.pack(pady=(SPACING['lg'], SPACING['xs']))
            
            # Store reference for updating
            self.stat_labels.append(value_label)
            
            # Label
            text_label = tk.Label(card,
                                 text=label,
                                 font=FONTS['body'],
                                 bg=COLORS['bg_secondary'],
                                 fg=COLORS['text_secondary'])
            text_label.pack(pady=(0, SPACING['lg']))
    
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
