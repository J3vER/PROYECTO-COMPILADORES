import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from datetime import datetime
import re
import csv

class LexicalAnalyzer:
    def __init__(self):
        self.reserved = {"var", "if", "else", "print"}
        self.operators = {"+", "-", "*", "/", "=", "==", "<", ">"}
        self.delimiters = {"(", ")", "{", "}", ";"}

    def load_tokens_from_csv(self, csv_file):
        self.reserved.clear()
        self.operators.clear()
        self.delimiters.clear()

        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                category = row["category"].strip().lower()
                value = row["value"].strip()

                if category == "reserved":
                    self.reserved.add(value)
                elif category == "operators":
                    self.operators.add(value)
                elif category == "delimiters":
                    self.delimiters.add(value)

    def analyze(self, text):
        tokens = []
        errors = []

        operator_pattern = "|".join(
            sorted((re.escape(op) for op in self.operators), key=len, reverse=True)
        )

        delimiter_pattern = "|".join(
            sorted((re.escape(d) for d in self.delimiters), key=len, reverse=True)
        )

        patterns = [
            ("NUMERO", r"\b[0-9]+\b"),
            ("IDENTIFICADOR", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
            ("OPERADOR", operator_pattern if operator_pattern else r"(?!)"),
            ("DELIMITADOR", delimiter_pattern if delimiter_pattern else r"(?!)")
        ]

        compiled_patterns = [(token_type, re.compile(pattern)) for token_type, pattern in patterns]

        index = 0

        while index < len(text):
            if text[index].isspace():
                index += 1
                continue

            match = None

            for token_type, regex in compiled_patterns:
                match = regex.match(text, index)

                if match:
                    value = match.group(0)

                    if token_type == "IDENTIFICADOR" and value in self.reserved:
                        token_type = "RESERVADA"

                    tokens.append((value, token_type))
                    index = match.end()
                    break

            if not match:
                errors.append(text[index])
                tokens.append((text[index], "ERROR"))
                index += 1

        return tokens, errors


class App:
    def __init__(self, root):
        self.analyzer = LexicalAnalyzer()
        self.root = root
        self.root.title("Analizador Léxico con CSV")

        self.text_input = tk.Text(root, height=10)
        self.text_input.pack(fill="x")

        # Contenedor para botones principales (Analizar y Ver Gramática)
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Analizar", command=self.run_analysis).pack(side="left", padx=5)
        
        # NUEVO: Botón permanente en la interfaz para reabrir la consulta de tokens
        tk.Button(button_frame, text="Ver Tokens Activos", command=self.show_loaded_tokens).pack(side="left", padx=5)

        self.tree = ttk.Treeview(root, columns=("Token", "Tipo"), show="headings")
        self.tree.heading("Token", text="Token")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.pack(fill="both", expand=True)

        self.info_label = tk.Label(root, text="")
        self.info_label.pack()

        self.menu = tk.Menu(root)
        root.config(menu=self.menu)

        config_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="CRUD Tokens", menu=config_menu)

        config_menu.add_command(label="Agregar Reservada", command=self.add_reserved)
        config_menu.add_command(label="Eliminar Reservada", command=self.remove_reserved)
        config_menu.add_command(label="Modificar Reservada", command=self.modify_reserved)

        config_menu.add_separator()

        config_menu.add_command(label="Agregar Delimitador", command=self.add_delimiter)
        config_menu.add_command(label="Eliminar Delimitador", command=self.remove_delimiter)
        config_menu.add_command(label="Modificar Delimitador", command=self.modify_delimiter)

        config_menu.add_separator()

        config_menu.add_command(
            label="Cargar Tokens desde CSV",
            command=self.load_csv_tokens
        )
        
        # NUEVO: Opción agregada al menú desplegable para mayor accesibilidad
        config_menu.add_command(
            label="Ver Tokens Activos",
            command=self.show_loaded_tokens
        )

    def load_csv_tokens(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar CSV",
            filetypes=[("CSV Files", "*.csv")]
        )

        if file_path:
            self.analyzer.load_tokens_from_csv(file_path)
            messagebox.showinfo(
                "Carga exitosa",
                "Tokens cargados correctamente desde CSV."
            )
            self.show_loaded_tokens()

    def show_loaded_tokens(self):
        info_window = tk.Toplevel(self.root)
        info_window.title("Resumen de Gramática Cargada")
        info_window.geometry("450x350")
        info_window.transient(self.root)  
        info_window.grab_set()         

        text_frame = ttk.Frame(info_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        display_text = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set, font=("Consolas", 10))
        display_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=display_text.yview)

        reporte = "=========================================\n"
        reporte += "       TOKENS ACTUALMENTE ACTIVOS        \n"
        reporte += "=========================================\n\n"

        reporte += f"▶ PALABRAS RESERVADAS ({len(self.analyzer.reserved)}):\n"
        reporte += (", ".join(sorted(self.analyzer.reserved)) if self.analyzer.reserved else "Ninguna") + "\n\n"

        reporte += f"▶ OPERADORES ({len(self.analyzer.operators)}):\n"
        reporte += (", ".join(sorted(self.analyzer.operators)) if self.analyzer.operators else "Ninguno") + "\n\n"

        reporte += f"▶ DELIMITADORES ({len(self.analyzer.delimiters)}):\n"
        reporte += (", ".join(sorted(self.analyzer.delimiters)) if self.analyzer.delimiters else "Ninguno") + "\n\n"
        reporte += "========================================="

        display_text.insert("1.0", reporte)
        display_text.config(state="disabled")

        ttk.Button(info_window, text="Entendido", command=info_window.destroy).pack(pady=5)

    def add_reserved(self):
        word = simpledialog.askstring("Agregar", "Nueva palabra reservada:")
        if word:
            self.analyzer.reserved.add(word)

    def remove_reserved(self):
        word = simpledialog.askstring("Eliminar", "Palabra reservada a eliminar:")
        if word in self.analyzer.reserved:
            self.analyzer.reserved.remove(word)

    def modify_reserved(self):
        old = simpledialog.askstring("Modificar", "Palabra actual:")
        if old in self.analyzer.reserved:
            new = simpledialog.askstring("Modificar", "Nueva palabra:")
            if new:
                self.analyzer.reserved.remove(old)
                self.analyzer.reserved.add(new)

    def add_delimiter(self):
        d = simpledialog.askstring("Agregar", "Nuevo delimitador:")
        if d:
            self.analyzer.delimiters.add(d)

    def remove_delimiter(self):
        d = simpledialog.askstring("Eliminar", "Delimitador a eliminar:")
        if d in self.analyzer.delimiters:
            self.analyzer.delimiters.remove(d)

    def modify_delimiter(self):
        old = simpledialog.askstring("Modificar", "Delimitador actual:")
        if old in self.analyzer.delimiters:
            new = simpledialog.askstring("Modificar", "Nuevo delimitador:")
            if new:
                self.analyzer.delimiters.remove(old)
                self.analyzer.delimiters.add(new)

    def run_analysis(self):
        text = self.text_input.get("1.0", tk.END)

        tokens, errors = self.analyzer.analyze(text)

        for item in self.tree.get_children():
            self.tree.delete(item)

        valid_count = 0

        for token, token_type in tokens:
            self.tree.insert("", "end", values=(token, token_type))

            if token_type != "ERROR":
                valid_count += 1

        estado = "VÁLIDA" if not errors else "INVÁLIDA"

        self.info_label.config(
            text=f"Tokens válidos: {valid_count} | Cadena: {estado}"
        )

        self.export_txt(text, tokens, errors)

        if errors:
            messagebox.showwarning(
                "Error",
                f"Caracteres no válidos: {errors}"
            )

    def export_txt(self, text, tokens, errors):
        with open("resultado.txt", "a", encoding="utf-8") as f:
            f.write("\n--- ANALISIS ---\n")
            f.write(f"Fecha: {datetime.now()}\n")
            f.write(f"Entrada: {text}\n")
            f.write("Tokens:\n")

            for token, token_type in tokens:
                f.write(f"{token} -> {token_type}\n")

            if errors:
                f.write(f"Errores: {errors}\n")

            f.write("----------------\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()