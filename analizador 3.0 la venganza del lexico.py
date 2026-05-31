import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from datetime import datetime
import re
import csv
import os


class LexicalAnalyzer:
    def __init__(self):
        self.reserved = {"var", "if", "else", "print"}
        self.operators = {"+", "-", "*", "/", "=", "==", "<", ">"}
        self.delimiters = {"(", ")", "{", "}", ";"}

    def load_tokens_from_csv(self, csv_file):
        duplicated_tokens = []
        loaded_tokens = []

        required_columns = {"category", "value"}

        try:
            with open(csv_file, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                if reader.fieldnames is None:
                    raise ValueError("El archivo CSV está vacío.")

                columns = {col.strip().lower() for col in reader.fieldnames}

                if not required_columns.issubset(columns):
                    raise ValueError(
                        "El CSV debe contener las columnas: category,value"
                    )

                seen_in_file = set()

                for row_num, row in enumerate(reader, start=2):
                    category = row["category"].strip().lower()
                    value = row["value"].strip()

                    if not value:
                        continue

                    # Duplicado dentro del mismo CSV
                    if value in seen_in_file:
                        duplicated_tokens.append(
                            f"{value} (duplicado en CSV)"
                        )
                        continue

                    seen_in_file.add(value)

                    # Duplicado respecto a los existentes
                    exists = (
                        value in self.reserved or
                        value in self.operators or
                        value in self.delimiters
                    )

                    if exists:
                        duplicated_tokens.append(
                            f"{value} (ya existente)"
                        )
                        continue

                    if category == "reserved":
                        self.reserved.add(value)
                        loaded_tokens.append(value)

                    elif category == "operators":
                        self.operators.add(value)
                        loaded_tokens.append(value)

                    elif category == "delimiters":
                        self.delimiters.add(value)
                        loaded_tokens.append(value)

                    else:
                        raise ValueError(
                            f"Categoría inválida '{category}' en línea {row_num}"
                        )

                return {
                    "success": True,
                    "loaded": loaded_tokens,
                    "duplicates": duplicated_tokens
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def analyze(self, text):
        tokens = []
        errors = []

        operator_pattern = "|".join(
            sorted(
                (re.escape(op) for op in self.operators),
                key=len,
                reverse=True
            )
        )

        delimiter_pattern = "|".join(
            sorted(
                (re.escape(d) for d in self.delimiters),
                key=len,
                reverse=True
            )
        )

        patterns = [
            ("NUMERO", r"\b[0-9]+\b"),
            ("IDENTIFICADOR", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
            ("OPERADOR", operator_pattern if operator_pattern else r"(?!)"),
            ("DELIMITADOR", delimiter_pattern if delimiter_pattern else r"(?!)")
        ]

        index = 0

        while index < len(text):

            if text[index].isspace():
                index += 1
                continue

            match = None

            for token_type, pattern in patterns:
                regex = re.compile(pattern)
                match = regex.match(text, index)

                if match:
                    value = match.group(0)

                    if (
                        token_type == "IDENTIFICADOR"
                        and value in self.reserved
                    ):
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
        self.root.geometry("800x600")

        self.text_input = tk.Text(root, height=10)
        self.text_input.pack(fill="x", padx=10, pady=10)

        tk.Button(
            root,
            text="Analizar",
            command=self.run_analysis
        ).pack(pady=5)

        self.tree = ttk.Treeview(
            root,
            columns=("Token", "Tipo"),
            show="headings"
        )

        self.tree.heading("Token", text="Token")
        self.tree.heading("Tipo", text="Tipo")

        self.tree.column("Token", width=250)
        self.tree.column("Tipo", width=250)

        self.tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.info_label = tk.Label(
            root,
            text="Esperando análisis..."
        )
        self.info_label.pack(pady=5)

        self.menu = tk.Menu(root)
        root.config(menu=self.menu)

        config_menu = tk.Menu(self.menu, tearoff=0)

        self.menu.add_cascade(
            label="CRUD Tokens",
            menu=config_menu
        )

        config_menu.add_command(
            label="Agregar Reservada",
            command=self.add_reserved
        )

        config_menu.add_command(
            label="Eliminar Reservada",
            command=self.remove_reserved
        )

        config_menu.add_command(
            label="Modificar Reservada",
            command=self.modify_reserved
        )

        config_menu.add_separator()

        config_menu.add_command(
            label="Agregar Delimitador",
            command=self.add_delimiter
        )

        config_menu.add_command(
            label="Eliminar Delimitador",
            command=self.remove_delimiter
        )

        config_menu.add_command(
            label="Modificar Delimitador",
            command=self.modify_delimiter
        )

        config_menu.add_separator()

        config_menu.add_command(
            label="Cargar Tokens desde CSV",
            command=self.load_csv_tokens
        )

    def load_csv_tokens(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("CSV Files", "*.csv")]
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".csv"):
            messagebox.showerror(
                "Archivo no admitido",
                "Solo se permiten archivos CSV."
            )
            return

        result = self.analyzer.load_tokens_from_csv(file_path)

        if not result["success"]:
            messagebox.showerror(
                "Error de formato CSV",
                result["error"]
            )
            return

        message = (
            f"Archivo cargado correctamente.\n\n"
            f"Tokens agregados: {len(result['loaded'])}"
        )

        if result["duplicates"]:
            message += (
                "\n\nTokens duplicados encontrados:\n\n"
                + "\n".join(result["duplicates"])
            )

            messagebox.showwarning(
                "Carga completada con duplicados",
                message
            )
        else:
            messagebox.showinfo(
                "Archivo cargado",
                message
            )

    def add_reserved(self):
        word = simpledialog.askstring(
            "Agregar",
            "Nueva palabra reservada:"
        )

        if word:
            self.analyzer.reserved.add(word)

    def remove_reserved(self):
        word = simpledialog.askstring(
            "Eliminar",
            "Palabra reservada a eliminar:"
        )

        if word in self.analyzer.reserved:
            self.analyzer.reserved.remove(word)

    def modify_reserved(self):
        old = simpledialog.askstring(
            "Modificar",
            "Palabra actual:"
        )

        if old in self.analyzer.reserved:
            new = simpledialog.askstring(
                "Modificar",
                "Nueva palabra:"
            )

            if new:
                self.analyzer.reserved.remove(old)
                self.analyzer.reserved.add(new)

    def add_delimiter(self):
        d = simpledialog.askstring(
            "Agregar",
            "Nuevo delimitador:"
        )

        if d:
            self.analyzer.delimiters.add(d)

    def remove_delimiter(self):
        d = simpledialog.askstring(
            "Eliminar",
            "Delimitador a eliminar:"
        )

        if d in self.analyzer.delimiters:
            self.analyzer.delimiters.remove(d)

    def modify_delimiter(self):
        old = simpledialog.askstring(
            "Modificar",
            "Delimitador actual:"
        )

        if old in self.analyzer.delimiters:
            new = simpledialog.askstring(
                "Modificar",
                "Nuevo delimitador:"
            )

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
            self.tree.insert(
                "",
                "end",
                values=(token, token_type)
            )

            if token_type != "ERROR":
                valid_count += 1

        estado = "VÁLIDA" if not errors else "INVÁLIDA"

        self.info_label.config(
            text=f"Tokens válidos: {valid_count} | Cadena: {estado}"
        )

        self.export_txt(text, tokens, errors)

        if errors:
            messagebox.showwarning(
                "Caracteres inválidos",
                f"Se encontraron los siguientes errores:\n{errors}"
            )

    def export_txt(self, text, tokens, errors):
        with open(
            "resultado.txt",
            "a",
            encoding="utf-8"
        ) as f:

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