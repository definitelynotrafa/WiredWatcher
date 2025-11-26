"""
Animation handling for the application
"""
import random
from modules.config import Colors, Timing


class AnimationController:
    """Handles all animations for the application"""
    
    def __init__(self, root, canvas, gif_frames, gif_label):
        """
        Initialize animation controller
        
        Args:
            root: tkinter root window
            canvas: tkinter Canvas object
            gif_frames: list of PhotoImage frames
            gif_label: canvas item id for the GIF
        """
        self.root = root
        self.canvas = canvas
        self.gif_frames = gif_frames
        self.gif_label = gif_label
        self.current_frame = 0
    
    def start_animations(self):
        """Start all animations"""
        self.animate_gif()
        self.animate_flicker()
    
    def animate_gif(self):
        """Animates the GIF frames"""
        if self.gif_frames and self.gif_label:
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.canvas.itemconfig(self.gif_label, image=self.gif_frames[self.current_frame])
        
        # Next frame
        self.root.after(Timing.GIF_FRAME_DELAY, self.animate_gif)
    
    def animate_flicker(self):
        """Animates subtle CRT flicker effect"""
        # More subtle and realistic flicker
        flicker_intensity = random.choice([0, 1, 0, 0, 1, 0, 0, 0])
        if flicker_intensity:
            bg = Colors.FLICKER_ALT
        else:
            bg = Colors.BACKGROUND
        
        self.canvas.configure(bg=bg)
        
        # Next flicker
        self.root.after(Timing.FLICKER_DELAY, self.animate_flicker)
