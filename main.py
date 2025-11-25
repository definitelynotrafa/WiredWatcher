import tkinter as tk
from PIL import Image, ImageTk
import random
import os


class SerialExperimentsRecon:
    def __init__(self, root):
        self.root = root
        self.root.title("wired://")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#000000")
        
        # Remove a barra de título (borderless)
        self.root.overrideredirect(True)
        
        # Fontes monoespaçadas
        try:
            self.font_title = ("Courier New", 16, "bold")
            self.font_menu = ("Courier New", 11)
            self.font_input = ("Courier New", 12)
            # Testa se a fonte existe
            tk.Label(root, font=self.font_title).destroy()
        except:
            self.font_title = ("Courier", 16, "bold")
            self.font_menu = ("Courier", 11)
            self.font_input = ("Courier", 12)
        
        # Canvas principal (terminal simulado)
        self.canvas = tk.Canvas(
            root,
            width=900,
            height=600,
            bg="#000000",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Cores CRT monocromáticas com toques de cor (esquema Lain)
        self.color_primary = "#00ff41"  # Matrix green
        self.color_secondary = "#ff6ec7"  # Soft pink
        self.color_accent = "#8b00ff"  # Purple accent
        self.color_text = "#c0c0c0"  # Silver/gray
        self.color_dim = "#606060"  # Dim gray
        self.color_target = "#6495ed"  # Azul Copland (cornflower blue)
        self.color_input = "#ff3333"  # Vermelho para input
        
        # Estado do terminal
        self.target_text = ""
        self.cursor_visible = True
        
        # GIF frames
        self.gif_frames = []
        self.current_frame = 0
        self.gif_label = None
        
        # Referências de texto
        self.target_text_id = None
        self.feedback_texts = []  # Lista para armazenar feedbacks
        self.menu_buttons = []  # Lista para armazenar áreas clicáveis dos botões
        self.input_x = 450  # Posição X fixa do input (centralizado)
        self.input_y = 0  # Será definido no draw_interface
        self.confirmation_symbol_id = None  # Símbolo de confirmação
        
        # Variáveis para arrastar a janela
        self.drag_x = 0
        self.drag_y = 0
        
        # Carrega e exibe tudo
        self.load_random_gif()
        self.draw_scanlines()
        self.draw_interface()
        self.start_animations()
        
        # Bind de teclado
        self.root.bind("<Key>", self.on_key_press)
        
        # Bind para fechar com ESC
        self.root.bind("<Escape>", lambda e: self.root.quit())
        
        # Bind de mouse para cliques
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
        # Bind para arrastar a janela
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
    
    def load_random_gif(self):
        """Carrega GIF aleatório da pasta assets/ sem distorção"""
        assets_path = os.path.join(os.path.dirname(__file__), "assets")
        
        # Procura GIFs
        gif_files = []
        if os.path.exists(assets_path):
            gif_files = [f for f in os.listdir(assets_path) if f.lower().endswith('.gif')]
        
        if not gif_files:
            # Se não houver GIFs, cria um placeholder
            self.create_placeholder_gif()
            return
        
        # Escolhe um GIF aleatório
        random_gif = random.choice(gif_files)
        gif_path = os.path.join(assets_path, random_gif)
        
        try:
            # Carrega GIF com PIL
            img = Image.open(gif_path)
            
            # Processa todos os frames
            frames = []
            try:
                while True:
                    # Redimensiona mantendo aspect ratio
                    frame = img.copy()
                    width, height = frame.size
                    
                    # Calcula novo tamanho mantendo proporções
                    max_width = 400
                    max_height = 200
                    
                    ratio = width / height
                    
                    # Ajusta pela largura
                    new_width = min(width, max_width)
                    new_height = int(new_width / ratio)
                    
                    # Se a altura ficar muito grande, ajusta pela altura
                    if new_height > max_height:
                        new_height = max_height
                        new_width = int(new_height * ratio)
                    
                    # Só redimensiona se necessário
                    if new_width != width or new_height != height:
                        frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Converte para PhotoImage
                    photo = ImageTk.PhotoImage(frame)
                    frames.append(photo)
                    
                    # Próximo frame
                    img.seek(img.tell() + 1)
            except EOFError:
                pass  # Fim dos frames
            
            self.gif_frames = frames
            
            # Exibe o primeiro frame centrado no topo
            if self.gif_frames:
                self.gif_label = self.canvas.create_image(
                    450, 120,  # Centrado horizontalmente, no topo
                    image=self.gif_frames[0],
                    anchor="center"
                )
        except Exception as e:
            print(f"Erro ao carregar GIF: {e}")
            self.create_placeholder_gif()
    
    def create_placeholder_gif(self):
        """Cria um placeholder se não houver GIFs"""
        # Cria imagem vazia com cor do tema
        img = Image.new('RGB', (400, 200), color='#1a1a1a')
        photo = ImageTk.PhotoImage(img)
        self.gif_frames = [photo]
        self.gif_label = self.canvas.create_image(
            450, 120,
            image=photo,
            anchor="center"
        )
    
    def draw_scanlines(self):
        """Desenha scanlines horizontais CRT"""
        # Scanlines mais visíveis e autênticas
        for y in range(0, 600, 2):
            self.canvas.create_line(
                0, y, 900, y,
                fill="#101010",
                width=1
            )
        
        # Borda simples
        self.canvas.create_rectangle(
            10, 10, 890, 590,
            outline=self.color_dim,
            width=1
        )
    
    def draw_interface(self):
        """Desenha toda a interface do terminal"""
        y_position = 250  # Começa após o GIF (mais espaço)
        
        # ASCII art separator
        separator = "─" * 70
        self.canvas.create_text(
            450, y_position,
            text=separator,
            font=self.font_menu,
            fill=self.color_dim,
            anchor="center"
        )
        
        y_position += 50
        
        # Menu com botões clicáveis
        menu_items = [
            "[1] Start Recon",
            "[2] Configure Tools",
            "[3] View Initial Checklist",
            "[4] Open Notes",
            "[5] Exit"
        ]
        
        for i, item in enumerate(menu_items):
            y_item = y_position + (i * 30)
            
            # Background do botão (retângulo)
            btn_bg = self.canvas.create_rectangle(
                320, y_item - 12,
                580, y_item + 12,
                outline=self.color_dim,
                fill="",
                width=1,
                tags=f"btn_{i+1}"
            )
            
            # Símbolo antes
            symbol = self.canvas.create_text(
                330, y_item,
                text="›",
                font=self.font_menu,
                fill=self.color_primary,
                anchor="w",
                tags=f"btn_{i+1}"
            )
            
            # Texto do botão
            text = self.canvas.create_text(
                345, y_item,
                text=item,
                font=self.font_menu,
                fill=self.color_text,
                anchor="w",
                tags=f"btn_{i+1}"
            )
            
            # Armazena informação do botão (y_min, y_max, option_number)
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
        
        y_position += 170
        
        # Separator antes do input
        self.canvas.create_text(
            450, y_position,
            text=separator,
            font=self.font_menu,
            fill=self.color_dim,
            anchor="center"
        )
        
        y_position += 30
        
        # Campo Target centralizado
        self.canvas.create_text(
            450, y_position,
            text="TARGET:",
            font=self.font_input,
            fill=self.color_secondary,
            anchor="center"
        )
        
        y_position += 25
        
        # Posição fixa do texto (centralizado)
        self.input_x = 450
        self.input_y = y_position
        
        # Linha de input centralizada
        self.target_text_id = self.canvas.create_text(
            self.input_x, self.input_y,
            text="",
            font=self.font_input,
            fill=self.color_input,  # Vermelho quando está a escrever
            anchor="center"
        )
    
    def start_animations(self):
        """Inicia todas as animações"""
        self.animate_gif()
        self.animate_flicker()
    
    def animate_gif(self):
        """Anima o GIF"""
        if self.gif_frames and self.gif_label:
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.canvas.itemconfig(self.gif_label, image=self.gif_frames[self.current_frame])
        
        # Próximo frame em 100ms
        self.root.after(100, self.animate_gif)
    
    def animate_flicker(self):
        """Anima o flicker suave CRT"""
        # Flicker mais subtil e realista
        flicker_intensity = random.choice([0, 1, 0, 0, 1, 0, 0, 0])
        if flicker_intensity:
            bg = "#0a0a0a"
        else:
            bg = "#000000"
        
        self.canvas.configure(bg=bg)
        
        # Próximo flicker em 100ms
        self.root.after(100, self.animate_flicker)
    
    def on_mouse_move(self, event):
        """Detecta movimento do mouse sobre os botões"""
        for btn in self.menu_buttons:
            if (btn['x_min'] <= event.x <= btn['x_max'] and 
                btn['y_min'] <= event.y <= btn['y_max']):
                # Mouse sobre o botão - destaca
                self.canvas.itemconfig(btn['rect_id'], outline=self.color_primary, width=2)
                self.canvas.itemconfig(btn['text_id'], fill=self.color_primary)
                self.canvas.config(cursor="hand2")
            else:
                # Mouse fora do botão - estado normal
                self.canvas.itemconfig(btn['rect_id'], outline=self.color_dim, width=1)
                self.canvas.itemconfig(btn['text_id'], fill=self.color_text)
        
        # Se não está sobre nenhum botão
        mouse_over_button = any(
            btn['x_min'] <= event.x <= btn['x_max'] and 
            btn['y_min'] <= event.y <= btn['y_max'] 
            for btn in self.menu_buttons
        )
        if not mouse_over_button:
            self.canvas.config(cursor="")
    
    def start_drag(self, event):
        """Inicia o arrasto da janela"""
        self.drag_x = event.x
        self.drag_y = event.y
    
    def on_drag(self, event):
        """Arrasta a janela"""
        # Calcula nova posição
        x = self.root.winfo_x() + (event.x - self.drag_x)
        y = self.root.winfo_y() + (event.y - self.drag_y)
        
        # Move a janela
        self.root.geometry(f"+{x}+{y}")
    
    def on_canvas_click(self, event):
        """Detecta cliques nos botões"""
        for btn in self.menu_buttons:
            if (btn['x_min'] <= event.x <= btn['x_max'] and 
                btn['y_min'] <= event.y <= btn['y_max']):
                # Clicou no botão - limpa feedbacks primeiro
                for text_id in self.feedback_texts:
                    self.canvas.delete(text_id)
                self.feedback_texts.clear()
                
                # Executa opção
                self.execute_menu_option(btn['option'])
                break
    
    def on_key_press(self, event):
        """Handler de teclado"""
        if event.keysym == "Return":
            # Enter pressionado
            if self.target_text.strip():
                # Limpa feedbacks anteriores
                for text_id in self.feedback_texts:
                    self.canvas.delete(text_id)
                self.feedback_texts.clear()
                
                # Processa o comando (NÃO limpa o target_text)
                self.process_command(self.target_text)
                # Não limpa: self.target_text = ""
                
        elif event.keysym == "BackSpace":
            # Remove último caractere
            self.target_text = self.target_text[:-1]
            # Volta ao vermelho quando edita
            self.canvas.itemconfig(self.target_text_id, fill=self.color_input)
            
        elif len(event.char) == 1 and event.char.isprintable():
            # Adiciona caractere ao target (permite 1-5 quando já há texto)
            self.target_text += event.char
            # Mantém vermelho quando está a escrever
            self.canvas.itemconfig(self.target_text_id, fill=self.color_input)
        
        # Atualiza o texto no canvas
        if self.target_text_id:
            self.canvas.itemconfig(self.target_text_id, text=self.target_text)
    
    def process_command(self, command):
        """Processa comando digitado no target"""
        # Remove símbolo anterior se existir
        if self.confirmation_symbol_id:
            self.canvas.delete(self.confirmation_symbol_id)
        
        # Muda a cor do target para azul Copland (confirmado)
        self.canvas.itemconfig(self.target_text_id, fill=self.color_target)
        
        # Mostra símbolo de confirmação ao lado do target
        self.confirmation_symbol_id = self.canvas.create_text(
            self.input_x + 150,
            self.input_y,
            text="✓",
            font=("Courier New", 16, "bold"),
            fill=self.color_target,
            anchor="w"
        )
        
        # Remove o símbolo após 2 segundos
        self.root.after(2000, lambda: self.canvas.delete(self.confirmation_symbol_id) if self.confirmation_symbol_id else None)
    
    def execute_menu_option(self, option):
        """Executa opção do menu"""
        menu_options = {
            '1': 'Start Recon',
            '2': 'Configure Tools',
            '3': 'View Initial Checklist',
            '4': 'Open Notes',
            '5': 'Exit'
        }
        
        option_name = menu_options.get(option, 'Invalid Option')
        
        # Limpa feedbacks anteriores
        for text_id in self.feedback_texts:
            self.canvas.delete(text_id)
        self.feedback_texts.clear()
        
        # Não mostra mais feedback visual (removido)
        
        # Se for opção 5 (Sair), fecha o programa
        if option == '5':
            self.root.after(500, self.root.quit)
    
    def run(self):
        """Inicia o loop principal"""
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = SerialExperimentsRecon(root)
    app.run()
