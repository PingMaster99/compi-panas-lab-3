from data_structures.scope import Scope
from error_module.error_handler import ErrorGenerator
from data_structures.types import Type, ContextType

"""
Syntax tree node
"""

TYPES = ['Int', 'String', 'Bool']

class Node:
    """
    Abstract Syntax Tree Node
    """

    def __init__(self):
        self.context_type = ContextType()
        self.return_type = Type('NoneType')
        self.dynamic_type = Type('NoneType')
        self.inner_context = None
        self.line = -1
        self.errors = None

    def set_line(self, line):
        self.line = line

    def validate(self, context):
        pass

"""
Nodes
"""

class ProgramNode(Node):
    def __init__(self, class_list):
        super(Node, self).__init__()
        self.class_list = class_list
        self.context = Scope()
        self.context_map = {}
        self.initialize_context()
        self.initialize_builtin_types()

    def initialize_context(self):
        # Object methods
        self.context.functions['abort'] = []
        self.context.functions['type_name'] = []
        self.context.functions['copy'] = []

    def initialize_builtin_types(self):
        # IO
        io_context = self.context.create_child_scope()
        io_context.functions['in_string'] = []
        io_context.functions['in_int'] = []
        io_context.functions['out_string'] = ['x']
        io_context.functions['out_int'] = ['x']
        self.context_map['IO'] = io_context

        int_context = self.context.create_child_scope()
        self.context_map['Int'] = int_context

        string_context = self.context.create_child_scope()
        self.context_map['String'] = string_context

        bool_context = self.context.create_child_scope()
        self.context_map['Bool'] = bool_context

        object_context = self.context.create_child_scope()
        self.context_map['Object'] = object_context

        self_type_context = self.context.create_child_scope()
        self.context_map['SELF_TYPE'] = self_type_context

    def __repr__(self):
        s = "Program:\n"
        for c in self.class_list:
            s += str(c) + '\n'
        return s

    def validate(self, context_attributes_inheritance, context: Scope = None):
        validated = True
        self.context_type = context_attributes_inheritance
        for statement in self.class_list:

            print("CHECKING", statement, context_attributes_inheritance, "END", statement.parent)
            if statement.parent and statement.parent in TYPES:
                if statement.parent == 'Int':
                    # TODO: MAKE GLOBAL
                    ErrorGenerator(
                        message=f'Class {statement.name} cannot inherit from Int',
                        line=statement.line
                    )
                    validated = False
                if statement.parent == 'String':
                    # print('A class cannot inherit from String')
                    ErrorGenerator(
                        message=f'Class {statement.name} cannot inherit from String',
                        line=statement.line
                    )
                    validated = False
                if statement.parent == 'Bool':
                    # print('A class cannot inherit from Bool')

                    ErrorGenerator(
                        message=f'Class {statement.name} cannot inherit from Bool',
                        line=statement.line
                    )

                    validated = False

            if statement.name == 'Main' and statement.parent and (statement.parent not in TYPES) and statement.parent != 'Object':
                if statement.parent == 'Object_':
                    statement.parent = 'Object'
                ErrorGenerator(
                    message=f'Class {statement.name} cannot inherit other classes, tried to inherit {statement.parent}',
                    line=statement.line
                )
                if statement.parent == 'Object':
                    statement.parent = 'Object_'

        # if not validated:
        #     return False

        for statement in self.class_list:
            print("STATEMENT", statement)
            statement.validate(self.context)
            if not statement.validate(self.context):
                validated = False
            self.context_map[statement.name] = self.context.children[len(self.context.children) - 1]

        return validated


class ClassNode(Node):
    def __init__(self, name, parent, features):
        super().__init__()
        self.name = name
        self.parent = parent
        self.features = features


    def __str__(self):
        return str(self.name)

    def validate(self, context) -> bool:
        print("VALIDATIONG===================", self.name)
        valid = True
        self.inner_context = context.create_child_scope()
        self.inner_context.define('self')
        # Attributes of the current class
        for attr in self.context_type.types[self.name].attributes.keys():
            print("ATTR", attr)
            self.inner_context.define(attr)
        for feature in self.features:
            if feature and not feature.validate(self.inner_context):
                valid = False


        return valid


