class AttributeTableEntry:
    def __init__(self, name, attribute_type, scope=None, parent_class=None, parent_method=None, is_parameter=False, size=0, offset=0):
        self.name = name
        self.type = attribute_type
        self.scope = scope
        self.parent_class = parent_class
        self.parent_method = parent_method
        self.is_parameter = is_parameter
        self.size = size
        self.offset = offset

    def __repr__(self):
        return f"ATTRIBUTE: {self.name} | TYPE: {self.type} | PARENT_CLASS: {self.parent_class} | PARENT_METHOD: {self.parent_method} | SCOPE: {self.scope} | PARAMETER: {self.is_parameter} | SIZE: {self.size} | MEM_OFFSET: {self.offset}"

    def __radd__(self, other):
        return other + str(self)


class ClassTableEntry:
    def __init__(self, name, inherits="Object", size=0):
        self.name = name
        self.inherits = inherits
        self.size = size

    def __repr__(self):
        return f'CLASS: {self.name} | PARENT: {self.inherits} | SIZE: {self.size}'

    def __radd__(self, other):
        return other + str(self)


class MethodEntry:
    def __init__(self, function_id, function_name, function_type, scope=None, parent_class=None):
        self.id = function_id
        self.name = function_name
        self.type = function_type
        self.scope = scope
        self.parent = parent_class

    def __repr__(self):
        return f"METHOD: {self.name} ID: {self.id} | | TYPE: {self.type} | SCOPE: {self.scope} | PARENT: {self.parent}"

    def __radd__(self, other):
        return other + str(self)
