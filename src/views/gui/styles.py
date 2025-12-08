"""
Modern Styling System for Tkinter GUI
Provides consistent colors, fonts, and styling across the application
"""

# Color Palette
COLORS = {
    # Backgrounds
    'bg_primary': '#F5F5F5',      # Light gray background
    'bg_secondary': '#FFFFFF',     # White for cards
    'bg_sidebar': '#2C3E50',       # Dark blue-gray sidebar
    'bg_hover': '#34495E',         # Lighter blue-gray for hover
    
    # Primary Colors
    'primary': '#3498DB',          # Bright blue
    'primary_dark': '#2980B9',     # Darker blue for hover
    'primary_light': '#5DADE2',    # Light blue
    
    # Accent Colors
    'success': '#27AE60',          # Green
    'warning': '#F39C12',          # Orange
    'danger': '#E74C3C',           # Red
    'info': '#3498DB',             # Blue
    
    # Text Colors
    'text_primary': '#2C3E50',     # Dark gray
    'text_secondary': '#7F8C8D',   # Medium gray
    'text_light': '#ECF0F1',       # Light gray
    'text_white': '#FFFFFF',       # White
    
    # Borders
    'border': '#BDC3C7',           # Light gray border
    'border_dark': '#95A5A6',      # Medium gray border
}

# Typography
FONTS = {
    'title': ('Segoe UI', 24, 'bold'),
    'heading': ('Segoe UI', 18, 'bold'),
    'subheading': ('Segoe UI', 14, 'bold'),
    'body': ('Segoe UI', 11),
    'body_bold': ('Segoe UI', 11, 'bold'),
    'small': ('Segoe UI', 9),
    'button': ('Segoe UI', 10, 'bold'),
}

# Spacing
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 16,
    'lg': 24,
    'xl': 32,
}

# Component Styles
BUTTON_STYLE = {
    'primary': {
        'bg': COLORS['primary'],
        'fg': COLORS['text_white'],
        'active_bg': COLORS['primary_dark'],
        'border': 0,
        'relief': 'flat',
        'cursor': 'hand2',
        'padx': SPACING['md'],
        'pady': SPACING['sm'],
    },
    'secondary': {
        'bg': COLORS['bg_secondary'],
        'fg': COLORS['text_primary'],
        'active_bg': COLORS['bg_primary'],
        'border': 1,
        'relief': 'solid',
        'cursor': 'hand2',
        'padx': SPACING['md'],
        'pady': SPACING['sm'],
    },
    'success': {
        'bg': COLORS['success'],
        'fg': COLORS['text_white'],
        'active_bg': '#229954',
        'border': 0,
        'relief': 'flat',
        'cursor': 'hand2',
        'padx': SPACING['md'],
        'pady': SPACING['sm'],
    },
    'danger': {
        'bg': COLORS['danger'],
        'fg': COLORS['text_white'],
        'active_bg': '#C0392B',
        'border': 0,
        'relief': 'flat',
        'cursor': 'hand2',
        'padx': SPACING['md'],
        'pady': SPACING['sm'],
    },
}

ENTRY_STYLE = {
    'bg': COLORS['bg_secondary'],
    'fg': COLORS['text_primary'],
    'border': 1,
    'relief': 'solid',
    'insertbackground': COLORS['primary'],
}

CARD_STYLE = {
    'bg': COLORS['bg_secondary'],
    'relief': 'flat',
    'border': 1,
    'borderwidth': 1,
    'highlightthickness': 0,
}

# Window Configuration
WINDOW_CONFIG = {
    'bg': COLORS['bg_primary'],
    'min_width': 1400,
    'min_height': 900,
}

# Sidebar Configuration
SIDEBAR_CONFIG = {
    'width': 170,
    'bg': COLORS['bg_sidebar'],
    'button_height': 50,
}
