"""
Reusable Form Components
Modern styled input fields, buttons, and form elements
"""

import tkinter as tk
from tkinter import ttk
from ..styles import COLORS, FONTS, SPACING, BUTTON_STYLE, ENTRY_STYLE


class StyledButton(tk.Button):
    """Modern styled button with hover effects"""
    
    def __init__(self, parent, text="", style='primary', command=None, **kwargs):
        # Get style configuration
        btn_style = BUTTON_STYLE.get(style, BUTTON_STYLE['primary'])
        
        # Merge with custom kwargs
        config = {
            'text': text,
            'font': FONTS['button'],
            'bg': btn_style['bg'],
            'fg': btn_style['fg'],
            'activebackground': btn_style['active_bg'],
            'activeforeground': btn_style['fg'],
            'relief': btn_style['relief'],
            'border': btn_style['border'],
            'cursor': btn_style['cursor'],
            'padx': btn_style['padx'],
            'pady': btn_style['pady'],
            'command': command,
        }
        config.update(kwargs)
        
        super().__init__(parent, **config)
        
        # Store colors for hover effect
        self.default_bg = btn_style['bg']
        self.hover_bg = btn_style['active_bg']
        
        # Bind hover events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, event):
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.config(bg=self.default_bg)


class StyledEntry(tk.Entry):
    """Modern styled entry field"""
    
    def __init__(self, parent, placeholder="", **kwargs):
        config = {
            'font': FONTS['body'],
            'bg': ENTRY_STYLE['bg'],
            'fg': ENTRY_STYLE['fg'],
            'relief': ENTRY_STYLE['relief'],
            'border': ENTRY_STYLE['border'],
            'insertbackground': ENTRY_STYLE['insertbackground'],
        }
        config.update(kwargs)
        
        super().__init__(parent, **config)
        
        self.placeholder = placeholder
        self.placeholder_color = COLORS['text_secondary']
        self.default_color = ENTRY_STYLE['fg']
        
        if placeholder:
            self.insert(0, placeholder)
            self.config(fg=self.placeholder_color)
            self.bind('<FocusIn>', self._on_focus_in)
            self.bind('<FocusOut>', self._on_focus_out)
    
    def _on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_color)
    
    def _on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
    
    def get_value(self):
        """Get value, excluding placeholder"""
        value = self.get()
        return value if value != self.placeholder else ""


class StyledLabel(tk.Label):
    """Modern styled label"""
    
    def __init__(self, parent, text="", style='body', **kwargs):
        config = {
            'text': text,
            'font': FONTS.get(style, FONTS['body']),
            'bg': COLORS['bg_primary'],
            'fg': COLORS['text_primary'],
        }
        config.update(kwargs)
        
        super().__init__(parent, **config)


class FormField(tk.Frame):
    """Complete form field with label and input"""
    
    def __init__(self, parent, label_text, field_type='entry', **kwargs):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        # Label
        label = StyledLabel(self, text=label_text, style='body_bold')
        label.pack(anchor='w', pady=(0, SPACING['xs']))
        
        # Input field
        if field_type == 'entry':
            self.input = StyledEntry(self, **kwargs)
            self.input.pack(fill='x')
        elif field_type == 'text':
            self.input = tk.Text(self, height=4, font=FONTS['body'], 
                                bg=ENTRY_STYLE['bg'], fg=ENTRY_STYLE['fg'],
                                relief=ENTRY_STYLE['relief'], border=ENTRY_STYLE['border'])
            self.input.pack(fill='both', expand=True)
    
    def get_value(self):
        """Get the value from the input field"""
        if isinstance(self.input, StyledEntry):
            return self.input.get_value()
        elif isinstance(self.input, tk.Text):
            return self.input.get('1.0', 'end-1c')
        return ""
    
    def set_value(self, value):
        """Set the value of the input field"""
        if isinstance(self.input, StyledEntry):
            # Remove focus to prevent placeholder issues
            self.input.master.focus()
            
            self.input.delete(0, tk.END)
            if value:
                self.input.insert(0, value)
                self.input.config(fg=self.input.default_color)
            else:
                # Restore placeholder when setting empty value
                if self.input.placeholder:
                    self.input.insert(0, self.input.placeholder)
                    self.input.config(fg=self.input.placeholder_color)
        elif isinstance(self.input, tk.Text):
            self.input.delete('1.0', tk.END)
            self.input.insert('1.0', value)
