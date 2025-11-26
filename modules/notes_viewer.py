"""
Notes viewer - displays saved recon output in separate window
"""
import os
import tkinter as tk
from modules.config import Colors, Dimensions, Fonts


class NotesViewer:
    """Handles notes/output viewing in separate window with scrolling"""
    
    def __init__(self, root):
        """
        Initialize notes viewer
        
        Args:
            root: main tkinter root window
        """
        self.main_root = root
        self.notes_window = None
        self.canvas = None
        
        # Output file - will find most recent _recon.txt file
        self.output_file = None
        
        # UI elements
        self.text_elements = []
        self.scroll_offset = 0
        self.all_lines = []
        self.max_visible_lines = 28
        
        # Scrollbar
        self.scrollbar = None
    
    def show_notes(self):
        """Display notes viewer in separate window"""
        if self.notes_window:
            # Window already exists, bring to front
            self.notes_window.lift()
            return
        
        # Create new window
        self.notes_window = tk.Toplevel(self.main_root)
        self.notes_window.title("notes://")
        self.notes_window.geometry("900x600")
        self.notes_window.resizable(False, False)
        self.notes_window.configure(bg=Colors.BACKGROUND)
        self.notes_window.overrideredirect(True)  # Borderless
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.notes_window,
            width=900,
            height=600,
            bg=Colors.BACKGROUND,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Draw scanlines
        self._draw_scanlines()
        
        # Draw interface
        self._draw_interface()
        
        # Load content
        self._load_content()
        
        # Display content
        self._update_display()
        
        # Bind events
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.notes_window.bind("<Escape>", self._close_window)
        
        # Bind drag to move window
        self.canvas.bind("<ButtonPress-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._on_drag)
    
    def _draw_scanlines(self):
        """Draw CRT scanlines"""
        for y in range(0, 600, 2):
            self.canvas.create_line(
                0, y, 900, y,
                fill="#101010",
                width=1
            )
        
        # Border
        self.canvas.create_rectangle(
            10, 10, 890, 590,
            outline=Colors.DIM,
            width=1
        )
    
    def _draw_interface(self):
        """Draw the notes interface"""
        # Title
        self.canvas.create_text(
            450, 40,
            text="notes://",
            font=(Fonts.FONT_FAMILY_PRIMARY, Fonts.TITLE_SIZE, "bold"),
            fill=Colors.PRIMARY,
            anchor="center"
        )
        
        # Output area background
        self.canvas.create_rectangle(
            30, 80,
            850, 550,
            outline=Colors.PRIMARY,
            fill=Colors.BACKGROUND,
            width=2
        )
        
        # Scrollbar background
        self.canvas.create_rectangle(
            855, 80,
            870, 550,
            outline=Colors.DIM,
            fill=Colors.BACKGROUND,
            width=1
        )
        
        # Close instruction
        self.canvas.create_text(
            450, 565,
            text="[ESC] Close",
            font=(Fonts.FONT_FAMILY_PRIMARY, 10),
            fill=Colors.ACCENT,
            anchor="center"
        )
    
    def _load_content(self):
        """Load content from output file"""
        self.all_lines = []
        
        # Find most recent _recon.txt file
        import glob
        base_dir = os.path.dirname(os.path.dirname(__file__))
        recon_files = glob.glob(os.path.join(base_dir, "*_recon.txt"))
        
        if recon_files:
            # Get most recent file
            self.output_file = max(recon_files, key=os.path.getmtime)
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        self.all_lines.append(line.rstrip('\n'))
            except:
                self.all_lines = ["[!] Error loading notes"]
        else:
            self.all_lines = ["[*] No reconnaissance data available yet", "", 
                            "[*] Run 'Start Recon' to generate output"]
    
    def _update_display(self):
        """Update displayed content"""
        if not self.canvas:
            return
        
        # Clear old text
        for elem in self.text_elements:
            self.canvas.delete(elem)
        self.text_elements.clear()
        
        # Calculate visible range
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.max_visible_lines, len(self.all_lines))
        
        # Display lines
        y_start = 90
        for i, idx in enumerate(range(start_idx, end_idx)):
            line = self.all_lines[idx]
            
            # Determine color based on content
            color = Colors.TEXT
            if line.startswith('[*]'):
                color = Colors.PRIMARY
            elif line.startswith('[✓]'):
                color = Colors.SECONDARY
            elif line.startswith('[!]'):
                color = Colors.INPUT
            elif line.startswith('==='):
                color = Colors.ACCENT
            
            text_elem = self.canvas.create_text(
                40, y_start + (i * 16),
                text=line[:100],  # Truncate if too long
                font=(Fonts.FONT_FAMILY_PRIMARY, 9),
                fill=color,
                anchor="w"
            )
            self.text_elements.append(text_elem)
        
        # Update scrollbar
        self._update_scrollbar()
    
    def _update_scrollbar(self):
        """Update scrollbar position"""
        if not self.canvas:
            return
        
        if self.scrollbar:
            self.canvas.delete(self.scrollbar)
        
        if len(self.all_lines) <= self.max_visible_lines:
            return  # No scrollbar needed
        
        # Calculate scrollbar size and position
        total_lines = len(self.all_lines)
        scrollbar_height = 470
        thumb_height = max(20, int(scrollbar_height * self.max_visible_lines / total_lines))
        
        # Calculate thumb position
        scroll_range = scrollbar_height - thumb_height
        if total_lines > self.max_visible_lines:
            thumb_y = 80 + int(scroll_range * self.scroll_offset / (total_lines - self.max_visible_lines))
        else:
            thumb_y = 80
        
        # Draw scrollbar thumb
        self.scrollbar = self.canvas.create_rectangle(
            857, thumb_y,
            868, thumb_y + thumb_height,
            outline=Colors.PRIMARY,
            fill=Colors.PRIMARY,
            width=0
        )
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling"""
        # Calculate scroll direction
        if event.delta > 0:
            # Scroll up
            self.scroll_offset = max(0, self.scroll_offset - 3)
        else:
            # Scroll down
            max_scroll = max(0, len(self.all_lines) - self.max_visible_lines)
            self.scroll_offset = min(max_scroll, self.scroll_offset + 3)
        
        # Update display
        self._update_display()
    
    def _start_drag(self, event):
        """Start dragging the window"""
        self.drag_x = event.x
        self.drag_y = event.y
    
    def _on_drag(self, event):
        """Drag the window"""
        x = self.notes_window.winfo_x() + (event.x - self.drag_x)
        y = self.notes_window.winfo_y() + (event.y - self.drag_y)
        self.notes_window.geometry(f"+{x}+{y}")
    
    def _close_window(self, event=None):
        """Close the notes window"""
        if self.notes_window:
            self.notes_window.destroy()
            self.notes_window = None
            self.canvas = None
            self.text_elements.clear()
    
    def clear_notes(self):
        """Clear notes viewer (close window)"""
        self._close_window()
    
    def is_active(self):
        """Check if notes viewer is active"""
        return self.notes_window is not None and self.notes_window.winfo_exists()
