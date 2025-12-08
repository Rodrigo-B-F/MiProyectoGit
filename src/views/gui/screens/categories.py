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
    update_category
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
            'id': 'ID',
            'name': 'NOMBRE',
            'description': 'DESCRIPCION',
        }
        
        self.table = ModernTable(table_card.content, columns, height=20)
        self.table.pack(fill='both', expand=True)
        
        # Right side - Info
        right_frame = tk.Frame(main_container, bg=COLORS['bg_primary'], width=365)
        right_frame.pack(side='right', fill='y')
        right_frame.pack_propagate(False)
        
        info_card = Card(right_frame, title="Informacion")
        info_card.pack(fill='both')
        
        # Info text
        info_text = tk.Label(info_card.content,
                            text="Las categorias se crean automaticamente\n"
                                 "al agregar productos con un nuevo\n"
                                 "nombre de categoria.\n\n"
                                 "Aqui puedes ver todas las categorias\n"
                                 "existentes en el sistema.",
                            font=FONTS['body'],
                            bg=COLORS['bg_secondary'],
                            fg=COLORS['text_secondary'],
                            justify='left')
        info_text.pack(anchor='w', pady=SPACING['md'])
        
        # Load initial data
        self.load_categories()
    
    def load_categories(self):
        """Load all categories"""
        categories = list_categories() or []
        self.table.insert_data(categories)
        # Store all categories for search
        self.all_categories = categories
    
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
        """Adjust table columns to fit container"""
        self.table.auto_fit_columns()
    
    def refresh(self):
        """Refresh screen data"""
        self.load_categories()
