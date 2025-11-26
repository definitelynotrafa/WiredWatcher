"""
Tools configuration screen for Configure Tools menu option
"""
import json
import os
from modules.config import Colors, Dimensions


class ToolsConfig:
    """Handles the tools configuration interface"""
    
    def __init__(self, canvas, fonts, root):
        """
        Initialize tools configuration
        
        Args:
            canvas: tkinter Canvas object
            fonts: dict with font configurations
            root: tkinter root window
        """
        self.canvas = canvas
        self.fonts = fonts
        self.root = root
        
        # Config file path
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        
        # Load or set default configurations
        self.load_config()
        
        # UI elements
        self.config_elements = []
        self.input_fields = {}
        self.active_field = None
        self.active_field_text = ""
        self.cursor_position = 0  # Cursor position in text
        self.scroll_offset = 0  # Scroll offset for long text
        self.cursor_visible = True  # Cursor always visible
        self.toggle_button = None
        self.back_button = None
        
    def show_config_menu(self):
        """Display the configuration menu"""
        # Clear existing config elements
        self.clear_config_menu()
        
        y_position = 260
        
        # Title
        title = self.canvas.create_text(
            450, y_position,
            text="toolsConfig://",
            font=self.fonts['title'],
            fill=Colors.PRIMARY,
            anchor="center"
        )
        self.config_elements.append(title)
        
        y_position += 50
        
        # Nmap configuration
        self._draw_config_field(
            y_position, 
            "NMAP COMMAND:", 
            self.nmap_command,
            "nmap"
        )
        
        y_position += 60
        
        # Fuzzer toggle
        self._draw_fuzzer_toggle(y_position)
        
        y_position += 60
        
        # Fuzzer command (gobuster or ffuf based on selection)
        if self.fuzzer_choice == "gobuster":
            self._draw_config_field(
                y_position,
                "GOBUSTER COMMAND:",
                self.gobuster_command,
                "gobuster"
            )
        else:
            self._draw_config_field(
                y_position,
                "FFUF COMMAND:",
                self.ffuf_command if self.ffuf_command else "[not set]",
                "ffuf"
            )
        
        y_position += 80
        
        # Back button
        self._draw_back_button(y_position)
        
    def _draw_config_field(self, y_pos, label, value, field_id):
        """Draw a configuration field"""
        # Label
        label_text = self.canvas.create_text(
            150, y_pos,
            text=label,
            font=self.fonts['menu'],
            fill=Colors.SECONDARY,
            anchor="w"
        )
        self.config_elements.append(label_text)
        
        # Field box
        box_x1 = 140
        box_x2 = 760
        box_y1 = y_pos + 15
        box_y2 = y_pos + 35
        
        field_box = self.canvas.create_rectangle(
            box_x1, box_y1, box_x2, box_y2,
            outline=Colors.DIM,
            fill=Colors.BACKGROUND,
            width=1,
            tags=f"field_{field_id}"
        )
        self.config_elements.append(field_box)
        
        # Display value (no truncation)
        display_value = value if value else "[not set]"
        
        field_text = self.canvas.create_text(
            150, y_pos + 25,
            text=display_value,
            font=("Courier New", 9),
            fill=Colors.TEXT if value and value != "[not set]" else Colors.DIM,
            anchor="w",
            tags=f"field_{field_id}"
        )
        self.config_elements.append(field_text)
        
        # Store field info for click detection
        self.input_fields[field_id] = {
            'box': field_box,
            'text': field_text,
            'y_min': box_y1,
            'y_max': box_y2,
            'x_min': box_x1,
            'x_max': box_x2,
            'label': label,
            'checkmark': None
        }
    
    def _draw_fuzzer_toggle(self, y_pos):
        """Draw the fuzzer toggle button"""
        # Label
        label_text = self.canvas.create_text(
            150, y_pos,
            text="WEB FUZZER:",
            font=self.fonts['menu'],
            fill=Colors.SECONDARY,
            anchor="w"
        )
        self.config_elements.append(label_text)
        
        # Toggle button
        btn_x = 450
        btn_y = y_pos + 20
        
        # Gobuster button
        gobuster_color = Colors.PRIMARY if self.fuzzer_choice == "gobuster" else Colors.DIM
        gobuster_bg = self.canvas.create_rectangle(
            btn_x - 100, btn_y - 12,
            btn_x - 10, btn_y + 12,
            outline=gobuster_color,
            fill=Colors.BACKGROUND if self.fuzzer_choice == "gobuster" else "",
            width=2 if self.fuzzer_choice == "gobuster" else 1,
            tags="toggle_gobuster"
        )
        self.config_elements.append(gobuster_bg)
        
        gobuster_text = self.canvas.create_text(
            btn_x - 55, btn_y,
            text="GOBUSTER",
            font=self.fonts['menu'],
            fill=gobuster_color,
            anchor="center",
            tags="toggle_gobuster"
        )
        self.config_elements.append(gobuster_text)
        
        # Ffuf button
        ffuf_color = Colors.PRIMARY if self.fuzzer_choice == "ffuf" else Colors.DIM
        ffuf_bg = self.canvas.create_rectangle(
            btn_x + 10, btn_y - 12,
            btn_x + 100, btn_y + 12,
            outline=ffuf_color,
            fill=Colors.BACKGROUND if self.fuzzer_choice == "ffuf" else "",
            width=2 if self.fuzzer_choice == "ffuf" else 1,
            tags="toggle_ffuf"
        )
        self.config_elements.append(ffuf_bg)
        
        ffuf_text = self.canvas.create_text(
            btn_x + 55, btn_y,
            text="FFUF",
            font=self.fonts['menu'],
            fill=ffuf_color,
            anchor="center",
            tags="toggle_ffuf"
        )
        self.config_elements.append(ffuf_text)
        
        # Store toggle button info
        self.toggle_button = {
            'gobuster': {
                'x_min': btn_x - 100,
                'x_max': btn_x - 10,
                'y_min': btn_y - 12,
                'y_max': btn_y + 12
            },
            'ffuf': {
                'x_min': btn_x + 10,
                'x_max': btn_x + 100,
                'y_min': btn_y - 12,
                'y_max': btn_y + 12
            }
        }
    
    def _draw_back_button(self, y_pos):
        """Draw back button to return to main menu"""
        btn_bg = self.canvas.create_rectangle(
            350, y_pos - 12,
            550, y_pos + 12,
            outline=Colors.ACCENT,
            fill="",
            width=1,
            tags="btn_back"
        )
        self.config_elements.append(btn_bg)
        
        btn_text = self.canvas.create_text(
            450, y_pos,
            text="BACK TO MAIN MENU",
            font=self.fonts['menu'],
            fill=Colors.ACCENT,
            anchor="center",
            tags="btn_back"
        )
        self.config_elements.append(btn_text)
        
        # Store back button info for click detection
        self.back_button = {
            'x_min': 350,
            'x_max': 550,
            'y_min': y_pos - 12,
            'y_max': y_pos + 12
        }
    
    def handle_click(self, event):
        """Handle mouse clicks on config fields"""
        # Check back button
        if self.back_button:
            if (self.back_button['x_min'] <= event.x <= self.back_button['x_max'] and
                self.back_button['y_min'] <= event.y <= self.back_button['y_max']):
                return 'back'
        
        # Check toggle buttons
        if self.toggle_button:
            if (self.toggle_button['gobuster']['x_min'] <= event.x <= self.toggle_button['gobuster']['x_max'] and
                self.toggle_button['gobuster']['y_min'] <= event.y <= self.toggle_button['gobuster']['y_max']):
                self.fuzzer_choice = "gobuster"
                self.save_config()
                self.show_config_menu()  # Refresh
                return True
            
            if (self.toggle_button['ffuf']['x_min'] <= event.x <= self.toggle_button['ffuf']['x_max'] and
                self.toggle_button['ffuf']['y_min'] <= event.y <= self.toggle_button['ffuf']['y_max']):
                self.fuzzer_choice = "ffuf"
                self.save_config()
                self.show_config_menu()  # Refresh
                return True
        
        # Check input fields
        for field_id, field_info in self.input_fields.items():
            if (field_info['x_min'] <= event.x <= field_info['x_max'] and
                field_info['y_min'] <= event.y <= field_info['y_max']):
                self._activate_field(field_id)
                return True
        
        return False
    
    def _activate_field(self, field_id):
        """Activate a field for inline editing"""
        # Deactivate any previous field
        if self.active_field:
            self._deactivate_field()
        
        # Set as active
        self.active_field = field_id
        
        # Get current value
        if field_id == "nmap":
            self.active_field_text = self.nmap_command
        elif field_id == "gobuster":
            self.active_field_text = self.gobuster_command
        elif field_id == "ffuf":
            self.active_field_text = self.ffuf_command
        
        # Set cursor to end
        self.cursor_position = len(self.active_field_text)
        self.scroll_offset = 0
        self.cursor_visible = True
        
        # Update display
        field_info = self.input_fields[field_id]
        self.canvas.itemconfig(field_info['box'], outline=Colors.PRIMARY, width=2)
        self._update_field_display()
    
    def _deactivate_field(self):
        """Deactivate current field"""
        if not self.active_field:
            return
        
        field_info = self.input_fields[self.active_field]
        self.canvas.itemconfig(field_info['box'], outline=Colors.DIM, width=1)
        
        # Get value to display
        value = self.active_field_text if self.active_field_text else "[not set]"
        self.canvas.itemconfig(field_info['text'], text=value, 
                              fill=Colors.TEXT if self.active_field_text else Colors.DIM)
        
        self.active_field = None
        self.active_field_text = ""
        self.cursor_position = 0
        self.scroll_offset = 0
        self.cursor_visible = True
    
    def _update_field_display(self):
        """Update field display with cursor and scroll"""
        if not self.active_field:
            return
        
        import tkinter.font as tkfont
        field_info = self.input_fields[self.active_field]
        
        # Font for measuring
        font = tkfont.Font(family="Courier New", size=9)
        
        # Max width for display (field width - padding)
        max_width = 600
        
        # Calculate what portion of text to show
        text_to_show = self.active_field_text
        cursor_pos = self.cursor_position
        
        # Measure text width
        full_width = font.measure(text_to_show)
        
        if full_width > max_width:
            # Need to scroll
            # Calculate where cursor should be visible
            cursor_offset = font.measure(text_to_show[:cursor_pos])
            
            # Adjust scroll offset to keep cursor visible
            if cursor_offset < self.scroll_offset:
                # Cursor is to the left of visible area
                self.scroll_offset = max(0, cursor_offset - 50)
            elif cursor_offset > self.scroll_offset + max_width:
                # Cursor is to the right of visible area
                self.scroll_offset = cursor_offset - max_width + 50
            
            # Find the visible portion of text
            start_char = 0
            end_char = len(text_to_show)
            
            # Binary search for start character
            for i in range(len(text_to_show)):
                if font.measure(text_to_show[:i]) >= self.scroll_offset:
                    start_char = max(0, i - 1)
                    break
            
            # Find end character
            for i in range(start_char, len(text_to_show)):
                if font.measure(text_to_show[start_char:i]) >= max_width:
                    end_char = i
                    break
            
            text_to_show = text_to_show[start_char:end_char]
            cursor_pos = cursor_pos - start_char
        else:
            self.scroll_offset = 0
        
        # Add cursor (always visible, no blink)
        if cursor_pos >= 0 and cursor_pos <= len(text_to_show):
            display_text = text_to_show[:cursor_pos] + "|" + text_to_show[cursor_pos:]
        else:
            display_text = text_to_show
        
        # Update canvas
        self.canvas.itemconfig(field_info['text'], text=display_text, fill=Colors.INPUT)
    
    def handle_key(self, event):
        """Handle keyboard input for active field"""
        if not self.active_field:
            return False
        
        if event.keysym == "Return":
            # Save the value
            if self.active_field == "nmap":
                self.nmap_command = self.active_field_text
            elif self.active_field == "gobuster":
                self.gobuster_command = self.active_field_text
            elif self.active_field == "ffuf":
                self.ffuf_command = self.active_field_text
            
            # Save to JSON
            self.save_config()
            
            # Show checkmark
            self._show_checkmark()
            
            # Deactivate field
            self._deactivate_field()
            return True
            
        elif event.keysym == "BackSpace":
            if self.cursor_position > 0:
                self.active_field_text = (self.active_field_text[:self.cursor_position-1] + 
                                         self.active_field_text[self.cursor_position:])
                self.cursor_position -= 1
                
        elif event.keysym == "Delete":
            if self.cursor_position < len(self.active_field_text):
                self.active_field_text = (self.active_field_text[:self.cursor_position] + 
                                         self.active_field_text[self.cursor_position+1:])
                
        elif event.keysym == "Left":
            if self.cursor_position > 0:
                self.cursor_position -= 1
                
        elif event.keysym == "Right":
            if self.cursor_position < len(self.active_field_text):
                self.cursor_position += 1
                
        elif event.keysym == "Home":
            self.cursor_position = 0
            
        elif event.keysym == "End":
            self.cursor_position = len(self.active_field_text)
            
        elif event.keysym == "Escape":
            # Cancel editing
            self._deactivate_field()
            return True
            
        elif len(event.char) == 1 and event.char.isprintable():
            # Insert character at cursor position
            self.active_field_text = (self.active_field_text[:self.cursor_position] + 
                                     event.char + 
                                     self.active_field_text[self.cursor_position:])
            self.cursor_position += 1
        
        # Update display
        if self.active_field:
            self._update_field_display()
        
        return True
    
    def _show_checkmark(self):
        """Show confirmation checkmark for saved field"""
        if not self.active_field:
            return
        
        field_info = self.input_fields[self.active_field]
        
        # Remove old checkmark if exists
        if field_info['checkmark']:
            self.canvas.delete(field_info['checkmark'])
        
        # Create checkmark
        checkmark = self.canvas.create_text(
            770, field_info['y_min'] + 10,
            text="✓",
            font=("Courier New", 14, "bold"),
            fill=Colors.TARGET,
            anchor="w"
        )
        field_info['checkmark'] = checkmark
        self.config_elements.append(checkmark)
        
        # Remove checkmark after 2 seconds
        self.root.after(2000, lambda: self._remove_checkmark(self.active_field))
    
    def _remove_checkmark(self, field_id):
        """Remove checkmark from field"""
        if field_id in self.input_fields and self.input_fields[field_id]['checkmark']:
            self.canvas.delete(self.input_fields[field_id]['checkmark'])
            self.input_fields[field_id]['checkmark'] = None
    
    def clear_config_menu(self):
        """Clear all configuration menu elements"""
        for element in self.config_elements:
            self.canvas.delete(element)
        self.config_elements.clear()
        self.input_fields.clear()
        self.toggle_button = None
    
    def is_active(self):
        """Check if config menu is currently displayed"""
        return len(self.config_elements) > 0
    
    def get_config(self):
        """Get current configuration"""
        fuzzer_cmd = self.gobuster_command if self.fuzzer_choice == "gobuster" else self.ffuf_command
        
        return {
            'nmap': self.nmap_command,
            'wordlist': self.wordlist_path,
            'fuzzer': self.fuzzer_choice,
            'fuzzer_command': fuzzer_cmd
        }
    
    def load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.nmap_command = config.get('nmap', "nmap -Pn -p- -sV -sC -O -T4")
                    self.wordlist_path = config.get('wordlist', "~/wordlists")
                    self.fuzzer_choice = config.get('fuzzer', "gobuster")
                    self.gobuster_command = config.get('gobuster', "gobuster dir -u target -w wordlist.txt -x php,txt,html,js,bak,old,zip,tar,conf,json,log")
                    self.ffuf_command = config.get('ffuf', "")
                    self.current_target = config.get('target', '')  # Load target
            except:
                # If error loading, use defaults
                self._set_defaults()
        else:
            self._set_defaults()
    
    def _set_defaults(self):
        """Set default configuration values"""
        self.nmap_command = "nmap -Pn -p- -sV -sC -O -T4"
        self.wordlist_path = "~/wordlists"
        self.fuzzer_choice = "gobuster"
        self.gobuster_command = "gobuster dir -u target -w wordlist.txt -x php,txt,html,js,bak,old,zip,tar,conf,json,log"
        self.ffuf_command = ""
        self.current_target = ""
    
    def save_config(self):
        """Save configuration to JSON file"""
        config = {
            'nmap': self.nmap_command,
            'wordlist': self.wordlist_path,
            'fuzzer': self.fuzzer_choice,
            'gobuster': self.gobuster_command,
            'ffuf': self.ffuf_command,
            'target': getattr(self, 'current_target', '')  # Save current target
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
