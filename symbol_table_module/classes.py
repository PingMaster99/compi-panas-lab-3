from symbol_table_module.table_entry_types import ClassTableEntry


class ClassTable:
    def __init__(self, init_entry=None):
        self.entries = []
        if init_entry:
            self.entries.append(init_entry)
        self.entries.append(ClassTableEntry("IO", "Object"))
        self.entries.append(ClassTableEntry("Object", None))
        self.entries.append(ClassTableEntry("Int", "Object"))
        self.entries.append(ClassTableEntry("String", "Object"))
        self.entries.append(ClassTableEntry("Bool", "Object"))

    def __repr__(self):
        class_string = ""
        for class_entry in self.entries:
            class_string = class_string + class_entry + "\n"
        return class_string

    def add_entry(self, table_entry):
        if self.find_entry(table_entry.name) is None:
            self.entries.append(table_entry)
            return True
        else:
            return False

    def find_entry(self, name):
        for entry in self.entries:
            if entry.name == name:
                return entry
        return None
