class Attribute:
    def __init__(self, name: str, attribute_type: str):
        self.name = name
        self.attribute_type = attribute_type

    def __eq__(self, other):
        return self.name == other.name


class Method:
    def __init__(self, name: str, return_type: str, arguments: list):
        self.name = name
        self.return_type = return_type
        self.arguments = arguments

    def __eq__(self, other):
        return self.arguments == other.arguments


class Type:
    def __init__(self, name: str, parent='Object'):
        self.parent = parent
        self.name = name
        self.attributes = {}
        self.methods = {}

    def getAttribute(self, name: str) -> Attribute:
        return self.attributes[name]

    def getMethod(self, name: str) -> Method:
        return self.methods[name]

    def defineAttribute(self, name: str, type: str):
        if name in self.attributes.keys():
            return False
        self.attributes[name] = Attribute(name, type)
        return True

    def defineMethod(self, name: str, returnType, arguments, argumentsTypes):
        l = [Attribute(arguments[i], argumentsTypes[i]) for i in range(len(arguments))]
        self.methods[name] = Method(name, returnType, l)


class ContextType:
    def __init__(self, parent=None, types={}, symbols={}):
        self.types = types
        self.symbols = symbols
        self.parent = parent

    def getType(self, type_name: str) -> Type:
        return self.types[type_name] if type_name in self.types else None

    def getTypeFor(self, symbol: str) -> Type:
        return self.symbols[symbol] if symbol in self.symbols else None

    def createChildContext(self):
        return ContextType(self, self.types, self.symbols)

    def defineSymbol(self, symbol: str, type_symbol: Type):
        self.symbols[symbol] = type_symbol

    def createType(self, name: str):
        self.types[name] = Type(name)

    def parentsOfType(self, types: Type) -> list:
        solve = [types.name]
        p = types.parent
        while p != 'Object':
            solve.append(p)
            p = self.getType(p).parent
        if solve[len(solve) - 1] != 'Object':
            solve.append('Object')
        return solve

    def heir(self, type1: Type, type2: Type):
        return type2.name in self.parentsOfType(type1) if type1 and type2 else None

