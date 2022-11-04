from symbol_table_module.table_entry_types import MethodEntry


class MethodTable:
    def __init__(self):
        self.entries = []
        self.entries.append(MethodEntry(1, "abort", "Object", 1, "Object"))
        self.entries.append(MethodEntry(2, "type_name", "String", 1, "Object"))
        self.entries.append(MethodEntry(3, "copy", "Object", 1, "Object"))
        self.entries.append(MethodEntry(4, "out_string", "IO", 1, "IO"))
        self.entries.append(MethodEntry(5, "out_int", "IO", 1, "IO"))
        self.entries.append(MethodEntry(6, "in_string", "String", 1, "IO"))
        self.entries.append(MethodEntry(7, "in_int", "Int", 1, "IO"))
        self.entries.append(MethodEntry(8, "length", "Int", 1, "String"))
        self.entries.append(MethodEntry(9, "concat", "String", 1, "String"))
        self.entries.append(MethodEntry(10, "substr", "String", 1, "String"))
        self.start_id = 10

    def __repr__(self):
        method_string = ""
        for entry in self.entries:
            method_string = method_string + entry + "\n"
        return method_string

    def add_entry(self, table_entry):
        if self.find_by_name(table_entry.name, table_entry.parent) is None:
            self.entries.append(table_entry)
            return True
        else:
            return False

    def find_by_name(self, name, parent):
        for entry in self.entries:
            if entry.name == name and entry.parent == parent:
                return entry
        return None

    def find_by_id(self, method_id):
        for entry in self.entries:
            if entry.id == method_id:
                return entry
        return None
