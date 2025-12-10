"""
Main GUI Application
Modern inventory management system with Tkinter
"""

import tkinter as tk
from .components import Sidebar
from .screens import (
    DashboardScreen,
    ProductsScreen,
    InventoryScreen,
    SalesScreen,
    CategoriesScreen
)
from .styles import COLORS, WINDOW_CONFIG


class InventoryGUI(tk.Tk):
    """Main GUI Application"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Sistema de Inventario")
        
        # Calculate center position for 800x600 window
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set geometry with centered position from the start
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(WINDOW_CONFIG['min_width'], WINDOW_CONFIG['min_height'])
        self.configure(bg=COLORS['bg_primary'])
        
        # Main container
        main_container = tk.Frame(self, bg=COLORS['bg_primary'])
        main_container.pack(fill='both', expand=True)
        
        # Sidebar
        self.sidebar = Sidebar(main_container, self.navigate)
        self.sidebar.pack(side='left', fill='y')
        
        # Content area
        self.content_frame = tk.Frame(main_container, bg=COLORS['bg_primary'])
        self.content_frame.pack(side='right', fill='both', expand=True)
        
        # Initialize screens
        self.screens = {}
        self.current_screen = None
        
        # Show dashboard by default
        self.navigate('dashboard')
    
    def navigate(self, screen_id):
        """Navigate to a different screen"""
        # Hide current screen
        if self.current_screen:
            self.current_screen.pack_forget()
        
        # Create screen if it doesn't exist
        if screen_id not in self.screens:
            self.screens[screen_id] = self._create_screen(screen_id)
        
        # Show new screen
        self.current_screen = self.screens[screen_id]
        self.current_screen.pack(fill='both', expand=True)
        
        # Refresh screen data
        if hasattr(self.current_screen, 'refresh'):
            self.current_screen.refresh()
    
    def _create_screen(self, screen_id):
        """Create a screen instance"""
        screens_map = {
            'dashboard': DashboardScreen,
            'products': ProductsScreen,
            'inventory': InventoryScreen,
            'sales': SalesScreen,
            'categories': CategoriesScreen,
        }
        
        screen_class = screens_map.get(screen_id)
        if screen_class:
            return screen_class(self.content_frame)
        
        # Fallback to dashboard
        return DashboardScreen(self.content_frame)


def run():
    """Run the GUI application"""
    app = InventoryGUI()
    app.mainloop()
