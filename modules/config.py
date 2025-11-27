"""
Configuration and constants for the application
"""


class Colors:
    """Color scheme for the CRT"""
    PRIMARY = "#8941AD"  # Purple
    SECONDARY = "#d2738a"  # Pink
    ACCENT = "#8b00ff"  # Purple accent
    TEXT = "#c0c0c0"  # Silver/gray
    DIM = "#606060"  # Dim gray
    TARGET = "#6495ed"  # Blue Copland (cornflower blue)
    INPUT = "#ff3333"  # Red for input
    BACKGROUND = "#000000"  # Black
    SCANLINE = "#101010"  # Scanline color
    FLICKER_ALT = "#0a0a0a"  # Alternative background for flicker


class Dimensions:
    """Window and component dimensions"""
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 600
    BORDER_MARGIN = 10
    GIF_MAX_WIDTH = 400
    GIF_MAX_HEIGHT = 200
    GIF_CENTER_X = 450
    GIF_CENTER_Y = 120
    
    # Target box in top-right corner
    TARGET_BOX_RIGHT_MARGIN = 50
    TARGET_BOX_TOP_MARGIN = 30
    TARGET_BOX_PADDING_X = 12
    TARGET_BOX_PADDING_Y = 10


class Fonts:
    """Font configurations"""
    TITLE_SIZE = 18
    MENU_SIZE = 12
    INPUT_SIZE = 13
    FONT_FAMILY_PRIMARY = "Courier New"
    FONT_FAMILY_FALLBACK = "Courier"


class MenuOptions:
    """Menu options mapping"""
    OPTIONS = {
        '1': 'Start Recon',
        '2': 'Configure Tools',
        '3': 'Open Notes',
        '4': 'Reset',
        '5': 'Exit'
    }
    
    MENU_ITEMS = [
        "[1] Start Recon",
        "[2] Configure Tools",
        "[3] Open Notes",
        "[4] Reset",
        "[5] Exit"
    ]


class Timing:
    """Animation timing constants"""
    GIF_FRAME_DELAY = 100  # milliseconds
    FLICKER_DELAY = 100  # milliseconds
    CONFIRMATION_DISPLAY_TIME = 2000  # milliseconds
