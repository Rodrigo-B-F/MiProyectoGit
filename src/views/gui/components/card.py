"""
Card Component
Container with modern styling for grouping content
"""

import tkinter as tk
from ..styles import COLORS, FONTS, SPACING, CARD_STYLE


class Card(tk.Frame):
    """Modern card container"""
    
    def __init__(self, parent, title="", **kwargs):
        config = {
            'bg': CARD_STYLE['bg'],
            'relief': CARD_STYLE['relief'],
            'border': CARD_STYLE['border'],
            'borderwidth': CARD_STYLE['borderwidth'],
            'highlightthickness': CARD_STYLE['highlightthickness'],
        }
        config.update(kwargs)
        
        super().__init__(parent, **config)
        
        # Title if provided
        if title:
            title_label = tk.Label(self,
                                  text=title,
                                  font=FONTS['subheading'],
                                  bg=CARD_STYLE['bg'],
                                  fg=COLORS['text_primary'])
            title_label.pack(anchor='w', padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
            
            # Separator
            separator = tk.Frame(self, bg=COLORS['border'], height=1)
            separator.pack(fill='x', padx=SPACING['md'])
        
        # Content frame
        self.content = tk.Frame(self, bg=CARD_STYLE['bg'])
        self.content.pack(fill='both', expand=True, padx=SPACING['md'], pady=SPACING['md'])
