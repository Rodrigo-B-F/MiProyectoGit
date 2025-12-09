"""
Category Combobox Component
Allows selecting existing categories or entering new ones
"""

import tkinter as tk
from tkinter import ttk
from ..styles import COLORS, FONTS, ENTRY_STYLE


class CategoryCombobox(tk.Frame):
    """Combobox for category selection with option to add new"""
    
    def __init__(self, parent, label_text="Categoria", **kwargs):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        # Label
        label = tk.Label(self, text=label_text, font=FONTS['body_bold'],
                        bg=COLORS['bg_primary'], fg=COLORS['text_primary'])
        label.pack(anchor='w', pady=(0, 4))
        
        # Combobox
        self.combobox = ttk.Combobox(self, font=FONTS['body'], **kwargs)
        self.combobox.pack(fill='x')
        
        # Configure style
        self._configure_style()
        
        # Load categories
        self.refresh_categories()
    
    def _configure_style(self):
        """Configure combobox style"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TCombobox',
                       fieldbackground=ENTRY_STYLE['bg'],
                       background=COLORS['bg_secondary'],
                       foreground=ENTRY_STYLE['fg'],
                       arrowcolor=COLORS['text_primary'],
                       borderwidth=1,
                       relief='solid')
        
        style.map('TCombobox',
                 fieldbackground=[('readonly', ENTRY_STYLE['bg'])],
                 selectbackground=[('readonly', COLORS['primary'])],
                 selectforeground=[('readonly', COLORS['text_white'])])
    
    def refresh_categories(self):
        """Load categories from database"""
        from controllers import list_categories
        
        categories = list_categories() or []
        category_names = [cat['name'] for cat in categories]
        
        # Add "Sin Categoría" option at the beginning
        category_names.insert(0, "Sin Categoría")
        
        self.combobox['values'] = category_names
        
        # Set placeholder if empty
        if not self.combobox.get() and category_names:
            self.combobox.set('')
    
    def get_value(self):
        """Get the selected or entered category name"""
        return self.combobox.get().strip()
    
    def set_value(self, value):
        """Set the category value"""
        self.combobox.set(value)
