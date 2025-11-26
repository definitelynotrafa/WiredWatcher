"""
GIF loading and processing functionality
"""
import os
import random
from PIL import Image, ImageTk
from modules.config import Dimensions


class GifLoader:
    """Handles loading and processing of GIF animations"""
    
    @staticmethod
    def load_random_gif():
        """
        Loads a random GIF from the assets folder
        
        Returns:
            list: List of PhotoImage frames, or placeholder if no GIFs found
        """
        assets_path = os.path.join(os.path.dirname(__file__), "assets")
        
        # Search for GIF files
        gif_files = []
        if os.path.exists(assets_path):
            gif_files = [f for f in os.listdir(assets_path) if f.lower().endswith('.gif')]
        
        if not gif_files:
            return GifLoader._create_placeholder()
        
        # Choose a random GIF
        random_gif = random.choice(gif_files)
        gif_path = os.path.join(assets_path, random_gif)
        
        try:
            return GifLoader._process_gif(gif_path)
        except Exception as e:
            print(f"Error loading GIF: {e}")
            return GifLoader._create_placeholder()
    
    @staticmethod
    def _process_gif(gif_path):
        """
        Processes a GIF file into frames maintaining aspect ratio
        
        Args:
            gif_path (str): Path to the GIF file
            
        Returns:
            list: List of PhotoImage frames
        """
        img = Image.open(gif_path)
        frames = []
        
        try:
            while True:
                # Copy current frame
                frame = img.copy()
                width, height = frame.size
                
                # Calculate new size maintaining aspect ratio
                ratio = width / height
                
                # Adjust by width
                new_width = min(width, Dimensions.GIF_MAX_WIDTH)
                new_height = int(new_width / ratio)
                
                # If height is too large, adjust by height
                if new_height > Dimensions.GIF_MAX_HEIGHT:
                    new_height = Dimensions.GIF_MAX_HEIGHT
                    new_width = int(new_height * ratio)
                
                # Resize only if necessary
                if new_width != width or new_height != height:
                    frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(frame)
                frames.append(photo)
                
                # Next frame
                img.seek(img.tell() + 1)
        except EOFError:
            pass  # End of frames
        
        return frames
    
    @staticmethod
    def _create_placeholder():
        """
        Creates a placeholder image if no GIFs are available
        
        Returns:
            list: List containing a single placeholder PhotoImage
        """
        img = Image.new('RGB', 
                       (Dimensions.GIF_MAX_WIDTH, Dimensions.GIF_MAX_HEIGHT), 
                       color='#1a1a1a')
        photo = ImageTk.PhotoImage(img)
        return [photo]
