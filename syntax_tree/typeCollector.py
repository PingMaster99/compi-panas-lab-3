import syntax_tree.tree_decorators as visitor
from data_structures.types import *
from data_structures.scope import Scope
from error_module.error_handler import ErrorGenerator
from data_structures.node import (
    Node,
    ProgramNode,
    ClassNode,
    AttributeNode,
    MethodNode,
    ParamNode
)

class TypeCollectorVisitor:

    @visitor.on('node')
    def visit(self, node: Node, context: ContextType, errors):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, context: ContextType, errors):
        for c in node.class_list:
            self.visit(c, context, errors)

        context.createType("Object")
        context.createType("Int")
        context.createType("String")
        context.createType("Bool")
        context.createType("IO")
        context.createType("SELF_TYPE")

        context.getType("IO").defineMethod("in_string", "SELF_TYPE", [], [])
        context.getType("IO").defineMethod("in_int", "SELF_TYPE", [], [])
        context.getType("IO").defineMethod("out_string", "IO", ["x"], ["String"])
        context.getType("IO").defineMethod("out_int", "IO", ["x"], ["Int"])

        context.getType("Object").defineMethod("abort", "Object", [], [])
        context.getType("Object").defineMethod("type_name", "String", [], [])
        context.getType("Object").defineMethod("copy", "SELF_TYPE", [], [])

        context.getType("IO").defineMethod("abort", "Object", [], [])
        context.getType("IO").defineMethod("type_name", "String", [], [])
        context.getType("IO").defineMethod("copy", "SELF_TYPE", [], [])

        context.getType("Int").defineMethod("abort", "Object", [], [])
        context.getType("Int").defineMethod("type_name", "String", [], [])
        context.getType("Int").defineMethod("copy", "SELF_TYPE", [], [])

        context.getType("String").defineMethod("abort", "Object", [], [])
        context.getType("String").defineMethod("type_name", "String", [], [])
        context.getType("String").defineMethod("copy", "SELF_TYPE", [], [])

        context.getType("Bool").defineMethod("abort", "Object", [], [])
        context.getType("Bool").defineMethod("type_name", "String", [], [])
        context.getType("Bool").defineMethod("copy", "SELF_TYPE", [], [])

        context.getType("String").defineMethod("length", "Int", [], [])
        context.getType("String").defineMethod("concat", "String", ["s"], ["String"])
        context.getType("String").defineMethod("substr", "String", ["i", "lex"], ["Int", "Int"])

    @visitor.when(ClassNode)
    def visit(self, node: ClassNode, context: ContextType, errors):
        context.createType(node.name)
        if node.parent is None:
            print("PARENT IS NONE FOR", node.name)
        if node.parent != None:
            context.getType(node.name).parent = node.parent


class TypeBuilderVisitor:
    @visitor.on('node')
    def visit(self, node: Node, context: ContextType, errors):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, context: ContextType, errors):
        for c in node.class_list:
            self.visit(c, context, errors)
        node.context_type = context

    @visitor.when(ClassNode)
    def visit(self, node: ClassNode, context: ContextType, errors):
        current_type = context.getType(node.name)
        for feature in node.features:
            self.visit(feature, context, errors, current_type)

    # VISITING VARIABLES
    @visitor.when(AttributeNode)
    def visit(self, node: AttributeNode, context: ContextType, errors, current_type: Type):
        if not current_type.defineAttribute(node.name, node.attr_type):
            ErrorGenerator(
                message=f"Attribute {node.name} already exists in scope",
                line=node.line
            )

    @visitor.when(MethodNode)
    def visit(self, node: MethodNode, context: ContextType, errors, current_type: Type):
        args = []
        argsTypes = []
        for arg in node.params:
            name, type = self.visit(arg, context, errors, current_type)
            args.append(name)
            argsTypes.append(type)
        current_type.defineMethod(node.name, node.method_type, args, argsTypes)

    @visitor.when(ParamNode)
    def visit(self, node: ParamNode, context: ContextType, errors, current_type: Type):
        if context.getType(node.param_type) == "SELF_TYPE":
            return (node.name, current_type)
        return (node.name, context.getType(node.param_type).name)