class FeatureNode(Node):
    def __init__(self):
        super().__init__()

    def validate(self, context: Scope) -> bool:
        pass


class MethodNode(FeatureNode):
    def __init__(self, name, params, return_type, body):
        super().__init__()
        self.name = name
        self.params = params
        self.method_type = return_type
        self.body = body

    def validate(self, context: Scope) -> bool:
        # New context inside method node
        self.inner_context = context.create_child_scope()

        for param in self.params:
            self.inner_context.define(param.name)
        print(self.name, "VALIDATING THISSSS", self.body)
        if self.body and not self.body.validate(self.inner_context):
            return False

        if not context.define(self.name, [param.name for param in self.params]):
            # print(f'There were multiple definitions of method: {self.name}')
            ErrorGenerator(
                message=f'There were multiple definitions of method: {self.name}',
                line=self.line
            )
            return False

        return True


class AttributeNode(FeatureNode):
    def __init__(self, name, attr_type, init_expr):
        super(AttributeNode, self).__init__()
        self.name = name
        self.attr_type = attr_type
        self.init_expr = init_expr

    def validate(self, context: Scope) -> bool:
        print("VALIDATING ATTRIBUTEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", self.name)
        valid = True
        if self.init_expr and not self.init_expr.validate(context):
            valid = False

        print(context.define(self.name), self.name, context)
        if not context.define(self.name):
            print("WOWWWW MULTPLEEEEEEEEEEEEEE")
            # print(f'There were multiple definition of attribute: {self.name}')
            ErrorGenerator(
                message=f'There were multiple definition of attribute: {self.name}',
                line=self.line
            )
            valid = False
        return valid


class ParamNode(FeatureNode):
    def __init__(self, name, param_type):
        super(ParamNode, self).__init__()
        self.name = name
        self.param_type = param_type

    def validate(self, context: Scope):
        return True


class ObjectNode(Node):
    def __init__(self, name):
        super(ObjectNode, self).__init__()
        self.name = name

    def __str__(self):
        return self.name

    def validate(self, context: Scope):
        if not context.is_defined(self.name):
            # print(f'The object "{self.name}" is not defined in this scope')
            ErrorGenerator(
                message=f'The object "{self.name}" is not defined in this scope',
                line=self.line
            )
            return False
        return True


class SelfNode(ObjectNode):
    def __init__(self):
        super(SelfNode, self).__init__("SELF")


class ExpressionNode(Node):
    def __init__(self):
        super(ExpressionNode, self).__init__()

    @property
    def get_type(self):
        pass


class NewObjectNode(ExpressionNode):
    def __init__(self, new_type):
        super(NewObjectNode, self).__init__()
        self.type_new_object = new_type

    def validate(self, context: Scope):
        return True


class CaseNode(ExpressionNode):
    def __init__(self, expr, actions):
        super(CaseNode, self).__init__()
        self.expr = expr
        self.actions = actions

    def validate(self, context: Scope):
        if not self.expr.validate(context):
            return False

        for action in self.actions:
            if not action.validate(context):
                return False
        return True


class ActionNode(Node):
    def __init__(self, name, action_type, body):
        super(ActionNode, self).__init__()
        self.name = name
        self.action_type = action_type
        self.body = body
        self.inner_context = None

    def validate(self, context: Scope):
        self.inner_context = context.create_child_scope()
        self.inner_context.define(self.name)
        return self.body.validate(self.inner_context)


class IsVoidNode(ExpressionNode):
    def __init__(self, expr: ExpressionNode):
        super(IsVoidNode, self).__init__()
        self.expr = expr

    @property
    def get_type(self):
        return 'Bool'

    def validate(self, context: Scope):
        return self.expr.validate(context)


