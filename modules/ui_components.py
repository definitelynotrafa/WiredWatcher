"""
UI component drawing functions
"""
from modules.config import Colors, Dimensions, MenuOptions


class UIComponents:
    """Handles drawing of UI components on the canvas"""
    
    def __init__(self, canvas, fonts):
        """
        Initialize UI components
        
        Args:
            canvas: tkinter Canvas object
            fonts: dict with font configurations
        """
        self.canvas = canvas
        self.fonts = fonts
        self.menu_buttons = []
    
    def draw_scanlines(self):
        """Draws horizontal CRT scanlines"""
        # Only draw if not already present
        if self.canvas.find_withtag("scanline"):
            return
            
        for y in range(0, Dimensions.WINDOW_HEIGHT, 2):
            self.canvas.create_line(
                0, y, Dimensions.WINDOW_WIDTH, y,
                fill=Colors.SCANLINE,
                width=1,
                tags="scanline"
            )
        
        # Simple border
        self.canvas.create_rectangle(
            Dimensions.BORDER_MARGIN, 
            Dimensions.BORDER_MARGIN, 
            Dimensions.WINDOW_WIDTH - Dimensions.BORDER_MARGIN, 
            Dimensions.WINDOW_HEIGHT - Dimensions.BORDER_MARGIN,
            outline=Colors.DIM,
            width=1
        )
    
    def draw_interface(self):
        """
        Draws the main interface
        
        Returns:
            tuple: (target_text_id, input_x, input_y) for input handling
        """
        y_position = 250  # Start after GIF
        
        # ASCII art separator
        separator = "─" * 70
        self.canvas.create_text(
            450, y_position,
            text=separator,
            font=self.fonts['menu'],
            fill=Colors.DIM,
            anchor="center",
            tags="menu_item"
        )
        
        y_position += 50
        
        # Menu with clickable buttons
        self._draw_menu_buttons(y_position)
        
        y_position += 170
        
        # Separator before input
        self.canvas.create_text(
            450, y_position,
            text=separator,
            font=self.fonts['menu'],
            fill=Colors.DIM,
            anchor="center",
            tags="menu_item"
        )
        
        y_position += 30
        
        # Target field centered
        self.canvas.create_text(
            450, y_position,
            text="TARGET:",
            font=self.fonts['input'],
            fill=Colors.SECONDARY,
            anchor="center",
            tags="menu_item"
        )
        
        y_position += 25
        
        # Input position (centered)
        input_x = 450
        input_y = y_position
        
        # Input line centered
        target_text_id = self.canvas.create_text(
            input_x, input_y,
            text="",
            font=self.fonts['input'],
            fill=Colors.INPUT,
            anchor="center",
            tags="target_input"  # Special tag for target input
        )
        
        return target_text_id, input_x, input_y
    
    def _draw_menu_buttons(self, start_y):
        """
        Draws menu buttons
        
        Args:
            start_y: Starting Y position for menu
        """
        for i, item in enumerate(MenuOptions.MENU_ITEMS):
            y_item = start_y + (i * 30)
            
            # Button background
            btn_bg = self.canvas.create_rectangle(
                320, y_item - 12,
                580, y_item + 12,
                outline=Colors.DIM,
                fill="",
                width=1,
                tags=f"btn_{i+1}"
            )
            
            # Symbol before
            symbol = self.canvas.create_text(
                330, y_item,
                text="›",
                font=self.fonts['menu'],
                fill=Colors.PRIMARY,
                anchor="w",
                tags=f"btn_{i+1}"
            )
            
            # Button text
            text = self.canvas.create_text(
                345, y_item,
                text=item,
                font=self.fonts['menu'],
                fill=Colors.TEXT,
                anchor="w",
                tags=f"btn_{i+1}"
            )
            
            # Store button information
            self.menu_buttons.append({
                'y_min': y_item - 12,
                'y_max': y_item + 12,
                'x_min': 320,
                'x_max': 580,
                'option': str(i + 1),
                'tag': f"btn_{i+1}",
                'rect_id': btn_bg,
                'text_id': text,
                'symbol_id': symbol
            })
    
    def highlight_button(self, button, highlight=True):
        """
        Highlights or unhighlights a button
        
        Args:
            button: Button dict from menu_buttons
            highlight: True to highlight, False to normal state
        """
        if highlight:
            self.canvas.itemconfig(button['rect_id'], outline=Colors.PRIMARY, width=2)
            self.canvas.itemconfig(button['text_id'], fill=Colors.PRIMARY)
        else:
            self.canvas.itemconfig(button['rect_id'], outline=Colors.DIM, width=1)
            self.canvas.itemconfig(button['text_id'], fill=Colors.TEXT)
    
    def clear_menu(self):
        """Clear the main menu (for switching to other screens)"""
        # Get all canvas items
        all_items = self.canvas.find_all()
        
        # Keep GIF, scanlines/borders, target box, and target input
        for item in all_items:
            tags = self.canvas.gettags(item)
            item_type = self.canvas.type(item)
            
            # Always keep target_input visible
            if 'target_input' in tags:
                continue
            
            # Hide menu_item tagged elements
            if 'menu_item' in tags:
                self.canvas.itemconfig(item, state='hidden')
                continue
            
            # Skip images (GIF)
            if item_type == 'image':
                continue
            
            # Skip lines (scanlines)
            if item_type == 'line':
                continue
                
            # For rectangles, keep border and target box
            if item_type == 'rectangle':
                coords = self.canvas.coords(item)
                # Border rectangle
                if coords[0] == 10 and coords[1] == 10:
                    continue
                # Target box rectangles
                if coords[0] > 600:  # Target box is in right side
                    continue
                    
            # For text, keep target box text
            if item_type == 'text':
                coords = self.canvas.coords(item)
                if coords and coords[0] > 600:  # Target box text
                    continue
            
            # Delete everything else
            self.canvas.delete(item)
        
        # Clear menu buttons list
        self.menu_buttons.clear()
