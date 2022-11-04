# Generated from yapl.g4 by ANTLR 4.10.1
from grammar.yaplParser import yaplParser
from grammar.yaplVisitor import yaplVisitor
from error_module.error_handler import ErrorGenerator


# This class defines a complete generic visitor for a parse tree produced by yaplParser.

# TYPE SYSTEM VISITOR
class ValidatorVisitor(yaplVisitor):
    """
    Validates a program once the symbol table is complete
    Checks variable definitions, classes, methods, conditionals in loops, expression contexts, and arithmetic
    """
    def __init__(self, symbol_table):
        super().__init__()
        self.functionTable = symbol_table.functions
        self.attributeTable = symbol_table.attributes
        self.typesTable = symbol_table.types
        self.classTable = symbol_table.classes
        self.current_method = None
        self.current_scope = 1
        self.current_class = ""
        self.current_method_id = self.functionTable.start_id

    def find_class_dependency(self, current_class, needed_class):
        """
        Checks if a base class can use a method
        :param current_class: base class
        :param needed_class: needed class
        :return: Boolean if it can use the method
        """
        # If the current class is None
        if not current_class:
            return False

        # Parent class of the current class
        parent_class = self.classTable.find_entry(current_class.inherits)
        available_classes = []

        # We check if the parent class also inherits other classes
        while parent_class:
            # Note that object inherits None, so it won't find any class once base is reached
            available_classes.append(parent_class.name)
            parent_class = self.classTable.find_entry(parent_class.inherits)

        # If base method cannot use the needed clas
        return needed_class in available_classes

    # Visit a parse tree produced by yaplParser#start.
    def visitStart(self, ctx: yaplParser.StartContext):
        """
        Visit the start of a program with production
        program EOF
        :param ctx:
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#program.
    def visitProgram(self, ctx: yaplParser.ProgramContext):
        """
        Visit the program with production
        classSpecification ';' program
        | EOF
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
        self.current_scope = 1

        # If class inherits another class
        if len(ctx.TYPE()) > 1:
            parent = str(ctx.TYPE()[1])
            if not self.classTable.find_entry(parent):
                ErrorGenerator(
                    message=f"Cannot inherit class '{parent}' because it is not defined",
                    line=class_line
                )

                return "Error"

            if parent == "String" or parent == "Int" or parent == "Bool":
                ErrorGenerator(
                    message=f"Class '{class_name}' cannot inherit base type '{parent}'",
                    line=class_line
                )

        return self.visitChildren(ctx)

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

        # We increase the scope because we are inside a method
        self.current_scope = 2
        self.current_method = method_name

        # SELF_TYPE returns parent class
        if method_type == "SELF_TYPE":
            method_type = self.current_class

        # We visit all formal declarations AKA. function parameters
        for node in ctx.formal():
            self.visit(node)

        # We visit what the method returns
        method_returns = self.visit(ctx.expr())

        if method_returns == "SELF_TYPE":
            method_returns = self.current_class

        # If the return type is valid
        if method_returns == method_type or self.find_class_dependency(self.classTable.find_entry(method_returns),
                                                                       method_type):
            return method_type

        # If method return type is not congruent with method definition
        elif method_returns:
            ErrorGenerator(
                message=f"Method '{method_name}' should return {method_type} but returns {method_returns}",
                line=method_line
            )
        # If method returns VOID
        else:
            ErrorGenerator(
                message=f"Method '{method_name}' returns VOID instead of {method_type}",
                line=method_line
            )
            return "Error"

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

        # If the attribute has an invalid type
        if attribute_type not in self.typesTable.all_types and self.classTable.find_entry(attribute_type) is None:
            ErrorGenerator(
                message=f"Invalid type '{attribute_type}' assignation to variable '{attribute_name}'",
                line=attribute_line
            )

        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#formal.
    def visitFormal(self, ctx: yaplParser.FormalContext):
        """
        Function parameter based on the production
        ID ':' TYPE
        :param ctx: context
        :return:
        """
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#add.
    def visitAdd(self, ctx: yaplParser.AddContext):
        """
        Visits an addition expression with production
        expr '+' expr

        VALID:
        bool + int
        string + string

        INVALID:
        bool + string
        int + string

        :param ctx:
        :return:
        """
        # Addition expressions only have 2 sides
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        line = ctx.start.line

        # Adding a string and another type
        if left != right and (left == "String" or right == "String" or left == "Error" or right == "Error"):
            ErrorGenerator(
                message=f"Cannot add types '{left}' and '{right}'",
                line=line
            )
            return "Error"

        # Adding ints, bools, or int and bool
        elif left != "String":
            return "Int"

        # Adding strings
        else:
            return "String"

    # Visit a parse tree produced by yaplParser#letIn.
    def visitLetIn(self, ctx: yaplParser.LetInContext):
        """
        visits a letIn declaration with production
        'let' ID ':' TYPE (ASSIGNMENT expr)? (',' ID ':' TYPE (ASSIGNMENT expr)?)* IN expr
        :param ctx:
        :return:
        """
        # This is a different scope from class scopes
        self.current_scope += 1

        # We visit concatenated nodes if present
        visited_nodes = []
        for node in ctx.expr()[0:-1]:
            visited_nodes.append(self.visit(node))

        # We add all variables defined in let

        for i in range(len(ctx.ID())):
            variable_name = str(ctx.ID()[i])  # ID in production
            variable_type = str(ctx.TYPE()[i])  # Variable TYPE

            # We check if we can assign the variable type
            if i < len(visited_nodes):
                if visited_nodes[i] != variable_type:
                    ErrorGenerator(
                        message=f"Variable '{variable_name}' is of type '{variable_type}' but '{visited_nodes[i]}' was assigned to it",
                        line=ctx.start.line
                    )
                    # We return the type to check for errors in posterior assignments
                    return variable_type

        visited_result = self.visit(ctx.expr()[-1])
        self.current_scope -= 1
        return visited_result

    # Visit a parse tree produced by yaplParser#identifier.
    def visitIdentifier(self, ctx: yaplParser.IdentifierContext):
        """
        Visit an identifier production
        ID
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        variable_name = str(ctx.ID())
        variable_line = ctx.start.line
        # Self returns the base class
        if variable_name == "self":
            return "SELF_TYPE"

        # Check if the variable is defined on the symbol table
        scope = self.current_scope
        table_entry = self.attributeTable.find_entry(variable_name, self.current_class, self.current_method_id,
                                                     scope)
        # While not in base scope
        while scope > 0:
            # Check if variable is defined in method
            if table_entry is None:
                table_entry = self.attributeTable.find_entry(variable_name, self.current_class, self.current_method_id,
                                                             scope)

            # If variable is not defined in method, we check the class
            if table_entry is None:
                table_entry = self.attributeTable.find_entry(variable_name, self.current_class, None, scope)

            # If the variable is not defined in the method or in the class
            if table_entry is not None:
                return table_entry.type
            # We check the previous scope
            scope -= 1

        # Variable is not defined
        if table_entry is None:
            ErrorGenerator(
                message=f"Variable '{variable_name}' is not defined",
                line=variable_line
            )

            return "Error"

    # Visit a parse tree produced by yaplParser#negation.
    def visitNegation(self, ctx: yaplParser.NegationContext):
        """
        Visits a negation production
        '~' expr
        :param ctx:
        :return:
        """
        negated_result = self.visit(ctx.expr())
        # ~ operator can only be used on Int type
        if negated_result != "Int":
            ErrorGenerator(
                message=f"Cannot use '~' operator on '{negated_result}' type"
            )
            return "Error"

        return negated_result

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

        VALID:
        bool - int
        int - int

        INVALID:
        Anything involving strings

        :param ctx:
        :return:
        """
        # Left and right expressions
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        line = ctx.start.line

        # Strings cannot be subtracted with any other type
        if left == "String" or right == "String":
            ErrorGenerator(
                message=f"Cannot subtract types '{left}' and '{right}'",
                line=line
            )
            return "Error"
        # Other types are cast to Int
        else:
            return "Int"

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
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        line = ctx.start.line

        # Strings cannot be compared, only bool and int
        if left == "String" or right == "String":
            ErrorGenerator(
                message=f"Cannot compare types '{left}' and {right}",
                line=line
            )
            return "Bool"
        # Can compare combinations of int and bool
        else:
            return "Bool"

    # Visit a parse tree produced by yaplParser#assignmentExpression.
    def visitAssignmentExpression(self, ctx: yaplParser.AssignmentExpressionContext):
        """
        Visits an assignment expression with production
        ID ASSIGNMENT expr
        (ID <- expr)
        :param ctx:
        :return:
        """

        # !ID! <- expr
        variable_name = str(ctx.ID())
        variable_line = ctx.start.line
        scope = self.current_scope

        table_entry = self.attributeTable.find_entry(variable_name, self.current_class, self.current_method_id,
                                                       scope)
        while scope > 0:
            # Checks if it is inside a method
            if table_entry is None:
                table_entry = self.attributeTable.find_entry(variable_name, self.current_class, self.current_method_id,
                                                               scope)
            # Checks if its inside a class
            if table_entry is None:
                table_entry = self.attributeTable.find_entry(variable_name, self.current_class, None, scope)
            # Exits lower scope
            scope -= 1

        # If variable is not defined
        if table_entry is None:
            ErrorGenerator(
                message=f"Variable {variable_name} is not defined",
                line=variable_line
            )
            return "Error"

        # We visit the assignment expression ID <- !expr!
        expression_result = self.visit(ctx.expr())

        # If it is the same type of the variable or has a parent that allows that type
        if expression_result == table_entry.type or self.find_class_dependency(
                self.classTable.find_entry(expression_result),
                table_entry.type):
            return table_entry.type

        # Trying to assign a type that is not valid
        else:
            ErrorGenerator(
                message=f"Variable '{variable_name}' is of type '{table_entry.type}' but '{expression_result}' was assigned to it",
                line=variable_line
            )

            # We return type to continue checking for errors
            return table_entry.type

    # Visit a parse tree produced by yaplParser#expressionContext.
    def visitExpressionContext(self, ctx: yaplParser.ExpressionContextContext):
        """
        Visits an expression context with production:
        '{' (expr ';')* '}'
        :param ctx:
        :return:
        """

        # We visit what is inside the context
        visited_nodes = []
        for node in ctx.expr():
            visited_nodes.append(self.visit(node))

        # We warn the user about empty contexts
        if len(visited_nodes) == 0:
            ErrorGenerator(
                message="Empty expression context detected",
                line=ctx.start.line,
                warning=True
            )

            # Empty contexts return VOID
            return "VOID"

        # We return the last type inside the expression
        return visited_nodes[-1]

    # Visit a parse tree produced by yaplParser#integer.
    def visitInteger(self, ctx: yaplParser.IntegerContext):
        """
        Visits an integer with production
        INT
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        return "Int"

    # Visit a parse tree produced by yaplParser#while.
    def visitWhile(self, ctx: yaplParser.WhileContext):
        """
        Visits a while context with production
        WHILE expr LOOP expr POOL
        :param ctx:
        :return:
        """

        conditional = self.visit(ctx.expr(0))
        body = self.visit(ctx.expr(1))
        line = ctx.start.line
        # We visit all expression nodes

        # First expression needs to be a conditional note that Int expressions are cast to bool
        if conditional == "Bool" or conditional == "Int":
            return "Object"

        # When the loop has an invalid condition
        else:
            ErrorGenerator(
                message=f"Attempted to enter a while loop with a condition of type {conditional}",
                line=line
            )

            return body

    # Visit a parse tree produced by yaplParser#parenthesis.
    def visitParenthesis(self, ctx: yaplParser.ParenthesisContext):
        """
        Visits a parenthesis expression with production
        '(' expr ')'
        :param ctx:
        :return:
        """
        return self.visit(ctx.expr())

    # Visit a parse tree produced by yaplParser#division.
    def visitDivision(self, ctx: yaplParser.DivisionContext):
        """
        Visits a division with production
        expr '/' expr
        :param ctx:
        :return:
        """

        # Left and right expressions
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        line = ctx.start.line

        # Strings cannot be divided with any other type
        if left == "String" or right == "String":
            ErrorGenerator(
                message=f"Cannot divide types '{left}' and '{right}'",
                line=line
            )
            return "Error"

        # Other types are cast to Int
        else:
            return "Int"

    # Visit a parse tree produced by yaplParser#equal.
    def visitEqual(self, ctx: yaplParser.EqualContext):
        """
        Visits an equal production
        expr '=' expr
        :param ctx:
        :return:
        """
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        line = ctx.start.line

        # All elements can be compared
        # if left == "String" or right == "String":
        #     ErrorGenerator(
        #         message=f"Cannot compare types '{left}' and {right}",
        #         line=line
        #     )
        #     return "Bool"
        # Can compare combinations of int and bool
        # else:
        return "Bool"

    # Visit a parse tree produced by yaplParser#newObjectInstance.
    def visitNewObjectInstance(self, ctx: yaplParser.NewObjectInstanceContext):
        """
        Visits a new object with production
        NEW TYPE
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        object_type = str(ctx.TYPE())
        object_line = ctx.start.line

        # We search if it is a defined class
        if self.classTable.find_entry(object_type):
            return object_type

        # If it is not a class we check the different types
        else:
            if self.typesTable.find_entry(object_type):
                return object_type
            # If it is not defined
            else:
                ErrorGenerator(
                    message=f"Type {object_type} is not defined",
                    line=object_line
                )
                return "Error"

    # Visit a parse tree produced by yaplParser#not.
    def visitNot(self, ctx: yaplParser.NotContext):
        """
        Visits a not expression with production
        NOT expr
        !!! CAN ONLY BE USED FOR BOOLs!!!
        :param ctx:
        :return:
        """
        expression_type = self.visit(ctx.expr())
        if expression_type == "Bool":
            return expression_type
        else:
            ErrorGenerator(
                message=f"Cannot use NOT operator on '{expression_type}' type"
            )
            # We return bool to continue checking
            return "Error"

    # Visit a parse tree produced by yaplParser#functionCall.
    def visitFunctionCall(self, ctx: yaplParser.FunctionCallContext):
        """
        Visits a function call with production
        ID '(' (expr (',' expr)*)? ')'
        :param ctx:
        :return:
        """
        function_name = str(ctx.ID())
        function_line = ctx.start.line
        function_parameters = []
        for node in ctx.expr():
            visited_parameter = self.visit(node)
            if visited_parameter == "SELF_TYPE":
                visited_parameter = self.current_class
            function_parameters.append(visited_parameter)

        # Check if method exists
        table_entry = self.functionTable.find_by_name(function_name, self.current_class)

        # If function exists
        if table_entry:
            # Check if it has the correct number of parameters
            defined_parameters = self.attributeTable.get_function_parameters(table_entry.id)

            # Function called with an incorrect number of parameters
            if len(function_parameters) != len(defined_parameters):
                ErrorGenerator(
                    message=f"Incorrect number of parameters for function '{table_entry.name}', expected {len(defined_parameters)} but got {len(function_parameters)}",
                    line=function_line
                )
                # We return this to get the return type
                return "Error"

            # Parameter types
            for i in range(len(function_parameters)):
                if function_parameters[i] != defined_parameters[i].type:
                    ErrorGenerator(
                        message=f"Method {table_entry.name} expects parameter of type {defined_parameters[i].type} in position {i + 1} got {function_parameters[i]}",
                        line=function_line
                    )
                    return "Error"
            # We return the base class or return type
            if table_entry.type == "SELF_TYPE":
                return function_parameters[0]
            else:
                return table_entry.type

        # Check if function is inherited
        else:
            # Check if class exists
            table_entry_class = self.classTable.find_entry(self.current_class)

            # If class exists
            if table_entry_class:

                parent = table_entry_class.inherits

                # If it does indeed inherit a class
                if parent:
                    table_entry = self.functionTable.find_by_name(function_name, parent)

                    if table_entry:
                        # We check the number of parameters of the parent class function
                        defined_parameters = self.attributeTable.get_function_parameters(table_entry.id)

                        # Function called with an incorrect number of parameters
                        if len(function_parameters) != len(defined_parameters):
                            ErrorGenerator(
                                message=f"Incorrect number of parameters for function '{table_entry.name}', expected {len(defined_parameters)} but got {len(function_parameters)}",
                                line=function_line
                            )
                            return "Error"

                        # Parameter types
                        for i in range(len(function_parameters)):
                            if function_parameters[i] != defined_parameters[i].type:
                                ErrorGenerator(
                                    message=f"Method {table_entry.name} expects parameter of type {defined_parameters[i].type} in position {i + 1} got {function_parameters[i]}",
                                    line=function_line
                                )

                                return "Error"

                        # If it returns base class
                        if table_entry.type == "SELF_TYPE":
                            return function_parameters[0]
                        else:
                            return table_entry.type
                    # Parent class is not defined
                    else:
                        ErrorGenerator(
                            message=f"Method '{function_name}' is not defined",
                            line=function_line
                        )
                        return "Error"

                # Method is not defined in any other class
                else:
                    ErrorGenerator(
                        message=f"Method '{function_name}' is not defined",
                        line=function_line
                    )

                    return "Error"
            # Class does not exist
            else:
                ErrorGenerator(
                    message=f"Method '{function_name}' is not defined",
                    line=function_line
                )
                return "Error"

    # Visit a parse tree produced by yaplParser#lessThan.
    def visitLessThan(self, ctx: yaplParser.LessThanContext):
        """
        Visits a less than expression with production
        expr '<' expr
        :param ctx:
        :return:
        """
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        line = ctx.start.line

        # Strings cannot be compared, only bool and int
        if left == "String" or right == "String":
            ErrorGenerator(
                message=f"Cannot compare types '{left}' and {right}",
                line=line
            )
            return "Bool"
        # Can compare combinations of int and bool
        else:
            return "Bool"

    # Visit a parse tree produced by yaplParser#true.
    def visitTrue(self, ctx: yaplParser.TrueContext):
        """
        Visits a true production
        TRUE
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        return "Bool"

    # Visit a parse tree produced by yaplParser#multiplication.
    def visitMultiplication(self, ctx: yaplParser.MultiplicationContext):
        """
        Visits a multiplication expression with production
        expr '*' expr
        :param ctx:
        :return:
        """

        # Left and right expressions
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        line = ctx.start.line

        # Strings cannot be divided with any other type
        if left == "String" or right == "String":
            ErrorGenerator(
                message=f"Cannot multiply types '{left}' and '{right}'",
                line=line
            )
            return "Error"

        # Other types are cast to Int
        else:
            return "Int"

    # Visit a parse tree produced by yaplParser#classMethodCall.
    def visitClassMethodCall(self, ctx: yaplParser.ClassMethodCallContext):
        """
        Visits a class method call expression with production
        expr ('@' TYPE)? '.' ID '(' (expr (',' expr)*)? ')'
        :param ctx:
        :return:
        """
        method_name = str(ctx.ID())
        method_line = ctx.start.line
        method_parameters = []
        # Class.method(!parameters*!)
        for node in ctx.expr():
            visited_node = self.visit(node)
            if visited_node == "SELF_TYPE":
                visited_node = self.current_class
            method_parameters.append(visited_node)

        # First node is the class
        class_name = method_parameters[0]

        # Check if it is inherited
        if ctx.TYPE():
            parent = str(ctx.TYPE())

            # Parent does not exist
            if not self.classTable.find_entry(parent):
                ErrorGenerator(
                    message=f"Parent class '{parent}' is not defined",
                    line=method_line
                )

                return "Error"

            current_class = self.classTable.find_entry(class_name)

            # Calling a method outside a class
            if current_class is None:
                ErrorGenerator(
                    message="Undefined class method call",
                    line=method_line
                )

                return "Error"

            # Wrong inheritance
            if current_class.inherits != parent:
                dad = self.classTable.find_entry(current_class.inherits)
                family = []
                while dad:
                    family.append(dad.name)
                    dad = self.classTable.find_entry(dad.inherits)
                if parent not in family:
                    error = ErrorGenerator(ctx.start.line,
                                           "Class " + class_name + " can't acces methods from class " + parent)

                    return "Error"

            # Check if the method is defined in the parent class
            table_entry = self.functionTable.find_by_name(method_name, parent)
            if table_entry:
                function_parameters = method_parameters[1:]
                defined_parameters = self.attributeTable.get_function_parameters(table_entry.id)
                # Function called with an incorrect number of parameters
                if len(function_parameters) != len(defined_parameters):
                    ErrorGenerator(
                        message=f"Incorrect number of parameters for function '{table_entry.name}', expected {len(defined_parameters)} but got {len(function_parameters)}",
                        line=method_line
                    )
                    return "Error"

                # Parameter types
                for i in range(len(function_parameters)):
                    if function_parameters[i] != defined_parameters[i].type:
                        ErrorGenerator(
                            message=f"Method {table_entry.name} expects parameter of type {defined_parameters[i].type} in position {i + 1} got {function_parameters[i]}",
                            line=method_line
                        )
                        return "Error"
                # We return the base class or return type
                if table_entry.type == "SELF_TYPE":
                    return method_parameters[0]
                else:
                    return table_entry.type
            # Not defined in parent
            else:
                ErrorGenerator(
                    message=f"Method '{method_name}' is not defined in parent class '{parent}'"
                )

                return "Error"

        # Check if it is on the current class
        else:
            # Check if the method is defined in the current class
            table_entry = self.functionTable.find_by_name(method_name, class_name)
            if table_entry:
                function_parameters = method_parameters[1:]
                defined_parameters = self.attributeTable.get_function_parameters(table_entry.id)

                # Function called with an incorrect number of parameters
                if len(function_parameters) != len(defined_parameters):
                    ErrorGenerator(
                        message=f"Incorrect number of parameters for function '{table_entry.name}', expected {len(defined_parameters)} but got {len(function_parameters)}",
                        line=method_line
                    )
                    return "Error"

                # Parameter types
                for i in range(len(function_parameters)):
                    if function_parameters[i] != defined_parameters[i].type:
                        ErrorGenerator(
                            message=f"Method {table_entry.name} expects parameter of type {defined_parameters[i].type} in position {i + 1} got {function_parameters[i]}",
                            line=method_line
                        )
                        return "Error"

                # If it returns base class
                if table_entry.type == "SELF_TYPE":
                    return method_parameters[0]
                else:
                    return table_entry.type
            # Method is not defined in base class
            else:
                table_entry = self.functionTable.find_by_name(method_name, "Object")
                if not table_entry:
                    print(method_name, class_name, "SEARCHING IN THIS")
                    ErrorGenerator(
                        message=f"Method '{method_name}' is not defined in parent class '{class_name}'",
                        line=method_line
                    )

                    return "Error"
                else:
                    return table_entry.type

    # Visit a parse tree produced by yaplParser#ifElse.
    def visitIfElse(self, ctx: yaplParser.IfElseContext):
        """
        Visits an ifElse expression with production
        IF expr THEN expr ELSE expr FI
        :param ctx:
        :return:
        """
        visited_expressions = []
        if_line = ctx.start.line

        # IF conditional, THEN conditional, ELSE conditional
        for node in ctx.expr():
            visited_expressions.append(self.visit(node))

        # Int and bool expressions are valid for conditionals
        if visited_expressions[0] == "Bool" or visited_expressions[0] == "Int":
            if visited_expressions[1] == visited_expressions[2]:
                # We return a new type only if they match
                return visited_expressions[1]
            # We return object if it is a composition of types
            return "Object"
        # Conditional is not a bool
        else:
            ErrorGenerator(
                message=f"Attempted to enter an if with a condition of type '{visited_expressions[0]}'",
                line=if_line
            )

            return "Error"


del yaplParser
