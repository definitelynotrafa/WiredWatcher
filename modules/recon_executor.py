"""
Recon execution screen - runs nmap and fuzzer tools
"""
import subprocess
import threading
import os
from modules.config import Colors, Dimensions


class ReconExecutor:
    """Handles reconnaissance execution and output display"""
    
    def __init__(self, canvas, fonts, root, tools_config):
        """
        Initialize recon executor
        
        Args:
            canvas: tkinter Canvas object
            fonts: dict with font configurations
            root: tkinter root window
            tools_config: ToolsConfig instance
        """
        self.canvas = canvas
        self.fonts = fonts
        self.root = root
        self.tools_config = tools_config
        
        # Output file (set dynamically per target)
        self.output_file = None
        self.current_target = None
        
        # UI elements
        self.recon_elements = []
        self.output_lines = []
        self.scroll_offset = 0
        self.max_visible_lines = 22
        
        # Execution state
        self.is_running = False
        self.processes = []
    
    def show_recon_screen(self, target):
        """Display the recon execution screen"""
        # Clear existing elements
        self.clear_recon_screen()
        
        y_position = 260
        
        # Title
        title = self.canvas.create_text(
            450, y_position,
            text="startRecon://",
            font=self.fonts['title'],
            fill=Colors.PRIMARY,
            anchor="center"
        )
        self.recon_elements.append(title)
        
        y_position += 50
        
        # Output area background
        output_box = self.canvas.create_rectangle(
            50, y_position,
            850, y_position + 250,
            outline=Colors.PRIMARY,
            fill=Colors.BACKGROUND,
            width=2
        )
        self.recon_elements.append(output_box)
        
        # Start execution
        self._start_recon(target)
    
    def _start_recon(self, target):
        """Start reconnaissance in background thread"""
        self.is_running = True
        self.current_target = target
        
        # Set output file based on target name
        # Clean target name for filename (remove http://, https://, etc)
        clean_target = target.replace('http://', '').replace('https://', '').replace('/', '_').replace(':', '_')
        self.output_file = os.path.join(os.getcwd(), f"{clean_target}_recon.txt")
        
        # Clear output file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(f"=== RECON STARTED FOR {target} ===\n\n")
        
        # Start in thread to not block UI
        thread = threading.Thread(target=self._run_recon, args=(target,))
        thread.daemon = True
        thread.start()
    
    def _run_recon(self, target):
        """Run reconnaissance commands"""
        # Get config
        nmap_cmd = self.tools_config.nmap_command
        wordlist_path = os.path.expanduser(self.tools_config.wordlist_path)
        fuzzer = self.tools_config.fuzzer_choice
        
        if fuzzer == "gobuster":
            fuzzer_cmd = self.tools_config.gobuster_command
        else:
            fuzzer_cmd = self.tools_config.ffuf_command
        
        # Add target to nmap command
        nmap_cmd = f"{nmap_cmd} {target} -vvv"
        
        # Add target to fuzzer command (insert -u <target> at the beginning)
        if fuzzer == "gobuster":
            fuzzer_cmd = fuzzer_cmd.replace("gobuster dir", f"gobuster dir -u {target}")
        elif fuzzer == "ffuf":
            # For ffuf, add -u at the beginning if not present
            if "-u " not in fuzzer_cmd:
                fuzzer_cmd = f"ffuf -u {target} {fuzzer_cmd}"
        
        fuzzer_cmd = fuzzer_cmd.replace("wordlist.txt", wordlist_path)
        
        # Run nmap
        self._add_output(f"[*] Starting Nmap scan...\n", Colors.PRIMARY)
        self._add_output(f"[*] Command: {nmap_cmd}\n\n", Colors.TEXT)
        
        try:
            # Run nmap with real-time output
            process = subprocess.Popen(
                nmap_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            self.processes.append(process)
            
            for line in process.stdout:
                if not self.is_running:
                    process.kill()
                    break
                self._add_output(line, Colors.TEXT)
            
            process.wait()
            self._add_output(f"\n[✓] Nmap scan completed\n\n", Colors.PRIMARY)
            
        except Exception as e:
            self._add_output(f"[!] Nmap error: {str(e)}\n\n", Colors.INPUT)
        
        # Run fuzzer
        if fuzzer_cmd:
            self._add_output(f"[*] Starting {fuzzer.upper()} scan...\n", Colors.PRIMARY)
            self._add_output(f"[*] Command: {fuzzer_cmd}\n\n", Colors.TEXT)
            
            try:
                process = subprocess.Popen(
                    fuzzer_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                self.processes.append(process)
                
                for line in process.stdout:
                    if not self.is_running:
                        process.kill()
                        break
                    self._add_output(line, Colors.TEXT)
                
                process.wait()
                self._add_output(f"\n[✓] {fuzzer.upper()} scan completed\n\n", Colors.PRIMARY)
                
            except Exception as e:
                self._add_output(f"[!] {fuzzer.upper()} error: {str(e)}\n\n", Colors.INPUT)
        
        self._add_output(f"\n=== RECON COMPLETED ===\n", Colors.SECONDARY)
        self._add_output(f"[*] Results saved to: {self.output_file}\n", Colors.TEXT)
        self.is_running = False
    
    def _add_output(self, text, color):
        """Add output line to display and file"""
        # Save to file
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(text)
        
        # Check if we're at the bottom before adding new lines
        total_lines = len(self.output_lines)
        at_bottom = (self.scroll_offset == 0)
        
        # Split text into lines and add each as separate entry
        lines = text.split('\n')
        for line in lines:
            if line or text.endswith('\n'):  # Include empty lines if original had newline
                self.output_lines.append({'text': line, 'color': color})
        
        # If we were at the bottom, stay at the bottom (auto-scroll)
        if at_bottom:
            self.scroll_offset = 0
        
        # Update display on main thread (using after_idle for better performance)
        self.root.after_idle(self._update_display)
    
    def _update_display(self):
        """Update the output display"""
        # Clear old text elements only (keep title and box)
        for elem in self.recon_elements[2:]:
            self.canvas.delete(elem)
        self.recon_elements = self.recon_elements[:2]
        
        # Calculate start and end indices based on scroll offset
        total_lines = len(self.output_lines)
        
        # Clamp scroll offset
        max_scroll = max(0, total_lines - self.max_visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        
        # Get visible slice
        start_idx = total_lines - self.max_visible_lines - self.scroll_offset
        end_idx = total_lines - self.scroll_offset
        
        # Ensure u don't go below 0
        start_idx = max(0, start_idx)
        
        visible_lines = self.output_lines[start_idx:end_idx]
        
        # Display visible lines
        y_start = 315
        
        for i, line_info in enumerate(visible_lines):
            # Truncate very long lines
            display_text = line_info['text']
            if len(display_text) > 110:
                display_text = display_text[:107] + "..."
            
            text_elem = self.canvas.create_text(
                60, y_start + (i * 11),
                text=display_text,
                font=("Courier New", 9),
                fill=line_info['color'],
                anchor="w"
            )
            self.recon_elements.append(text_elem)
    
    def scroll(self, amount):
        """Scroll the output display"""
        self.scroll_offset += amount
        self._update_display()
    
    def stop_recon(self):
        """Stop running reconnaissance"""
        self.is_running = False
        for process in self.processes:
            try:
                process.kill()
            except:
                pass
        self.processes.clear()
    
    def clear_recon_screen(self):
        """Clear recon screen elements"""
        for element in self.recon_elements:
            self.canvas.delete(element)
        self.recon_elements.clear()
    
    def is_active(self):
        """Check if recon screen is active"""
        return len(self.recon_elements) > 0