class TypeHierarchy:
    def __init__(self):
        self.types_defined = {}
        self.ast_children_nodes = {}

        self.define_type('Object')
        self.define_type('IO')
        self.define_type('Int')
        self.define_type('String')
        self.define_type('Bool')

        self.ast_children_nodes['Object'] = []
        self.ast_children_nodes['IO'] = []
        self.ast_children_nodes['Int'] = []
        self.ast_children_nodes['String'] = []
        self.ast_children_nodes['Bool'] = []

        self.set_child('Object', 'IO')


    def define_type(self, name: str):
        self.types_defined[name] = []

    def set_child(self, name: str, child: str):
        if name not in self.types_defined.keys():
            self.define_type(name)
        self.types_defined[name].append(child)

    def set_child_node(self, name: str, child: ClassNode):
        if name not in self.ast_children_nodes.keys():
            self.ast_children_nodes[name] = []
        self.ast_children_nodes[name].append(child)

    def inheritance_resolve(self, context_type: ContextType, current_parent: str):
        for child in self.ast_children_nodes[current_parent]:
            inheritance_resolve_visitor = InheritanceResolveVisitor()
            inheritance_resolve_visitor.visit(child, context_type)
        for child in self.types_defined[current_parent]:
            self.inheritance_resolve(context_type, child)


class Hierarchy:
    @visitor.on('node')
    def visit(self, node: Node, context: ContextType, type_hierarchy: TypeHierarchy):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, context: ContextType, type_hierarchy: TypeHierarchy):
        for c in node.class_list:
            if not self.visit(c, context, type_hierarchy):
                return False

    @visitor.when(ClassNode)
    def visit(self, node: ClassNode, context: ContextType, type_hierarchy: TypeHierarchy):
        if node.name not in type_hierarchy.types_defined.keys():
            type_hierarchy.define_type(node.name)
        if node.name not in type_hierarchy.ast_children_nodes.keys():
            type_hierarchy.ast_children_nodes[node.name] = []
        if node.name == 'Main' and node.parent == 'Object':
            node.parent = 'Object_'
        if node.parent is None:
            node.parent = 'Object'
        if node.parent not in context.types.keys():
            # print("Type " + node.parent + " not defined")
            ErrorGenerator(
                message="Type " + node.parent + " not defined",
                line=node.line
            )
            return False
        type_hierarchy.set_child(node.parent, node.name)
        type_hierarchy.set_child_node(node.parent, node)
        return True



class InheritanceResolveVisitor:
    @visitor.on('node')
    def visit(self, node: Node, context: ContextType):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node: ProgramNode, context: ContextType):
        for clas in node.class_list:
            self.visit(clas, context)

    @visitor.when(ClassNode)
    def visit(self, node: ClassNode, context: ContextType):
        parent_class = node.parent
        if parent_class is None:
            parent_class = 'Object'

        if node.name == 'Main' and parent_class != 'Object':
            ErrorGenerator(
                message=f'Main cannot inherit from other Types. Tried to inherit {parent_class}',
                line=node.line
            )

        type_of_parent = context.getType(parent_class)
        type_of_class = context.getType(node.name)

        type_of_class.parent = parent_class

        for attribute in type_of_parent.attributes.values():
            if attribute in type_of_class.attributes.values():
                # print('The attributes of a class can not be redefined in the child class')
                ErrorGenerator(
                    message="The attributes of a class can not be redefined in the child class",
                    line=node.line
                )
                return False
            else:
                type_of_class.defineAttribute(attribute.name, attribute.attribute_type)

        for method_of_parent in type_of_parent.methods.values():
            founded = False
            for method_of_class in type_of_class.methods.values():
                method_of_parent: Method
                method_of_class: Method


                if method_of_parent.name == method_of_class.name:
                    founded = True
                    if method_of_parent.return_type != method_of_class.return_type:
                        # print("Return type of method must be the same of return type from inherits class")
                        ErrorGenerator(
                            message="Return type of method must be the same of return type from inherits class",
                            line=node.line
                        )
                        return False
                    if len(method_of_parent.arguments) != len(method_of_class.arguments):
                        # print("The amount of arguments of method must be the same of method from inherits class")
                        ErrorGenerator(
                            message="The amount of arguments of method must be the same of method from inherits class",
                            line=node.line
                        )
                        return False
                    for i in range(len(method_of_parent.arguments)):
                        attr_1: Attribute = method_of_parent.arguments[i]
                        attr_2: Attribute = method_of_class.arguments[i]
                        if attr_1.attribute_type != attr_2.attribute_type:
                            # print("Type of attribute in position " + str(i) + " must be the same of the method from inherits class")
                            ErrorGenerator(
                                message="Type of attribute in position " + str(i) + " must be the same of the method from inherits class",
                                line=node.line
                            )
                            return False
                if founded:
                    break
            else:
                arguments = [arg.name for arg in method_of_parent.arguments]
                arguments_types = [arg.attribute_type for arg in method_of_parent.arguments]
                type_of_class.defineMethod(method_of_parent.name, method_of_parent.return_type, arguments,
                                           arguments_types)


        return True