"""
 Operators
"""

class BinaryOperatorNode(ExpressionNode):
    def __init__(self, left: ExpressionNode, right: ExpressionNode):
        super(BinaryOperatorNode, self).__init__()
        self.left = left
        self.right = right

    @property
    def get_type(self):
        return self.left.get_type

    def validate(self, context: Scope):
        return self.left.validate(context) and self.right.validate(context)


class UnaryOperator(ExpressionNode):
    def __init__(self, expr: ExpressionNode):
        super(UnaryOperator, self).__init__()
        self.expr = expr

    @property
    def get_type(self):
        return self.expr.get_type

    def validate(self, context: Scope):
        return self.expr.validate(context)


class AtomicNode(ExpressionNode):
    def __init__(self):
        super(AtomicNode, self).__init__()


class PlusNode(BinaryOperatorNode):
    def __init__(self, left, right):
        super(PlusNode, self).__init__(left, right)
        self.left = left
        self.right = right
        self.operator = '+'


class MinusNode(BinaryOperatorNode):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.left = left
        self.right = right
        self.operator = '-'


class StarNode(BinaryOperatorNode):
    def __init__(self, left, right):
        super(StarNode, self).__init__(left, right)
        self.left = left
        self.right = right
        self.operator = '*'


class DivNode(BinaryOperatorNode):
    def __init__(self, left, right):
        super(DivNode, self).__init__(left, right)
        self.left = left
        self.right = right
        self.operator = '/'


class EqualNode(BinaryOperatorNode):
    def __init__(self, left, right):
        super(EqualNode, self).__init__(left, right)
        self.left = left
        self.right = right
        self.operator = '='


class LessThanNode(BinaryOperatorNode):
    def __init__(self, left, right):
        super(LessThanNode, self).__init__(left, right)
        self.left = left
        self.right = right
        self.operator = '<'


class LessEqualNode(BinaryOperatorNode):
    def __init__(self, left, right):
        super(LessEqualNode, self).__init__(left, right)
        self.left = left
        self.right = right
        self.operator = '<='


class NegationNode(UnaryOperator):
    def __init__(self, value):
        super(NegationNode, self).__init__(value)
        self.value = value


class BooleanNegation(NegationNode):
    def __init__(self, value):
        super(BooleanNegation, self).__init__(value)
        self.operator = "!"


class IntegerNegation(NegationNode):
    def __init__(self, value):
        super(IntegerNegation, self).__init__(value)
        self.operator = "~"


class LetInNode(AtomicNode):
    def __init__(self, return_type, declaration_list, expr):
        super(LetInNode, self).__init__()
        # self.instance = instance
        self.return_type = return_type
        self.declaration_list = declaration_list
        self.expr = expr

    def get_type(self):
        return self.expr.get_type

    def validate(self, context: Scope):
        self.inner_context = context.create_child_scope()
        for declaration in self.declaration_list:
            if not declaration.validate(self.inner_context):
                return False
        return self.expr.validate(self.inner_context)


