COLORS = {
    "primary": "#1976D2",
    "primary_light": "#BBDEFB",
    "primary_dark": "#0D47A1",
    "secondary": "#FFC107",
    "secondary_light": "#FFECB3",
    "secondary_dark": "#FF8F00",
    "background": "#FAFAFA",
    "surface": "#FFFFFF",
    "error": "#B00020",
    "on_primary": "#FFFFFF",
    "on_secondary": "#000000",
    "on_background": "#000000",
    "on_surface": "#000000",
    "on_error": "#FFFFFF",
    "success": "#4CAF50",
    "info": "#2196F3",
    "warning": "#FF9800",
    "tile": "#42A5F5",
    "tile_text": "#FFFFFF",
    "empty_tile": "#E3F2FD",
}

FONTS = {
    "heading": ("Roboto", 16, "bold"),  
    "subheading": ("Roboto", 12, "bold"), 
    "body": ("Roboto", 10),  
    "button": ("Roboto", 9, "bold"),  
    "tile": ("Roboto", 20, "bold"),  
    "small": ("Roboto", 8),
}

STYLES = {
    "button": {
        "bg": COLORS["primary"],
        "fg": COLORS["on_primary"],
        "activebackground": COLORS["primary_dark"],
        "activeforeground": COLORS["on_primary"],
        "relief": "flat",
        "borderwidth": 0,
        "padx": 10,
        "pady": 5,
        "font": FONTS["button"]
    },
    "secondary_button": {
        "bg": COLORS["secondary"],
        "fg": COLORS["on_secondary"],
        "activebackground": COLORS["secondary_dark"],
        "activeforeground": COLORS["on_secondary"],
        "relief": "flat",
        "borderwidth": 0,
        "padx": 10,
        "pady": 5,
        "font": FONTS["button"]
    },
    "frame": {
        "bg": COLORS["surface"],
        "highlightbackground": COLORS["primary_light"],
        "highlightthickness": 1
    },
    "label": {
        "bg": COLORS["surface"],
        "fg": COLORS["on_surface"],
        "font": FONTS["body"]
    },
    "heading": {
        "bg": COLORS["surface"],
        "fg": COLORS["primary"],
        "font": FONTS["heading"]
    },
    "tile": {
        "bg": COLORS["tile"],
        "fg": COLORS["tile_text"],
        "font": FONTS["tile"],
        "width": 2,
        "height": 1,
        "relief": "raised",
        "borderwidth": 2
    },
    "empty_tile": {
        "bg": COLORS["empty_tile"],
        "relief": "sunken",
        "borderwidth": 2
    }
}

def apply_style(widget, style_name):
    if style_name in STYLES:
        for key, value in STYLES[style_name].items():
            try:
                widget[key] = value
            except:
                pass
    return widget