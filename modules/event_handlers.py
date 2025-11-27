"""
Event handling for keyboard and mouse interactions
"""
from modules.config import Colors, MenuOptions, Timing, Dimensions


class EventHandler:
    """Handles keyboard and mouse events"""
    
    def __init__(self, root, canvas, ui_components, tools_config, recon_executor, notes_viewer):
        """
        Initialize event handler
        
        Args:
            root: tkinter root window
            canvas: tkinter Canvas object
            ui_components: UIComponents instance
            tools_config: ToolsConfig instance
            recon_executor: ReconExecutor instance
            notes_viewer: NotesViewer instance
        """
        self.root = root
        self.canvas = canvas
        self.ui = ui_components
        self.tools_config = tools_config
        self.recon_executor = recon_executor
        self.notes_viewer = notes_viewer
        
        # State
        self.target_text = ""
        self.target_text_id = None
        self.input_x = 0
        self.input_y = 0
        self.confirmation_symbol_id = None
        self.feedback_texts = []
        
        # Target box in top-right corner
        self.target_box_rect = []
        self.target_box_text = None
        self.confirmed_target = ""
        
        # Drag state
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_moved = False
        
        # Mouse move throttle
        self.mouse_move_pending = False
    
    def setup_bindings(self):
        """Setup all event bindings"""
        self.root.bind("<Key>", self.on_key_press)
        self.root.bind("<Escape>", self._handle_escape)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        # Separate drag and click bindings
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        # Mouse wheel scroll
        self.canvas.bind("<Button-4>", self._on_mouse_scroll)  # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mouse_scroll)  # Linux scroll down
        self.canvas.bind("<MouseWheel>", self._on_mouse_scroll)  # Windows/Mac
    
    def _on_mouse_down(self, event):
        """Handle mouse button press"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.drag_moved = False
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag motion"""
        # Calculate distance moved
        dx = abs(event.x - self.drag_start_x)
        dy = abs(event.y - self.drag_start_y)
        
        # Only start dragging if moved more than 5 pixels
        if dx > 5 or dy > 5:
            self.drag_moved = True
            # Drag the window
            x = self.root.winfo_x() + (event.x - self.drag_start_x)
            y = self.root.winfo_y() + (event.y - self.drag_start_y)
            self.root.geometry(f"+{x}+{y}")
    
    def _on_mouse_up(self, event):
        """Handle mouse button release"""
        # Only process as click if didn't drag
        if not self.drag_moved:
            self.on_canvas_click(event)
    
    def _on_mouse_scroll(self, event):
        """Handle mouse wheel scroll"""
        if self.recon_executor.is_active():
            # Linux uses event.num, Windows/Mac uses event.delta
            if hasattr(event, 'num'):
                if event.num == 4:
                    # Scroll up
                    self.recon_executor.scroll(-3)
                elif event.num == 5:
                    # Scroll down
                    self.recon_executor.scroll(3)
            elif hasattr(event, 'delta'):
                if event.delta > 0:
                    # Scroll up
                    self.recon_executor.scroll(-3)
                elif event.delta < 0:
                    # Scroll down
                    self.recon_executor.scroll(3)
    
    def _handle_escape(self, event):
        """Handle escape key - back to main menu or quit"""
        # Check if notes viewer is open - let it handle its own ESC
        if self.notes_viewer.is_active():
            return
        
        if self.recon_executor.is_active():
            # Stop recon and return to main menu
            self.recon_executor.stop_recon()
            self.recon_executor.clear_recon_screen()
            self._restore_main_menu()
            return
        
        if self.tools_config.is_active():
            # Return to main menu
            self.tools_config.clear_config_menu()
            # Restore main menu visibility
            self._restore_main_menu()
            return
        
        # Quit application
        self.root.quit()
    
    def _restore_main_menu(self):
        """Restore main menu visibility"""
        # Show all hidden menu_item tagged elements
        all_items = self.canvas.find_all()
        for item in all_items:
            tags = self.canvas.gettags(item)
            if 'menu_item' in tags:
                self.canvas.itemconfig(item, state='normal')
        
        # Redraw menu buttons
        self.ui.draw_interface()
    
    def _restore_main_menu(self):
        """Restore main menu visibility"""
        # Show all hidden menu_item tagged elements
        all_items = self.canvas.find_all()
        for item in all_items:
            tags = self.canvas.gettags(item)
            if 'menu_item' in tags:
                self.canvas.itemconfig(item, state='normal')
        
        # Redraw menu buttons
        self.ui.draw_interface()
    
    def set_input_references(self, target_text_id, input_x, input_y):
        """
        Set references for input handling
        
        Args:
            target_text_id: Canvas text item id
            input_x: X position of input
            input_y: Y position of input
        """
        self.target_text_id = target_text_id
        self.input_x = input_x
        self.input_y = input_y
    
    def on_key_press(self, event):
        """Handle keyboard input"""
        # If config menu is active, only handle config keys
        if self.tools_config.is_active():
            # Only let config menu handle keys
            self.tools_config.handle_key(event)
            return
        
        # Only allow target input in main menu
        if event.keysym == "Return":
            # Enter pressed
            if self.target_text.strip():
                # Clear previous feedback
                self._clear_feedback()
                
                # Process command and don't clear target_text! 
                self._process_command(self.target_text)
                
        elif event.keysym == "BackSpace":
            # Remove last character
            self.target_text = self.target_text[:-1]
            # Return to red when editing
            self.canvas.itemconfig(self.target_text_id, fill=Colors.INPUT)
            
        elif len(event.char) == 1 and event.char.isprintable():
            # Add character to target
            self.target_text += event.char
            # Keep red while typing
            self.canvas.itemconfig(self.target_text_id, fill=Colors.INPUT)
        
        # Update text on canvas
        if self.target_text_id:
            self.canvas.itemconfig(self.target_text_id, text=self.target_text)
    
    def on_mouse_move(self, event):
        """Handle mouse movement over buttons"""
        # Throttle mouse move events
        if self.mouse_move_pending:
            return
            
        self.mouse_move_pending = True
        self.root.after(50, lambda: setattr(self, 'mouse_move_pending', False))
        
        # Don't highlight during config menu
        if self.tools_config.is_active():
            return
        
        mouse_over_button = False
        
        for btn in self.ui.menu_buttons:
            if (btn['x_min'] <= event.x <= btn['x_max'] and 
                btn['y_min'] <= event.y <= btn['y_max']):
                # Mouse over button - highlight
                self.ui.highlight_button(btn, highlight=True)
                self.canvas.config(cursor="hand2")
                mouse_over_button = True
            else:
                # Mouse outside button - normal state
                self.ui.highlight_button(btn, highlight=False)
        
        # If not over any button
        if not mouse_over_button:
            self.canvas.config(cursor="")
    
    def on_canvas_click(self, event):
        """Handle clicks on buttons"""
        # Check if config menu is active and handle its clicks
        if self.tools_config.is_active():
            result = self.tools_config.handle_click(event)
            if result == 'back':
                # Back button clicked
                self.tools_config.clear_config_menu()
                self._restore_main_menu()
                return
            elif result:
                return
        
        # Handle main menu buttons
        for btn in self.ui.menu_buttons:
            if (btn['x_min'] <= event.x <= btn['x_max'] and 
                btn['y_min'] <= event.y <= btn['y_max']):
                # Clicked on button - clear feedback first
                self._clear_feedback()
                
                # Execute option
                self._execute_menu_option(btn['option'])
                break
    
    def _process_command(self, command):
        """Process command typed in target field"""
        # Remove previous symbol if exists
        if self.confirmation_symbol_id:
            self.canvas.delete(self.confirmation_symbol_id)
        
        # Remove old target box completely
        if self.target_box_rect:
            for rect_id in self.target_box_rect:
                self.canvas.delete(rect_id)
            self.target_box_rect = []
        if self.target_box_text:
            self.canvas.delete(self.target_box_text)
            self.target_box_text = None
        
        # Store confirmed target
        self.confirmed_target = command
        
        # Save target to config
        self.tools_config.current_target = command
        self.tools_config.save_config()
        
        # Clear the input field
        self.target_text = ""
        self.canvas.itemconfig(self.target_text_id, text="", fill=Colors.INPUT)
        
        # Update or create target box in top-right corner
        self._update_target_box()
        
        # Show confirmation symbol briefly
        self.confirmation_symbol_id = self.canvas.create_text(
            self.input_x + 150,
            self.input_y,
            text="✓",
            font=("Courier New", 16, "bold"),
            fill=Colors.TARGET,
            anchor="w"
        )
        
        # Remove symbol after delay
        self.root.after(
            Timing.CONFIRMATION_DISPLAY_TIME,
            lambda: self.canvas.delete(self.confirmation_symbol_id) 
                if self.confirmation_symbol_id else None
        )
    
    def _update_target_box(self):
        """Update or create the target box in top-right corner"""
        import tkinter.font as tkfont
        
        # Delete old box elements if exist
        if self.target_box_rect:
            self.canvas.delete(self.target_box_rect)
        if self.target_box_text:
            self.canvas.delete(self.target_box_text)
        
        # Create font object to measure text width
        font = tkfont.Font(family="Courier New", size=10, weight="bold")
        text_width = font.measure(self.confirmed_target)
        text_height = font.metrics("linespace")
        
        # Calculate box dimensions based on text
        box_width = text_width + (Dimensions.TARGET_BOX_PADDING_X * 2)
        box_height = text_height + (Dimensions.TARGET_BOX_PADDING_Y * 2)
        
        # Position box aligned to top-right corner
        box_x2 = Dimensions.WINDOW_WIDTH - Dimensions.TARGET_BOX_RIGHT_MARGIN
        box_x1 = box_x2 - box_width
        box_y1 = Dimensions.TARGET_BOX_TOP_MARGIN
        box_y2 = box_y1 + box_height
        
        # Store as list to track multiple elements
        self.target_box_rect = []
        
        # Main rectangle with thicker border
        main_rect = self.canvas.create_rectangle(
            box_x1, box_y1, box_x2, box_y2,
            outline=Colors.TARGET,
            fill=Colors.BACKGROUND,
            width=2
        )
        self.target_box_rect.append(main_rect)
        
        # Corner accents
        corner_length = 8
        
        # Top-left corner
        tl1 = self.canvas.create_line(
            box_x1 - 1, box_y1, box_x1 + corner_length, box_y1,
            fill=Colors.PRIMARY, width=2
        )
        tl2 = self.canvas.create_line(
            box_x1, box_y1 - 1, box_x1, box_y1 + corner_length,
            fill=Colors.PRIMARY, width=2
        )
        
        # Top-right corner
        tr1 = self.canvas.create_line(
            box_x2 - corner_length, box_y1, box_x2 + 1, box_y1,
            fill=Colors.PRIMARY, width=2
        )
        tr2 = self.canvas.create_line(
            box_x2, box_y1 - 1, box_x2, box_y1 + corner_length,
            fill=Colors.PRIMARY, width=2
        )
        
        # Bottom-left corner
        bl1 = self.canvas.create_line(
            box_x1 - 1, box_y2, box_x1 + corner_length, box_y2,
            fill=Colors.PRIMARY, width=2
        )
        bl2 = self.canvas.create_line(
            box_x1, box_y2 - corner_length, box_x1, box_y2 + 1,
            fill=Colors.PRIMARY, width=2
        )
        
        # Bottom-right corner
        br1 = self.canvas.create_line(
            box_x2 - corner_length, box_y2, box_x2 + 1, box_y2,
            fill=Colors.PRIMARY, width=2
        )
        br2 = self.canvas.create_line(
            box_x2, box_y2 - corner_length, box_x2, box_y2 + 1,
            fill=Colors.PRIMARY, width=2
        )
        
        self.target_box_rect.extend([tl1, tl2, tr1, tr2, bl1, bl2, br1, br2])
        
        # Subtle shadow/glow effect - secondary outline
        shadow = self.canvas.create_rectangle(
            box_x1 + 2, box_y1 + 2, box_x2 + 2, box_y2 + 2,
            outline=Colors.DIM,
            fill="",
            width=1
        )
        # Move shadow behind main rect
        self.canvas.tag_lower(shadow)
        self.target_box_rect.append(shadow)
        
        # Create text inside box (centered)
        text_x = box_x1 + (box_width // 2)
        text_y = box_y1 + (box_height // 2)
        
        self.target_box_text = self.canvas.create_text(
            text_x,
            text_y,
            text=self.confirmed_target,
            font=("Courier New", 10, "bold"),
            fill=Colors.TARGET,
            anchor="center"
        )
    
    def _execute_menu_option(self, option):
        """Execute menu option"""
        import os
        option_name = MenuOptions.OPTIONS.get(option, 'Invalid Option')
        
        # Clear previous feedback
        self._clear_feedback()
        
        # Execute based on option
        if option == '1':
            # Start Recon - check if target is set
            if not self.confirmed_target:
                # Show error feedback
                error_text = self.canvas.create_text(
                    450, 540,
                    text="[!] Please set a target first",
                    font=("Courier New", 11),
                    fill=Colors.INPUT,
                    anchor="center"
                )
                self.feedback_texts.append(error_text)
                return
            
            # Target is set, start recon
            self.ui.clear_menu()
            self.recon_executor.show_recon_screen(self.confirmed_target)
            
        elif option == '2':
            # Configure Tools
            self.ui.clear_menu()
            self.tools_config.show_config_menu()
            
        elif option == '3':
            # Open Notes - opens in separate window, don't clear menu
            self.notes_viewer.show_notes()
            
        elif option == '4':
            # Reset - delete all recon files, clear target, restore defaults
            import glob
            
            # Delete all _recon.txt files
            base_dir = os.getcwd()
            recon_files = glob.glob(os.path.join(base_dir, "*_recon.txt"))
            for file in recon_files:
                try:
                    os.remove(file)
                except:
                    pass
            
            # Reset config to defaults
            self.tools_config._set_defaults()
            self.tools_config.save_config()
            
            # Clear target
            self.confirmed_target = ""
            if self.target_box_rect:
                for rect_id in self.target_box_rect:
                    self.canvas.delete(rect_id)
                self.target_box_rect = []
            if self.target_box_text:
                self.canvas.delete(self.target_box_text)
                self.target_box_text = None
            
            # Show feedback
            feedback = self.canvas.create_text(
                450, 540,
                text="[✓] System reset complete",
                font=("Courier New", 11),
                fill=Colors.SECONDARY,
                anchor="center"
            )
            self.feedback_texts.append(feedback)
            
        elif option == '5':
            # Exit
            self.root.after(500, self.root.quit)
    
    def _clear_feedback(self):
        """Clear feedback texts from canvas"""
        for text_id in self.feedback_texts:
            self.canvas.delete(text_id)
        self.feedback_texts.clear()
