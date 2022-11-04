# Generated from yapl.g4 by ANTLR 4.10.1
from grammar.yaplParser import yaplParser
from grammar.yaplVisitor import yaplVisitor
from symbol_table_module.table_entry_types import *
from error_module.error_handler import ErrorGenerator

# This class defines a complete generic visitor for a parse tree produced by yaplParser.
PRINT_TABLE = False

BASE_METHODS = ['out_int', 'out_string', 'in_int', 'in_string']


# TYPE SYSTEM VISITOR
class CustomVisitor(yaplVisitor):

    def __init__(self, symbol_table):
        super().__init__()
        self.symbol_table = symbol_table
        self.has_main_class = False
        self.has_main_method = False
        self.current_class = None
        self.functionTable = symbol_table.functions
        self.attributeTable = symbol_table.attributes
        self.typesTable = symbol_table.types
        self.classTable = symbol_table.classes
        self.current_method = None
        self.scope = 1
        self.current_class = ""
        self.current_method_id = self.functionTable.start_id
        self.memory_offset = 0
        self.visiting_from_class = False
        self.visiting_from_method = False

    def iterTable(self, table, dictionary):
        if dictionary not in table:
            table.append(dictionary)
            if PRINT_TABLE:
                print(self.symbol_table, "\n\n\n\n\n")
                for i in table:
                    print(i)
                print("Len Table", len(self.symbol_table))

    # Visit a parse tree produced by yaplParser#start.
    def visitStart(self, ctx: yaplParser.StartContext):
        """
        Visit the start of a program
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#program.
    def visitProgram(self, ctx: yaplParser.ProgramContext):
        """
        Visit the program
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#classSpecification.
    def visitClassSpecification(self, ctx: yaplParser.ClassSpecificationContext):
        """
        Visits a class specification according to the production
        CLASS TYPE (INHERITS TYPE)? '{' (feature ';')* '}'
        :param ctx:
        :return:
        """
        class_name = str(ctx.TYPE()[0])  # CLASS !TYPE! (INHERITS TYPE)? '{' (feature ';')* '}'
        class_line = ctx.start.line
        # Every time we visit a class we restart the parameters
        self.current_class = class_name
        self.current_method = None
        self.scope = 1
        self.memory_offset = 0

        # If class inherits another class
        if len(ctx.TYPE()) > 1:
            parent = str(ctx.TYPE()[1])
            if class_name == 'Main':
                ErrorGenerator(
                    message=f"Class Main cannot inherit other classes, tried to inherit: {parent}",
                    line=class_line
                )

                parent = "IO"  # We only do this to recover from errors in case any IO methods were used in Main

            if not self.classTable.find_entry(parent):
                ErrorGenerator(
                    message=f"Cannot inherit class '{parent}' because it is not defined",
                    line=class_line
                )

                return "Error"

        # Main always inherits IO due to language definition
        elif class_name == 'Main':
            parent = "IO"

        # All classes inherit Object
        else:
            parent = "Object"

        # We visit all declarations of attributes, letIn, methods, etc. inside the class
        # CLASS TYPE (INHERITS TYPE)? '{' (!feature! ';')* '}'
        visited_nodes = []
        self.visiting_from_class = True
        for node in ctx.feature():

            visited_nodes.append(self.visit(node))  # Once the node is visited we get the result
        self.visiting_from_class = False
        # We remove any errors to get memory size
        if "Error" in visited_nodes:
            visited_nodes.remove("Error")

        # Symbol table entry is added
        entry = ClassTableEntry(class_name, parent, size=sum(visited_nodes))
        successful_entry = self.classTable.add_entry(entry)

        # Class already defined
        if not successful_entry:
            ErrorGenerator(
                message="Class " + class_name + " already defined",
                line=class_line
            )

            return "Error"

    # Visit a parse tree produced by yaplParser#method.
    def visitMethod(self, ctx: yaplParser.MethodContext):
        """
        Visits a method with the production
        (ID) '(' (formal (','formal)*)* ')' ':' TYPE '{' expr '}'
        :param ctx:
        :return:
        """
        # A new method is declared, so we increase the ID
        method_name = str(ctx.ID())
        method_type = str(ctx.TYPE())
        method_line = ctx.start.line
        self.current_method_id += 1

        # Symbol table entry
        entry = MethodEntry(self.current_method_id, method_name, method_type, self.scope, self.current_class)
        successful_entry = self.functionTable.add_entry(entry)

        # We increase the scope because we are inside a method
        self.scope = 2

        # Method already defined
        if not successful_entry:
            ErrorGenerator(
                message=f"Function {method_name} already defined in scope '{self.current_class}'",
                line=method_line
            )

            return "Error"

        # New method added
        else:
            self.current_method = method_name
            self.memory_offset = 0  # Memory offset is restarted

            # We visit all formal declarations AKA. function parameters
            for node in ctx.formal():
                self.visit(node)
            self.visiting_from_method = False
            self.visit(ctx.expr())
            self.visiting_from_method = False
            return 0  # We return 0 for memory size

    # Visit a parse tree produced by yaplParser#attribute.
    def visitAttribute(self, ctx: yaplParser.AttributeContext):
        """
        Visits an attribute with the production
        ID ':' TYPE (ASSIGNMENT expr)?
        :param ctx: context
        :return: Error or attribute size
        """
        # Name and type of the attribute
        attribute_name = str(ctx.ID())  # !ID! : TYPE (ASSIGNMENT expr)?
        attribute_type = str(ctx.TYPE())  # ID : !TYPE! (ASSIGNMENT expr)?
        attribute_line = ctx.start.line
        attribute_size = self.typesTable.get_primitive_size(attribute_type)  # Size in bytes
        # print("I AM VISITING THE ATTRIBUTE", attribute_name, attribute_type, self.scope, self.current_method_id, self.current_class, self.visiting_from_method, self.visiting_from_class)

        method_attribute = self.current_method
        if self.visiting_from_class and not self.visiting_from_method:
            method_attribute = False



        # If the attribute is inside a current method
        if method_attribute:
            entry = AttributeTableEntry(attribute_name, attribute_type, self.scope, self.current_class,
                                        self.current_method_id, size=attribute_size, offset=self.memory_offset)
            self.memory_offset += attribute_size  # We add to the memory offset

        # If the attribute is inside a class
        # IMPORTANT!!!! CLASS ATTRIBUTES ARE ALWAYS SAVED WITH SCOPE 1
        else:
            entry = AttributeTableEntry(attribute_name, attribute_type, 1, self.current_class, None,
                                        size=attribute_size,
                                        offset=self.memory_offset)
            self.memory_offset += attribute_size

        # Adding entry to the symbol table
        successful_entry = self.attributeTable.add_entry(entry)

        if not successful_entry:
            ErrorGenerator(
                message=f"Duplicate declaration of attribute '{attribute_name}' in scope '{self.current_class}'",
                line=attribute_line
            )

            return attribute_size  # We return size instead of error to get memory offsets right
        else:
            self.visitChildren(ctx)
            return attribute_size

    # Visit a parse tree produced by yaplParser#formal.
    def visitFormal(self, ctx: yaplParser.FormalContext):
        """
        Function parameter based on the production
        ID ':' TYPE
        :param ctx: context
        :return:
        """
        # Name and type of the formal
        formal_name = str(ctx.ID())  # !ID! ':' TYPE
        formal_type = str(ctx.TYPE())  # ID ':' !TYPE!
        formal_line = ctx.start.line
        formal_size = self.typesTable.get_primitive_size(formal_type)  # Size in bytes

        # Symbol table entry
        entry = AttributeTableEntry(formal_name, formal_type, self.scope, self.current_class,
                                    self.current_method_id, True, size=formal_size, offset=self.memory_offset)
        self.memory_offset += formal_size

        # Adding entry
        successful_entry = self.attributeTable.add_entry(entry)

        # Error module
        if not successful_entry:
            ErrorGenerator(
                message=f"Duplicate parameter {formal_name} on function {self.current_method}",
                line=formal_line
            )

            return "Error"
        else:
            return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#add.
    def visitAdd(self, ctx: yaplParser.AddContext):
        """
        Visits an addition expression with production
        expr '+' expr
        :param ctx:
        :return:
        """
        left = ctx.expr()[0]
        right = ctx.expr()[1]
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#letIn.
    def visitLetIn(self, ctx: yaplParser.LetInContext):
        """
        visits a letIn declaration with production
        'let' ID ':' TYPE (ASSIGNMENT expr)? (',' ID ':' TYPE (ASSIGNMENT expr)?)* IN expr
        :param ctx:
        :return:
        """
        # This is a different scope from class scopes
        self.scope += 1
        let_nodes = ctx.expr()[0:-1]

        # We visit concatenated nodes if present
        for node in let_nodes:
            self.visit(node)

        # We add all variables defined in let
        for i in range(len(ctx.ID())):
            variable_name = str(ctx.ID()[i])  # ID in production
            variable_type = str(ctx.TYPE()[i])  # Variable TYPE
            variable_size = self.typesTable.get_primitive_size(variable_type)

            # Adding the entry to the symbol table
            entry = AttributeTableEntry(variable_name, variable_type, self.scope, self.current_class,
                                        self.current_method_id, size=variable_size, offset=self.memory_offset)
            self.memory_offset += variable_size
            successful_entry = self.attributeTable.add_entry(entry)

            if not successful_entry:
                ErrorGenerator(
                    message=f"Variable {variable_name} already defined in scope {self.current_method}",
                    line=ctx.start.line
                )

                return "Error"

        # We visit this part of the production:
        # 'let' ID ':' TYPE (ASSIGNMENT expr)? (',' ID ':' TYPE (ASSIGNMENT expr)?)* IN !expr!
        self.visit(ctx.expr()[-1])
        self.scope -= 1
        return 0

    # Visit a parse tree produced by yaplParser#identifier.
    def visitIdentifier(self, ctx: yaplParser.IdentifierContext):
        """
        Visit an identifier production
        ID
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#negation.
    def visitNegation(self, ctx: yaplParser.NegationContext):
        """
        Visits a negation production
        '~' expr
        :param ctx:
        :return:
        """
        return "Int"

    # Visit a parse tree produced by yaplParser#void.
    def visitVoid(self, ctx: yaplParser.VoidContext):
        """
        Visits a void production
        ISVOID expr
        :param ctx:
        :return:
        """
        return "Bool"

    # Visit a parse tree produced by yaplParser#string.
    def visitString(self, ctx: yaplParser.StringContext):
        """
        Visits a string with production
        STR
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        return "String"

    # Visit a parse tree produced by yaplParser#subtract.
    def visitSubtract(self, ctx: yaplParser.SubtractContext):
        """
        Visits a subtract production
        expr '-' expr
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#false.
    def visitFalse(self, ctx: yaplParser.FalseContext):
        """
        Visits a false expression with production
        FALSE
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        return "Bool"

    # Visit a parse tree produced by yaplParser#lessOrEqual.
    def visitLessOrEqual(self, ctx: yaplParser.LessOrEqualContext):
        """
        Visits a less than or equal with production
        expr '<=' expr
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#assignmentExpression.
    def visitAssignmentExpression(self, ctx: yaplParser.AssignmentExpressionContext):
        """
        Visits an assignment expression with production
        ID ASSIGNMENT expr
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#expressionContext.
    def visitExpressionContext(self, ctx: yaplParser.ExpressionContextContext):
        """
        Visits an expression context with production:
        '{' (expr ';')* '}'
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#integer.
    def visitInteger(self, ctx: yaplParser.IntegerContext):
        """
        Visits an integer with production
        INT
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#while.
    def visitWhile(self, ctx: yaplParser.WhileContext):
        """
        Visits a while context with production
        WHILE expr LOOP expr POOL
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#parenthesis.
    def visitParenthesis(self, ctx: yaplParser.ParenthesisContext):
        """
        Visits a parenthesis expression with production
        '(' expr ')'
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#division.
    def visitDivision(self, ctx: yaplParser.DivisionContext):
        """
        Visits a division with production
        expr '/' expr
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#equal.
    def visitEqual(self, ctx: yaplParser.EqualContext):
        """
        Visits an equal production
        expr '=' expr
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#newObjectInstance.
    def visitNewObjectInstance(self, ctx: yaplParser.NewObjectInstanceContext):
        """
        Visits a new object with production
        NEW TYPE
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#not.
    def visitNot(self, ctx: yaplParser.NotContext):
        """
        Visits a not expression with production
        NOT expr
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#functionCall.
    def visitFunctionCall(self, ctx: yaplParser.FunctionCallContext):
        """
        Visits a function call with production
        ID '(' (expr (',' expr)*)? ')'
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#lessThan.
    def visitLessThan(self, ctx: yaplParser.LessThanContext):
        """
        Visits a less than expression with production
        expr '<' expr
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#true.
    def visitTrue(self, ctx: yaplParser.TrueContext):
        """
        Visits a true production
        TRUE
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#multiplication.
    def visitMultiplication(self, ctx: yaplParser.MultiplicationContext):
        """
        Visits a multiplication expression with production
        expr '*' expr
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#classMethodCall.
    def visitClassMethodCall(self, ctx: yaplParser.ClassMethodCallContext):
        """
        Visits a class method call expression with production
        expr ('@' TYPE)? '.' ID '(' (expr (',' expr)*)? ')'
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#ifElse.
    def visitIfElse(self, ctx: yaplParser.IfElseContext):
        """
        Visits an ifElse expression with production
        IF expr THEN expr ELSE expr FI
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)


del yaplParser
