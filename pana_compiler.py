from antlr4 import *

from grammar.yaplLexer import yaplLexer
from grammar.yaplParser import yaplParser
from syntax_tree.customVisitor import CustomVisitor
from syntax_tree.treeValidatorVisitor import ValidatorVisitor
from error_module.error_handler import compiler_errors, CustomErrorListener, ErrorGenerator
from intermediate_code.intermediate_code_visitor import IntermediateCodeGenerator
from symbol_table_module.symbol_table import SymbolTable
from assembly.code_generator import CodeGenerator

PRINT_SYMBOL_TABLE = False

import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askopenfile

errores_encontrados = []
codigo_intermedio = []

class Lineas_UI(tk.Text):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)

        self.text_widget = text_widget
        self.text_widget.bind('<FocusIn>', self.on_key_press)

        self.insert(0.0, '')
        self.configure(state='disabled')

    def on_key_press(self, event=None):
        final_index = str(self.text_widget.index(tk.END))
        num_of_lines = final_index.split('.')[0]
        line_numbers_string = "\n".join(str(no + 1) for no in range(int(num_of_lines)))
        width = len(str(num_of_lines))

        self.configure(state='normal', width=width+1 if int(num_of_lines) < 10 else width)
        self.delete(1.0, tk.END)
        self.insert(1.0, line_numbers_string)
        self.configure(state='disabled')

def main(program):

    codigo_intermedio.clear()
    compiler_errors.clear()

    # INPUT CODE
    data = InputStream(program)

    # ERROR LISTENER
    custom_error_listener = CustomErrorListener()

    # SYMBOL TABLE
    symbol_table = SymbolTable()                            # Symbol table interacts with all compiler phases

    # LEXER SPECIFICATION
    lexer = yaplLexer(data)
    lexer.removeErrorListeners()
    lexer.addErrorListener(custom_error_listener)           # Custom error listener for lexical errors
    stream = CommonTokenStream(lexer)

    # PARSER SPECIFICATION
    parser = yaplParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(custom_error_listener)          # Custom error listeners for syntactic errors
    tree = parser.program()

    try:
        # SEMANTIC ANALYSIS

        # Symbol table population
        visitor = CustomVisitor(symbol_table)
        visitor.visit(tree)

        # ast analysis
        ast_visitor = ValidatorVisitor(symbol_table)
        ast_visitor.visit(tree)

        if PRINT_SYMBOL_TABLE:
            print(symbol_table)

        if not visitor.classTable.find_entry("Main"):
            ErrorGenerator("Class Main not defined")

        if not visitor.functionTable.find_by_name("main", "Main"):
            ErrorGenerator("Function main not defined in class Main")
    except Exception:
        ErrorGenerator("Incorrect program structure, check errors")


    # PRINTS ERRORS
    if len(compiler_errors) > 0:
        print("======ERRORS======")
        for error in compiler_errors:
            print(error)
            errores_encontrados.append(error)
            # terminal_cuadro.insert(tk.INSERT, error)
        errores_encontrados.append("Process finished with exit code -1")
    else:
        errores_encontrados.append("Process finished with exit code 0")

    # INTERMEDIATE CODE
    intermediate_code = "Pana, we found errors in your code, please fix them so that the intermediate code can be " \
                        "generated "

    # We generate the code only if there are no errors present
    if len(compiler_errors) == 0:
        code_generator = IntermediateCodeGenerator(symbol_table)

        # Shows empty string quotations when printing them
        code_generator.visual_empty_strings = True
        intermediate_code = code_generator.visit(tree)

    print(intermediate_code)
    codigo_intermedio.append(intermediate_code)


    # ASSEMBLY CODE (MIPS)
    code_generator = CodeGenerator(intermediate_code.code)
    print(code_generator.generate_code())


# FUNCTIONS UI

def abrir_archivo():
    codigo_cuadro.delete("1.0", "end")
    terminal_cuadro.delete("1.0", "end")
    tresDirecciones_cuadro.delete("1.0", "end")

    archivo = askopenfile(initialdir="./test_files", mode="r")
    contenido = archivo.read()
    codigo_cuadro.insert(tk.INSERT, contenido)

def ejecutar():
    terminal_cuadro.delete("1.0", "end")
    tresDirecciones_cuadro.delete("1.0", "end")
    errores_encontrados.clear()
    print(len(errores_encontrados))
    

    with open('test_files/temporal.cl', 'w') as f:
        contenido = codigo_cuadro.get('1.0', 'end-1c')
        f.write(contenido)

    with open('test_files/temporal.cl', 'r') as f2:
        # temp = FileStream('test_files/temporal.cl')
        lines = f2.read()
        main(lines)
        errores()

def errores():
    for i in errores_encontrados:
        terminal_cuadro.insert(tk.INSERT, i)
        terminal_cuadro.insert(INSERT, "\n")
    for i in codigo_intermedio:
        tresDirecciones_cuadro.insert(tk.INSERT, i)
        tresDirecciones_cuadro.insert(INSERT, "\n")

def scroll(*args):
    global codigo_cuadro, lineas_cuadro
    eval("codigo_cuadro.yview(*args)")
    eval("lineas_cuadro.yview(*args)")    

if __name__ == "__main__":
    with open('test_files/arithmetic_test.cl', 'r') as f:
        lines = f.read()
        main(lines)

# if __name__ == "__main__":
#     """
#     TEST FILES
#     prueba -> hello world!
#     arithmetic_test -> arithmetic and operator precedence
#     classes -> classes
#     lists -> lists
#     loops_and_conditional_test -> loops and conditionals
#     palindrome -> battery of all tests
#     fibonacci -> battery of all tests
#
#     TEST FOR ERRORS
#     add test_errors/errors_<filename>
#     gatitos_panas_ascii_art.cl -> easter egg error test
#     """
#
# #     with open('test_files/fibonacci.cl', 'r') as f:
# #         lines = f.read()
#
#
#
#
#
#     window = tk.Tk()
#     window.title("Proyecto Compiladores")
#     # window.state('zoomed')
#     window.geometry("1500x900")
#     window['background']='#89cff0'
#
#     correr_button = Button(window, text="Ejecutar", command=ejecutar)
#     correr_button.place(x=1200, y=50)
#     # correr_button.configure(background="#575366", fg="#ffffff")
#     abrir_button = Button(window, text="Seleccionar archivo", command=abrir_archivo)
#     abrir_button.place(x=1200, y=100)
#     # abrir_button.configure(background="#575366", fg="#ffffff")
#
#     text_scroll = Scrollbar(window, orient=VERTICAL, command=scroll)
#     text_scroll.place(x=1115, y=50, height=370, width=16)
#
#     codigo_cuadro = Text(window, width=130, height=23, background="#575366", foreground="#ffffff")
#     codigo_cuadro.place(x=70, y=50)
#     codigo_cuadro["yscrollcommand"] = text_scroll.set
#     lineas_cuadro = Lineas_UI(window, codigo_cuadro, width=2, height=23, background="#32292F", foreground="#ffffff")
#     lineas_cuadro.place(x=50, y=50)
#     lineas_cuadro["yscrollcommand"] = text_scroll.set
#
#     terminal_cuadro = Text(window, width=65, height=15, background="#575366", foreground="#ffffff")
#     terminal_cuadro.place(x=50, y=445)
#     tresDirecciones_cuadro = Text(window, width=65, height=15, background="#575366", foreground="#ffffff")
#     tresDirecciones_cuadro.place(x=600, y=445)
#
#
#
#     window.mainloop()



    