class DeclarationNode(ExpressionNode):
    def __init__(self, idx_token, type_token, expr=None):
        print("INIT OF A DECLARATION NODEEEEEEEEEEEEEEEEEEEEEE")
        super(ExpressionNode, self).__init__()
        self.idx_token = idx_token
        self.type_token = type_token
        self.expr = expr
        self.variable_info = None

    def get_type(self):
        return self.type_token

    def validate(self, context: Scope):
        print("VALIDATING A DECLARATION NODEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
        if self.expr is not None and not self.expr.validate(context):
            return False
        if not context.define(self.idx_token):
            # print(f'There were multiple declaration of var with id: {self.idx_token}')
            ErrorGenerator(
                message=f'There were multiple declaration of var with id: {self.idx_token}',
                line=self.line
            )
            return False
        return True


class IfNode(ExpressionNode):
    def __init__(self, predicate, then_expr, else_expr):
        super(IfNode, self).__init__()
        self.predicate = predicate
        self.then_expr = then_expr
        self.else_expr = else_expr

    def get_type(self):
        return self.then_expr

    def validate(self, context: Scope):
        if not self.predicate.validate(context):
            return False
        if not self.then_expr.validate(context):
            return False
        if not self.else_expr.validate(context):
            return False
        return True


class WhileNode(ExpressionNode):
    def __init__(self, predicate, expr):
        super(WhileNode, self).__init__()
        self.predicate = predicate
        self.expr = expr

    def get_type(self):
        return self.expr.get_type

    def validate(self, context: Scope):
        if not self.predicate.validate(context):
            return False
        if not self.expr.validate(context):
            return False
        return True


class BlockNode(AtomicNode):
    def __init__(self, expr_list):
        super(BlockNode, self).__init__()
        self.expr_list = expr_list

    def validate(self, context: Scope):
        # Validate all expressions inside code block
        for expresion in self.expr_list:
            if not expresion.validate(context):
                return False
        return True


class AssignNode(AtomicNode):
    def __init__(self, idx_token, expr):
        super(AssignNode, self).__init__()
        self.idx_token = idx_token
        self.expr = expr
        self.variable_info = None

    def validate(self, context: Scope):
        if self.expr and not self.expr.validate(context):
            return False
        if not context.is_defined(self.idx_token):
            # print(f'Var with id "{self.idx_token}" is not defined')
            ErrorGenerator(
                message=f'Var with id "{self.idx_token}" is not defined',
                line=self.line
            )
            return False
        return True


class DynamicDispatchNode(ExpressionNode):
    def __init__(self, instance, method, arguments):
        super(DynamicDispatchNode, self).__init__()
        self.instance = instance
        self.method = method
        self.arguments = arguments

    def validate(self, context: Scope):
        if type(self.instance) != str and not self.instance.validate(context):
            return False
        for expresion in self.arguments:
            if not expresion.validate(context):
                return False
        return True


class StaticDispatchNode(ExpressionNode):
    def __init__(self, instance, dispatch_type, method, arguments):
        super(StaticDispatchNode, self).__init__()
        self.instance = instance
        self.dispatch_type = dispatch_type
        self.method = method
        self.arguments = arguments

    def validate(self, context: Scope):
        if not self.instance.validate(context):
            return False
        for expresion in self.arguments:
            if not expresion.validate(context):
                return False
        return True


class IntegerNode(AtomicNode):
    def __init__(self, integer_token):
        super(IntegerNode, self).__init__()
        self.integer_token = integer_token

    def validate(self, context: Scope) -> bool:
        return True


class BooleanNode(AtomicNode):
    def __init__(self, boolean_token):
        super(BooleanNode, self).__init__()
        self.boolean_token = boolean_token

    def validate(self, context: Scope) -> bool:
        return True


class StringNode(AtomicNode):
    def __init__(self, string_token):
        super(StringNode, self).__init__()
        self.string_token = string_token

    def validate(self, context: Scope) -> bool:
        return True


class VariableNode(AtomicNode):
    def __init__(self, idx_token):
        super(VariableNode, self).__init__()
        self.idx_token = idx_token
        self.variable_info = None

    def validate(self, context: Scope):
        return context.is_defined(self.idx_token)


class PrintIntegerNode(AtomicNode):
    def __init__(self, expr):
        super(PrintIntegerNode, self).__init__()
        self.expr = expr

    def validate(self, context: Scope) -> bool:
        return True


class PrintStringNode(AtomicNode):
    def __init__(self, string_token):
        super(PrintStringNode, self).__init__()
        self.string_token = string_token

    def validate(self, context: Scope) -> bool:
        return True


class ScanNode(AtomicNode):
    def __init__(self, method):
        self.method = method
        super(ScanNode, self).__init__()

    def validate(self, context: Scope) -> bool:
        return True

