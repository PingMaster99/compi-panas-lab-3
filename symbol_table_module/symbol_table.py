from symbol_table_module.attributes import AttributeTable
from symbol_table_module.methods import MethodTable
from symbol_table_module.classes import ClassTable
from syntax_tree.type_system import TypeSystem


class SymbolTable:
    def __init__(self):
        self.functions = MethodTable()
        self.attributes = AttributeTable()
        self.types = TypeSystem()
        self.classes = ClassTable()

    def __repr__(self):

        return f"""
=======================================================
                    SYMBOL TABLE
=======================================================
                    
{self.classes}
{self.functions}
{self.attributes}
        """


