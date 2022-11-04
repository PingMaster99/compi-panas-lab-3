from symbol_table_module.table_entry_types import AttributeTableEntry


class AttributeTable:
    def __init__(self, init_entry=None):
        self.entries = []
        self.entries.append(AttributeTableEntry("out_string", "String", 2, "IO", 4, True))
        self.entries.append(AttributeTableEntry("out_int", "Int", 2, "IO", 5, True))
        self.entries.append(AttributeTableEntry("concat", "String", 2, "String", 9, True))
        self.entries.append(AttributeTableEntry("start", "Int", 2, "String", 10, True))
        self.entries.append(AttributeTableEntry("End", "Int", 2, "String", 10, True))
        if init_entry:
            self.entries.append(init_entry)

    def __repr__(self):
        attribute_string = ""
        for entry in self.entries:
            attribute_string = attribute_string + entry + "\n"
        return attribute_string

    def add_entry(self, table_entry):
        if self.find_entry(table_entry.name, table_entry.parent_class, table_entry.parent_method,
                           table_entry.scope) is None:
            self.entries.append(table_entry)
            return True
        else:
            return False

    def find_entry(self, name, parent_class, parent_method, scope):
        for entry in self.entries:
            if entry.name == name and entry.parent_class == parent_class and entry.parent_method == parent_method and entry.scope == scope:
                return entry
        return None

    def get_function_parameters(self, function_id):
        results = []
        for entry in self.entries:
            if entry.parent_method == function_id:
                if entry.is_parameter:
                    results.append(entry)
        return results

    def get_function_let_values(self, parent_method):
        results = []
        for entry in self.entries:
            if entry.parent_method == parent_method:
                if not entry.is_parameter:
                    results.append(entry)
        return results
