class TypeSystem:
    def __init__(self):
        self.all_types = ["Int", "Bool", "String", "Void", "Object"]                    # All Types
        self.type_sizes = {"Int": 8, "Bool": 1, "String": None}                         # Sizes in bytes
    
    def add_entry(self, entry_type):
        self.all_types.append(entry_type)
    
    # finds type in table
    def find_entry(self, entry_type):
        for entry in self.all_types:
            if entry == entry_type:
                return entry
        return None

    def get_primitive_size(self, element_type):
        # Not one of the primitives, we allocate min memory size (1)
        if element_type not in self.type_sizes:
            return 1
        if element_type != 'String' and element_type != 'Str':
            return self.type_sizes[element_type]
        else:
            return len(element_type.encode('utf-8'))

    def get_all_types(self):
        return self.all_types
    
