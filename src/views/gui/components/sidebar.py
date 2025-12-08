"""
Navigation Sidebar Component
Modern vertical navigation menu
"""

import tkinter as tk
from ..styles import COLORS, FONTS, SPACING, SIDEBAR_CONFIG


class Sidebar(tk.Frame):
    """Modern navigation sidebar"""
    
    def __init__(self, parent, on_navigate):
        super().__init__(parent, 
                        bg=SIDEBAR_CONFIG['bg'],
                        width=SIDEBAR_CONFIG['width'])
                        
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.active_button = None
        
        # Logo/Title area
        title_frame = tk.Frame(self, bg=SIDEBAR_CONFIG['bg'], height=85)
        title_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['lg'])
        title_frame.pack_propagate(False)
        
        title = tk.Label(title_frame, 
                        text="Sistema\nde\nInventario",
                        font=FONTS['heading'],
                        bg=SIDEBAR_CONFIG['bg'],
                        fg=COLORS['text_white'],
                        justify='left')
        title.pack(anchor='w')
        
        # Separator
        separator = tk.Frame(self, bg=COLORS['border'], height=1)
        separator.pack(fill='x', pady=SPACING['sm'])
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ('dashboard', 'Dashboard'),
            ('products', 'Productos'),
            ('inventory', 'Inventario'),
            ('sales', 'Ventas'),
            ('categories', 'Categorias'),
        ]
        
        for screen_id, label in nav_items:
            btn = self._create_nav_button(label, screen_id)
            self.nav_buttons[screen_id] = btn
        
        # Set dashboard as active by default
        self.set_active('dashboard')
    
    def _create_nav_button(self, text, screen_id):
        """Create a navigation button"""
        btn = tk.Button(self,
                       text=text,
                       font=FONTS['body_bold'],
                       bg=SIDEBAR_CONFIG['bg'],
                       fg=COLORS['text_light'],
                       activebackground=COLORS['bg_hover'],
                       activeforeground=COLORS['text_white'],
                       relief='flat',
                       border=0,
                       cursor='hand2',
                       anchor='w',
                       padx=SPACING['lg'],
                       pady=SPACING['md'],
                       command=lambda: self._on_click(screen_id))
        
        btn.pack(fill='x', pady=2)
        
        # Hover effects
        btn.bind('<Enter>', lambda e: self._on_hover(btn, screen_id))
        btn.bind('<Leave>', lambda e: self._on_leave(btn, screen_id))
        
        return btn
    
    def _on_click(self, screen_id):
        """Handle navigation button click"""
        self.set_active(screen_id)
        self.on_navigate(screen_id)
    
    def _on_hover(self, btn, screen_id):
        """Handle button hover"""
        if self.active_button != btn:
            btn.config(bg=COLORS['bg_hover'])
    
    def _on_leave(self, btn, screen_id):
        """Handle button leave"""
        if self.active_button != btn:
            btn.config(bg=SIDEBAR_CONFIG['bg'])
    
    def set_active(self, screen_id):
        """Set active navigation button"""
        # Reset previous active button
        if self.active_button:
            self.active_button.config(bg=SIDEBAR_CONFIG['bg'])
        
        # Set new active button
        if screen_id in self.nav_buttons:
            btn = self.nav_buttons[screen_id]
            btn.config(bg=COLORS['primary'])
            self.active_button = btn
