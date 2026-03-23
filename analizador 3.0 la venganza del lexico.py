import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import re
from datetime import datetime

#Se rompe en piezas el texto de entrada, identifica tokens, errores y los muestra en una tabla.
class LexicalAnalyzer:
    def __init__(self): # Define las palabras reservadas, operadores y delimitadores que el analizador reconocerá.
        self.reserved = {"var", "if", "else", "print"}  
        self.operators = {"+", "-", "*", "/", "=", "==", "<", ">"}
        self.delimiters = {"(", ")", "{", "}", ";", "."}
# Analiza el texto de entrada, identifica tokens válidos y errores, y devuelve ambos.
    
    #lista de tokens y errores
class LexicalAnalyzer:
    def __init__(self): 
        self.reserved = {"var", "if", "else", "print"}  
        self.operators = {"+", "-", "*", "/", "=", "==", "<", ">"}
        self.delimiters = {"(", ")", "{", "}", ";"}

    def analyze(self, text):
        tokens = [] 
        errors = [] 


        import re
        delim_pattern = "|".join(re.escape(d) for d in self.delimiters)
        
        if not delim_pattern:
            delim_pattern = r"(?!)"

        patterns = [ 
            ("NUMERO", r"\b[0-9]+\b"),
            ("IDENTIFICADOR", r"\b[a-zA-Z][a-zA-Z0-9]*\b"),
            ("OPERADOR", r"==|\+|\-|\*|\/|=|<|>"),
            ("DELIMITADOR", delim_pattern) 
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

# Interfaz
class App:
    def __init__(self, root):
        self.analyzer = LexicalAnalyzer() 
        self.root = root 
        self.root.title("Analizador Léxico") # Título de la ventana

        self.text_input = tk.Text(root, height=10) # Área de texto para ingresar el código a analizar
        self.text_input.pack() 

        tk.Button(root, text="Analizar", command=self.run_analysis).pack() # Botón para ejecutar el análisis

        self.tree = ttk.Treeview(root, columns=("Token", "Tipo"), show='headings') # Tabla para mostrar los tokens encontrados y su tipo.
        self.tree.heading("Token", text="Token") 
        self.tree.heading("Tipo", text="Tipo") 
        self.tree.pack() 

        self.info_label = tk.Label(root, text="") 
        self.info_label.pack()


        # se inicia logica para el CRUD 

        self.menu = tk.Menu(root)
        root.config(menu=self.menu) # Agrega el menú a la ventana principal

        config_menu = tk.Menu(self.menu, tearoff=0) 
        self.menu.add_cascade(label="CRUD Tokens", menu=config_menu) # Agrega el submenú "CRUD Tokens"

        # CRUD PARA PALABRAS RESERVADAS
        config_menu.add_command(label="Agregar Reservada", command=self.add_reserved) 
        config_menu.add_command(label="Eliminar Reservada", command=self.remove_reserved) 
        config_menu.add_command(label="Modificar Reservada", command=self.modify_reserved) 

            # CRUD PARA DELIMITADORES
        config_menu.add_command(label="Agregar Delimitador", command=self.add_delimiter) 
        config_menu.add_command(label="Eliminar Delimitador", command=self.remove_delimiter) 
        config_menu.add_command(label="Modificar Delimitador", command=self.modify_delimiter) 


    def add_reserved(self): 
        word = simpledialog.askstring("Agregar", "Nueva palabra reservada:") 
        if word:
            self.analyzer.reserved.add(word) 

    def remove_reserved(self):
        word = simpledialog.askstring("Eliminar", "Palabra reservada a eliminar:") 
        if word in self.analyzer.reserved: 
            self.analyzer.reserved.remove(word) 

    def modify_reserved(self): 
        old = simpledialog.askstring("Modificar", "Palabra actual:") # Muestra un cuadro para ingresar la palabra reservada actual.
        if old in self.analyzer.reserved: 
            new = simpledialog.askstring("Modificar", "Nueva palabra:") # Muestra un cuadro para ingresar la nueva palabra reservada.
            self.analyzer.reserved.remove(old) 
            self.analyzer.reserved.add(new) 

    def add_delimiter(self): # Solicita al usuario ingresar un nuevo delimitador
        d = simpledialog.askstring("Agregar", "Nuevo delimitador:") 
        if d:
            self.analyzer.delimiters.add(d) # Si se ingresó un delimitador, se agrega al conjunto de delimitadores del analizador.

    def remove_delimiter(self): # Solicita al usuario ingresar un delimitador a eliminar.
        d = simpledialog.askstring("Eliminar", "Delimitador a eliminar:") 
        if d in self.analyzer.delimiters:
            self.analyzer.delimiters.remove(d) # Si el delimitador ingresado no existe, no se realiza ninguna acción.

#   Solicita al usuario ingresar el delimitador actual y el nuevo delimitador para modificarlo.
    def modify_delimiter(self): 
        old = simpledialog.askstring("Modificar", "Delimitador actual:") # Muestra un cuadro para ingresar el delimitador actual.
        if old in self.analyzer.delimiters: 
            new = simpledialog.askstring("Modificar", "Nuevo delimitador:") # Muestra un cuadro para ingresar el nuevo delimitador.
            self.analyzer.delimiters.remove(old)
            self.analyzer.delimiters.add(new) 

    def run_analysis(self): # Obtiene el texto ingresado en el área de texto, lo analiza utilizando el analizador léxico, muestra los tokens encontrados en la tabla, actualiza la etiqueta de información con la cantidad de tokens válidos y el estado de la cadena, exporta los resultados a un archivo de texto, y muestra una advertencia si se encontraron errores.
        text = self.text_input.get("1.0", tk.END) 
        tokens, errors = self.analyzer.analyze(text) # Analiza el texto utilizando el método analyze del analizador léxico, obteniendo una lista de tokens encontrados y una lista de errores.

        for i in self.tree.get_children():
            self.tree.delete(i)

# Inserta los tokens encontrados en la tabla de la interfaz.
        valid_count = 0
        for token, ttype in tokens: 
            self.tree.insert('', 'end', values=(token, ttype)) # Inserta cada token encontrado en la tabla de la interfaz, mostrando el token y su tipo.
            if ttype != "ERROR": # Si el tipo del token no es "ERROR", se considera un token válido y se incrementa el contador de tokens válidos.
                valid_count += 1


# Determina el estado de la cadena como "VÁLIDA" si no se encontraron errores, o "INVÁLIDA" si se encontraron errores.
        estado = "VÁLIDA" if not errors else "INVÁLIDA" # Si no se encontraron errores, el estado de la cadena se considera "VÁLIDA". Si se encontraron errores, el estado de la cadena se considera "INVÁLIDA".
        self.info_label.config(text=f"Tokens válidos: {valid_count} | Cadena: {estado}") # Actualiza la información con la cantidad de tokens válidos.

        self.export_txt(text, tokens, errors) # Exporta el resultado del análisis a un archivo de texto.

        if errors:
            messagebox.showwarning("Error", f"Caracteres no válidos: {errors}") # Si se encontraron errores, muestra una advertencia con los caracteres no válidos.

     #Estructura del archivo de guardao de resultados de las cadenas insertadas, tokens encontrados y errores si los hay.
        #--- ANALISIS ---
    def export_txt(self, text, tokens, errors): # Exporta el resultado del análisis a un .txt
        with open("resultado.txt", "a") as f:  
            f.write("\n--- ANALISIS ---\n")
            f.write(f"Fecha: {datetime.now()}\n")
            f.write(f"Entrada: {text}\n")
            f.write("Tokens:\n") 
            for token, ttype in tokens:
                f.write(f"{token} -> {ttype}\n")
            if errors:  # Escribe si hay errores.
                f.write(f"Errores: {errors}\n") 
            f.write("----------------\n")

# Punto de entrada del programa
if __name__ == "__main__": 
    root = tk.Tk()
    app = App(root)
    root.mainloop() 