"""
CTF reconnaissance tool
Main application entry point
"""
import tkinter as tk
from modules.config import Colors, Dimensions, Fonts
from modules.gif_loader import GifLoader
from modules.ui_components import UIComponents
from modules.animations import AnimationController
from modules.event_handlers import EventHandler
from modules.config_tools import ToolsConfig
from modules.recon_executor import ReconExecutor
from modules.notes_viewer import NotesViewer


class WiredWatcher:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self._setup_window()
        self._setup_fonts()
        self._setup_canvas()
        
        # Load GIF
        self.gif_frames = GifLoader.load_random_gif()
        self.gif_label = None
        
        # Initialize components
        self.ui = UIComponents(self.canvas, self.fonts)
        self.tools_config = ToolsConfig(self.canvas, self.fonts, self.root)
        self.recon_executor = ReconExecutor(self.canvas, self.fonts, self.root, self.tools_config)
        self.notes_viewer = NotesViewer(self.root)
        self.event_handler = EventHandler(self.root, self.canvas, self.ui, self.tools_config, self.recon_executor, self.notes_viewer)
        
        # Draw everything
        self._display_gif()
        self.ui.draw_scanlines()
        target_text_id, input_x, input_y = self.ui.draw_interface()
        
        # Setup event handling
        self.event_handler.set_input_references(target_text_id, input_x, input_y)
        self.event_handler.setup_bindings()
        
        # Load saved target if exists
        if self.tools_config.current_target:
            self.event_handler.confirmed_target = self.tools_config.current_target
            self.event_handler._update_target_box()
        
        # Start animations
        self.animation_controller = AnimationController(
            self.root,
            self.canvas,
            self.gif_frames,
            self.gif_label
        )
        self.animation_controller.start_animations()
    
    def _setup_window(self):
        """Configure main window"""
        self.root.title("wired://watcher")
        self.root.geometry(f"{Dimensions.WINDOW_WIDTH}x{Dimensions.WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=Colors.BACKGROUND)
        
        # Set icon
        try:
            import os
            from PIL import Image, ImageTk
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules', 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                # Use PhotoImage for Linux compatibility
                icon_image = Image.open(icon_path)
                photo = ImageTk.PhotoImage(icon_image)
                self.root.iconphoto(True, photo)
        except:
            # Fallback to iconbitmap for Windows
            try:
                import os
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules', 'assets', 'icon.ico')
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            except:
                pass
        
        # Dark title bar - THIS THING IS FOR WINDOWS ONLY, WHICH IS PROBABLY THE OS THAT YOU ARE NOT USING XDDDD
        try:
            self.root.update()
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            value = ctypes.c_int(2)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
        except:
            pass
    
    def _setup_fonts(self):
        """Setup font configurations"""
        try:
            self.fonts = {
                'title': (Fonts.FONT_FAMILY_PRIMARY, Fonts.TITLE_SIZE, "bold"),
                'menu': (Fonts.FONT_FAMILY_PRIMARY, Fonts.MENU_SIZE),
                'input': (Fonts.FONT_FAMILY_PRIMARY, Fonts.INPUT_SIZE)
            }
            # Test if font exists
            tk.Label(self.root, font=self.fonts['title']).destroy()
        except:
            self.fonts = {
                'title': (Fonts.FONT_FAMILY_FALLBACK, Fonts.TITLE_SIZE, "bold"),
                'menu': (Fonts.FONT_FAMILY_FALLBACK, Fonts.MENU_SIZE),
                'input': (Fonts.FONT_FAMILY_FALLBACK, Fonts.INPUT_SIZE)
            }
    
    def _setup_canvas(self):
        """Create main canvas"""
        self.canvas = tk.Canvas(
            self.root,
            width=Dimensions.WINDOW_WIDTH,
            height=Dimensions.WINDOW_HEIGHT,
            bg=Colors.BACKGROUND,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
    
    def _display_gif(self):
        """Display the GIF on canvas"""
        if self.gif_frames:
            self.gif_label = self.canvas.create_image(
                Dimensions.GIF_CENTER_X,
                Dimensions.GIF_CENTER_Y,
                image=self.gif_frames[0],
                anchor="center"
            )
    
    def run(self):
        """Start the application main loop"""
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = WiredWatcher(root)
    app.run()
