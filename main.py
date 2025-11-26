"""
Wired Recon - Serial Experiments Lain inspired reconnaissance tool
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


class SerialExperimentsRecon:
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
        
        # Keep GIF frames in memory to prevent garbage collection
        self.ui.gif_frames = self.gif_frames
        self.ui.gif_label = None
        
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
        self.root.title("wired://")
        self.root.geometry(f"{Dimensions.WINDOW_WIDTH}x{Dimensions.WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=Colors.BACKGROUND)
        self.root.overrideredirect(True)  # Borderless
    
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
            # Store in UI component as well
            self.ui.gif_label = self.gif_label
    
    def run(self):
        """Start the application main loop"""
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = SerialExperimentsRecon(root)
    app.run()
