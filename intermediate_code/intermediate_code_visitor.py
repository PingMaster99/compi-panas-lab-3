# Generated from yapl.g4 by ANTLR 4.10.1
from grammar.yaplParser import yaplParser
from grammar.yaplVisitor import yaplVisitor
from intermediate_code.intermediate_template_builder import *
from intermediate_code.quadruple import Quadruple

class IntermediateCodeGenerator(yaplVisitor):
    """
    Symbol definition:
    @ -> Always instantiated before a class
    """

    def __init__(self, symbol_table):
        super().__init__()
        self.functionTable = symbol_table.functions
        self.attributeTable = symbol_table.attributes
        self.typesTable = symbol_table.types
        self.classTable = symbol_table.classes
        self.temporalGenerator = TemporalGenerator()
        self.labelGenerator = LabelGenerator()
        self.currentClass = None
        self.currentMethodId = self.functionTable.start_id
        self.currentScope = 1
        self.currentMethod = None
        self.newCounter = 0
        self.split_character = '@'
        self.visual_empty_strings = False

    # Visit a parse tree produced by yaplParser#start.
    def visitStart(self, ctx: yaplParser.StartContext):
        """
        Visit the start of a program with production
        program EOF
        :param ctx:
        :return:
        """
        # Starts the intermediate code production
        return self.visit(ctx.program())

    # Visit a parse tree produced by yaplParser#program.
    def visitProgram(self, ctx: yaplParser.ProgramContext):
        """
        Visit the program with production
        classSpecification ';' program
        | EOF
        :param ctx:
        :return:
        """

        template_builder = TemplateBuilder()

        # If program has something
        if not ctx.EOF():
            class_definition = self.visit(ctx.classSpecification())  # !classSpecification! ';' program
            program_result = self.visit(ctx.program())  # classSpecification ';' !program!
            template_builder.add_code(class_definition.code)  # Adds the code for a class
            template_builder.add_code(program_result.code)  # Adds the code for the program
        return template_builder

    # Visit a parse tree produced by yaplParser#classSpecification.
    def visitClassSpecification(self, ctx: yaplParser.ClassSpecificationContext):
        """
        Visits a class specification according to the production
        CLASS TYPE (INHERITS TYPE)? '{' (feature ';')* '}'
        :param ctx:
        :return:
        """
        class_name = str(ctx.TYPE()[0])  # CLASS !TYPE! (INHERITS TYPE)? '{' (feature ';')* '}'

        # Every time we visit a class we restart the parameters
        self.currentClass = class_name
        self.currentMethod = None
        self.currentScope = 1

        # Template builder adds quadruple code
        template_builder = TemplateBuilder()
        template_builder.add_code([Quadruple('label', f"{class_name}", None)])

        # We visit the features inside the class
        for node in ctx.feature():
            visited_feature = self.visit(node)
            template_builder.add_code(visited_feature.code)  # Code is added
        return template_builder

    # Visit a parse tree produced by yaplParser#method.
    def visitMethod(self, ctx: yaplParser.MethodContext):
        """
        Visits a method with the production
        (ID) '(' (formal (','formal)*)* ')' ':' TYPE '{' expr '}'
        :param ctx:
        :return:
        """
        # Template builder
        template_builder = TemplateBuilder()

        # We increase the current method id and scope
        method_name = str(ctx.ID())
        self.currentMethodId += 1
        self.currentScope = 2
        parameter_intermediate_code = []

        # We visit the function parameters
        for node in ctx.formal():
            parameter_intermediate_code.append(self.visit(node))

        # We get the intermediate code that's inside the method
        inner_intermediate_code = self.visit(ctx.expr())

        # We add a label to define the method
        template_builder.add_code([Quadruple("label", f"{method_name}{self.split_character}{self.currentClass}", None)])

        # Parameters that define the method
        if parameter_intermediate_code is not None:
            template_builder.add_code(parameter_intermediate_code)

        # Once label is done, we add the method contents
        template_builder.add_code(inner_intermediate_code.code)

        # We add the return address label
        template_builder.add_code([Quadruple("=", inner_intermediate_code.addr, "method_return_address")])

        return template_builder

    # Visit a parse tree produced by yaplParser#attribute.
    def visitAttribute(self, ctx: yaplParser.AttributeContext):
        """
        Visits an attribute with the production
        AKA VARIABLES
        ID ':' TYPE (ASSIGNMENT expr)?
        :param ctx: context
        :return: Error or attribute size
        """

        template_builder = TemplateBuilder()
        variable_name = str(ctx.ID())
        generated_quadruple = False

        # Attributes are always saved in scope 1
        table_entry = self.attributeTable.find_entry(variable_name, self.currentClass, None, 1)

        # If the variable has an initialization
        if ctx.expr():
            result = self.visit(ctx.expr())
            template_builder.add_code(result.code)

            # Strings
            loop_range = 1
            string_value = None
            assignment_value = result.addr
            if table_entry.type == "String":
                assignment_value = assignment_value.replace('"', "").replace("'", "")
                string_value = assignment_value
                loop_range = len(assignment_value)

            for i in range(loop_range):
                if string_value is not None:
                    assignment_value = string_value[i]

                generated_quadruple = Quadruple("=", assignment_value,
                                                f"ATTR_VARIABLE_{variable_name}@{table_entry.parent_class}[{table_entry.offset + i}]")
                template_builder.add_code([generated_quadruple])

        # If the variable has a default initialization
        else:
            if table_entry.type == "Int":
                generated_quadruple = Quadruple("=", 0,
                                                f"ATTR_VARIABLE_{variable_name}@{table_entry.parent_class}[{table_entry.offset}]")
            elif table_entry.type == "Bool":
                generated_quadruple = Quadruple("=", 0,
                                                f"ATTR_VARIABLE_{variable_name}@{table_entry.parent_class}[{table_entry.offset}]")

            elif table_entry.type == "String":
                string_element = "" if not self.visual_empty_strings else "''"

                print("STRING SIZE", table_entry.size)
                generated_quadruple = Quadruple("=", string_element,
                                                f"ATTR_VARIABLE_{variable_name}@{table_entry.parent_class}[{table_entry.offset}]")
            else:
                pass

            # We add the variable if it has a generated quadruple
            if generated_quadruple:
                template_builder.add_code([generated_quadruple])
        return template_builder

    # Visit a parse tree produced by yaplParser#formal.
    def visitFormal(self, ctx: yaplParser.FormalContext):
        """
        Function parameter based on the production
        ID ':' TYPE
        :param ctx: context
        :return:
        """

        # Template builder
        template_builder = TemplateBuilder()
        formal_name = str(ctx.ID())

        parameter = self.attributeTable.find_entry(formal_name, self.currentClass, self.currentMethodId,
                                                   self.currentScope)

        # Parameter temporal
        temporal = self.temporalGenerator.generate_temporal()

        # Temporal with offset
        generated_quadruple = Quadruple("=", parameter.offset, temporal)
        template_builder.add_code([generated_quadruple])

        # Generated parameter
        generated_quadruple = Quadruple("param", f"[{formal_name}]", temporal)
        template_builder.add_code([generated_quadruple])

        # Garbage collector
        self.temporalGenerator.free_temporal_variable(temporal)

        return template_builder

    # Visit a parse tree produced by yaplParser#add.
    def visitAdd(self, ctx: yaplParser.AddContext):
        """
        Visits an addition expression with production
        expr '+' expr
        :param ctx:
        :return:
        """

        # Needed elements for temporal code
        template_builder = TemplateBuilder()
        temporal = self.temporalGenerator.generate_temporal()
        template_builder.set_memory_address(temporal)

        # Intermediate code generated from expressions
        expression_intermediate_code = []
        for node in ctx.expr():
            result = self.visit(node)
            expression_intermediate_code.append(result)
            template_builder.add_code(result.code)

        # Quadruple
        generated_quadruple = Quadruple('+', expression_intermediate_code[0].addr, temporal,
                                        expression_intermediate_code[1].addr)
        template_builder.add_code([generated_quadruple])

        # Garbage collector
        self.temporalGenerator.free_temporal_variable(temporal)

        return template_builder

    # Visit a parse tree produced by yaplParser#letIn.
    def visitLetIn(self, ctx: yaplParser.LetInContext):
        """
        visits a letIn declaration with production
        'let' ID ':' TYPE (ASSIGNMENT expr)? (',' ID ':' TYPE (ASSIGNMENT expr)?)* IN expr
        :param ctx:
        :return:
        """
        # Template builder
        template_builder = TemplateBuilder()

        # We get the scope
        self.currentScope += 1
        visited_expression = ctx.expr()[0:-1]
        expressions_intermediate_code = []

        # We get the intermediate code for the expressions
        for node in visited_expression:
            expressions_intermediate_code.append(self.visit(node))

        # We define the intermediate code for all variables
        for i in range(len(ctx.ID())):
            # If variable has an assignment
            if i < len(ctx.ASSIGNMENT()):

                # We get the variable
                name = str(ctx.ID()[i])
                table_entry = self.attributeTable.find_entry(name, self.currentClass, self.currentMethodId,
                                                             self.currentScope)
                # We add the code for the variable
                template_builder.add_code(expressions_intermediate_code[i].code)

                # If it has a parent class
                if table_entry.parent_class:
                    template_builder.add_code([Quadruple("=", expressions_intermediate_code[i].addr,
                                                         f"LET_VARIABLE_{name}@{self.currentMethod}@{table_entry.parent_class}[{table_entry.offset}]")])
                # No parent class
                else:
                    template_builder.add_code([Quadruple("=", expressions_intermediate_code[i].addr,
                                                         f"LET_VARIABLE_@{table_entry.parent_class}[{table_entry.offset}]")])
        # We add the intermediate code of the let in node
        in_expression_node = self.visit(ctx.expr()[-1])
        template_builder.add_code(in_expression_node.code)
        template_builder.set_memory_address(in_expression_node.addr)
        return template_builder

    # Visit a parse tree produced by yaplParser#identifier.
    def visitIdentifier(self, ctx: yaplParser.IdentifierContext):
        """
        Visit an identifier production
        ID
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """

        # We get the name and entry of the variable
        variable_name = str(ctx.ID())
        table_entry = self.attributeTable.find_entry(variable_name, self.currentClass, self.currentMethodId,
                                                     self.currentScope)

        # We check if it is defined in a broader scope if it has not been found
        scope = self.currentScope
        while scope > 0:
            if table_entry is None:
                table_entry = self.attributeTable.find_entry(variable_name, self.currentClass, self.currentMethodId,
                                                             scope)
            if table_entry is None:
                table_entry = self.attributeTable.find_entry(variable_name, self.currentClass, None, scope)
            if table_entry is not None:
                break
            scope -= 1

        # Intermediate code
        template_builder = TemplateBuilder()
        if variable_name == "self":
            return template_builder

        # If ID depends on a function
        if table_entry.parent_method:
            parent_table_entry = self.functionTable.find_by_id(table_entry.parent_method)
            template_builder.set_memory_address(
                f"ID_{variable_name}@{parent_table_entry.name}@{table_entry.parent_class}[{table_entry.offset}]")
        # ID doesn't depend on a function
        else:
            template_builder.set_memory_address(f"ID_{variable_name}@{table_entry.parent_class}[{table_entry.offset}]")
        template_builder.type = table_entry.type
        return template_builder

    # Visit a parse tree produced by yaplParser#negation.
    def visitNegation(self, ctx: yaplParser.NegationContext):
        """
        Visits a negation production
        '~' expr
        :param ctx:
        :return:
        """
        # Template builder
        template_builder = TemplateBuilder()
        negated_result = self.visit(ctx.expr())

        # Temporal generation
        temporal = self.temporalGenerator.generate_temporal()
        template_builder.set_memory_address(temporal)
        template_builder.add_code(negated_result.code)
        # print("THIS IS THE RESULT", negated_result)
        template_builder.add_code([Quadruple("NOT", negated_result.addr, template_builder.addr)])

        # Garbage collector
        self.temporalGenerator.free_temporal_variable(temporal)

        return template_builder

    # Visit a parse tree produced by yaplParser#void.
    def visitVoid(self, ctx: yaplParser.VoidContext):
        """
        Visits a void production
        ISVOID expr
        :param ctx:
        :return:
        """

        # Template builder
        template_builder = TemplateBuilder()

        # Temporal
        temporal = self.temporalGenerator.generate_temporal()
        template_builder.set_memory_address(temporal)

        # Expression code
        expression_code = self.visit(ctx.expr())
        template_builder.add_code(expression_code.code)
        template_builder.add_code([Quadruple("void", expression_code.addr, template_builder.addr)])
        template_builder.type = "Bool"

        # Garbage collector
        self.temporalGenerator.free_temporal_variable(temporal)
        return template_builder

    # Visit a parse tree produced by yaplParser#string.
    def visitString(self, ctx: yaplParser.StringContext):
        """
        Visits a string with production
        STR
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """

        # Template builder
        template_builder = TemplateBuilder()

        # Note: address has string value in order to get all characters to offset in the right way
        template_builder.set_memory_address(str(ctx.STR()))
        template_builder.type = "String"
        return template_builder

    # Visit a parse tree produced by yaplParser#subtract.
    def visitSubtract(self, ctx: yaplParser.SubtractContext):
        """
        Visits a subtract production
        expr '-' expr
        :param ctx:
        :return:
        """

        # Template builder
        template_builder = TemplateBuilder()
        temporal = self.temporalGenerator.generate_temporal()
        template_builder.set_memory_address(temporal)

        # Expression codes
        expression_code = []
        for node in ctx.expr():
            result = self.visit(node)
            expression_code.append(result)
            template_builder.add_code(result.code)

        # Quadruple
        generated_quadruple = Quadruple('-', expression_code[0].addr, temporal, expression_code[1].addr)
        template_builder.add_code([generated_quadruple])

        # Garbage collector
        self.temporalGenerator.free_temporal_variable(temporal)
        return template_builder

    # Visit a parse tree produced by yaplParser#false.
    def visitFalse(self, ctx: yaplParser.FalseContext):
        """
        Visits a false expression with production
        FALSE
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        template_builder = TemplateBuilder()
        template_builder.set_memory_address(str(ctx.FALSE()))
        template_builder.type = "Bool"
        return template_builder

    # Visit a parse tree produced by yaplParser#lessOrEqual.
    def visitLessOrEqual(self, ctx: yaplParser.LessOrEqualContext):
        """
        Visits a less than or equal with production
        expr '<=' expr
        :param ctx:
        :return:
        """
        template_builder = TemplateBuilder()
        inherited_attributes = ctx.parentCtx.inheritedAttributes

        # We get the intermediate code for the expressions
        expression_codes = []
        for node in ctx.expr():
            result = self.visit(node)
            expression_codes.append(result)

        # We add the code of the expressions
        template_builder.add_code(expression_codes[0].code)
        template_builder.add_code(expression_codes[1].code)

        # We add the code
        template_builder.add_code(
            [Quadruple("<=", expression_codes[0].addr, inherited_attributes[1], expression_codes[1].addr + " goto")])
        template_builder.add_code([Quadruple("goto", inherited_attributes[2], None)])
        return template_builder

    # Visit a parse tree produced by yaplParser#assignmentExpression.
    def visitAssignmentExpression(self, ctx: yaplParser.AssignmentExpressionContext):
        """
        Visits an assignment expression with production
        ID ASSIGNMENT expr
        (ID <- expr)
        :param ctx:
        :return:
        """

        # Template builder and table entry
        template_builder = TemplateBuilder()
        variable_name = str(ctx.ID())
        table_entry = self.attributeTable.find_entry(variable_name, self.currentClass, self.currentMethodId,
                                                     self.currentScope)
        scope = self.currentScope

        # We check if variable is in other scopes
        while scope > 0:
            if table_entry is None:
                table_entry = self.attributeTable.find_entry(variable_name, self.currentClass, self.currentMethodId,
                                                             scope)
            if table_entry is None:
                table_entry = self.attributeTable.find_entry(variable_name, self.currentClass, None, scope)
            scope -= 1

        # Intermediate code for expressions
        expression_code = self.visit(ctx.expr())
        template_builder.add_code(expression_code.code)

        # If it has a parent method
        if table_entry.parent_method:
            method_table_entry = self.functionTable.find_by_id(table_entry.parent_method)
            generated_quadruple = Quadruple("=", expression_code.addr,
                                  f"ASSIGN_VARIABLE_{variable_name}@{method_table_entry.name}@{table_entry.parent_class}[{table_entry.offset}]")

            template_builder.set_memory_address(
                 f"ASSIGN_VARIABLE_{variable_name}@{method_table_entry.name}@{table_entry.parent_class}[{table_entry.offset}]")

        # No parent method
        else:
            generated_quadruple = Quadruple("=", expression_code.addr,
                                  f"ASSIGN_VARIABLE_{variable_name}@{table_entry.parent_class}[{table_entry.offset}]")
            template_builder.set_memory_address(
                f"ASSIGN_VARIABLE_{variable_name}@{table_entry.parent_class}[{table_entry.offset}]")
        template_builder.add_code([generated_quadruple])
        # print("ADDED CODE", generated_quadruple)
        return template_builder

    # Visit a parse tree produced by yaplParser#expressionContext.
    def visitExpressionContext(self, ctx: yaplParser.ExpressionContextContext):
        """
        Visits an expression context with production:
        '{' (expr ';')* '}'
        :param ctx:
        :return:
        """

        # We get the expression codes
        template_builder = TemplateBuilder()
        expression_codes = []

        # Visiting codes and adding them
        for node in ctx.expr():
            result = self.visit(node)
            expression_codes.append(result)
            template_builder.add_code(result.code)

        # We add the last address
        template_builder.addr = expression_codes[-1].addr

        return template_builder

    # Visit a parse tree produced by yaplParser#integer.
    def visitInteger(self, ctx: yaplParser.IntegerContext):
        """
        Visits an integer with production
        INT
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        template_builder = TemplateBuilder()
        template_builder.set_memory_address(str(ctx.INT()))
        template_builder.type = "Int"
        return template_builder

    # Visit a parse tree produced by yaplParser#while.
    def visitWhile(self, ctx: yaplParser.WhileContext):
        """
        Visits a while context with production
        WHILE expr LOOP expr POOL
        :param ctx:
        :return:
        """

        # We add the labels for while nodes
        template_builder = TemplateBuilder()
        while_true_label, false_condition_label, begin = self.labelGenerator.generate_while_labels()
        ctx.inheritedAttributes = (begin, while_true_label, false_condition_label)

        # We add the code for expressions in while loops
        expression_codes = []
        for node in ctx.expr():
            result = self.visit(node)
            expression_codes.append(result)

        # We add the START WHILE label
        template_builder.add_code([Quadruple("label", begin, None)])
        template_builder.add_code(expression_codes[0].code)

        # If it has a condition we have a true and a false label
        if expression_codes[0].code[-1].opp != "goto":
            template_builder.add_code([Quadruple("eq", expression_codes[0].addr, while_true_label, 1)])
            template_builder.add_code([Quadruple("goto", false_condition_label, None)])

        # True condition
        template_builder.add_code([Quadruple("label", while_true_label, None)])
        template_builder.add_code(expression_codes[1].code)

        # Loops back to start
        template_builder.add_code([Quadruple("goto", begin, None)])

        # False condition
        template_builder.add_code([Quadruple("label", false_condition_label, None)])
        template_builder.set_memory_address(expression_codes[1].addr)
        return template_builder

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

        # Temporal generation
        template_builder = TemplateBuilder()
        temporal = self.temporalGenerator.generate_temporal()
        template_builder.set_memory_address(temporal)

        # Expression intermediate codes
        expression_codes = []
        for node in ctx.expr():
            result = self.visit(node)
            expression_codes.append(result)
            template_builder.add_code(result.code)

        # Generated quadruple
        generated_quadruple = Quadruple('/', expression_codes[0].addr, temporal, expression_codes[1].addr)
        template_builder.add_code([generated_quadruple])

        # Garbage collector
        self.temporalGenerator.free_temporal_variable(temporal)

        return template_builder

    # Visit a parse tree produced by yaplParser#equal.
    def visitEqual(self, ctx: yaplParser.EqualContext):
        """
        Visits an equal production
        expr '=' expr
        :param ctx:
        :return:
        """

        # Inherited attributes
        template_builder = TemplateBuilder()
        inherited_attributes = ctx.parentCtx.inheritedAttributes

        # Expression codes
        expression_codes = []
        for node in ctx.expr():
            result = self.visit(node)
            expression_codes.append(result)

        # We add the intermediate codes
        template_builder.add_code(expression_codes[0].code)
        template_builder.add_code(expression_codes[1].code)

        # We add the code of the equal expression
        template_builder.add_code(
            [Quadruple("eq", expression_codes[0].addr, inherited_attributes[1], expression_codes[1].addr + " goto")])

        # Jump in case condition is true
        template_builder.add_code([Quadruple("goto", inherited_attributes[2], None)])

        return template_builder

    # Visit a parse tree produced by yaplParser#newObjectInstance.
    def visitNewObjectInstance(self, ctx: yaplParser.NewObjectInstanceContext):
        """
        Visits a new object with production
        NEW TYPE
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """

        # Template builder
        template_builder = TemplateBuilder()
        object_instance = str(ctx.TYPE())

        # Table entry
        table_entry = self.classTable.find_entry(object_instance)
        # print("THE CLASS ENTRY IS", table_entry)

        # We add the new instance
        template_builder.set_memory_address(f"NEW_{object_instance}{self.newCounter}")

        # This instance should be added to heap memory for everything that is not parameters
        template_builder.add_code([Quadruple("HEAP_MALLOC", table_entry.size, object_instance)])
        template_builder.type = object_instance
        self.newCounter += 1    # In case new instances of the same type are made
        # print("RETURNING", template_builder)
        return template_builder

    # Visit a parse tree produced by yaplParser#not.
    def visitNot(self, ctx: yaplParser.NotContext):
        """
        Visits a not expression with production
        NOT expr
        !!! CAN ONLY BE USED FOR BOOLs!!!
        :param ctx:
        :return:
        """

        # Template builder and temporal
        template_builder = TemplateBuilder()
        temporal = self.temporalGenerator.generate_temporal()
        template_builder.set_memory_address(temporal)

        # The expression code
        expression_code = self.visit(ctx.expr())
        template_builder.add_code(expression_code.code)
        template_builder.add_code([Quadruple("NOT", expression_code.addr, template_builder.addr)])

        # Garbage collector
        self.temporalGenerator.free_temporal_variable(temporal)

        return template_builder

    # Visit a parse tree produced by yaplParser#functionCall.
    def visitFunctionCall(self, ctx: yaplParser.FunctionCallContext):
        """
        Visits a function call with production
        ID '(' (expr (',' expr)*)? ')'
        :param ctx:
        :return:
        """
        # Template builder
        template_builder = TemplateBuilder()
        temporal = self.temporalGenerator.generate_temporal()

        # We get the intermediate code for expressions
        expression_codes = []
        for node in ctx.expr():
            result = self.visit(node)
            expression_codes.append(result)

        # We check the method in the symbol table
        method_table_entry = self.functionTable.find_by_name(str(ctx.ID()), self.currentClass)

        # If method is not defined -> inherited?
        if not method_table_entry:

            class_table_entry = self.classTable.find_entry(self.currentClass)
            method_table_entry = self.functionTable.find_by_name(str(ctx.ID()), class_table_entry.inherits)

        # We get the function parameters and declared variables
        function_parameters = self.attributeTable.get_function_parameters(method_table_entry.id)
        let_declarations = self.attributeTable.get_function_let_values(method_table_entry.id)

        # Method starts with a zero size
        size = 0
        for i in function_parameters:
            size += 8              # Memory allocation grows with each parameter
        for j in let_declarations:
            size += 8              # Memory allocation grows with each new variable

        # We allocate in stack the size required for parameters and variables
        template_builder.add_code([Quadruple("STACK_MALLOC", size, method_table_entry.id)])

        # We add the intermediate code for the expressions
        for i in range(len(expression_codes)):
            if i < len(function_parameters):
                template_builder.add_code(expression_codes[i].code)
                template_builder.add_code([Quadruple("=", expression_codes[i].addr,
                                                     f"FUNCTION_{method_table_entry.name}@{method_table_entry.parent}[{function_parameters[i].offset}]")])

        # Function call temporal code
        template_builder.add_code([Quadruple("CALL", f"{method_table_entry.name}@{method_table_entry.parent}", "method_return_address")])
        template_builder.addr = "method_return_address"
        template_builder.type = method_table_entry.type

        # Garbage collector
        self.temporalGenerator.free_temporal_variable(temporal)

        return template_builder

    # Visit a parse tree produced by yaplParser#lessThan.
    def visitLessThan(self, ctx: yaplParser.LessThanContext):
        """
        Visits a less than expression with production
        expr '<' expr
        :param ctx:
        :return:
        """

        # Template builder
        template_builder = TemplateBuilder()
        inherited_attributes = ctx.parentCtx.inheritedAttributes

        # We add the intermediate code for the expressions
        expression_codes = []
        for node in ctx.expr():
            result = self.visit(node)
            expression_codes.append(result)

        template_builder.add_code(expression_codes[0].code)
        template_builder.add_code(expression_codes[1].code)

        # Conditional code
        template_builder.add_code(
            [Quadruple("<", expression_codes[0].addr, inherited_attributes[1], expression_codes[1].addr + " goto")])

        # Goto label if condition
        template_builder.add_code([Quadruple("goto", inherited_attributes[2], None)])

        return template_builder

    # Visit a parse tree produced by yaplParser#true.
    def visitTrue(self, ctx: yaplParser.TrueContext):
        """
        Visits a true production
        TRUE
        THIS IS A TERMINAL NODE!
        :param ctx:
        :return:
        """
        template_builder = TemplateBuilder()
        template_builder.set_memory_address(str(ctx.TRUE()))
        template_builder.type = "Bool"
        return template_builder

    # Visit a parse tree produced by yaplParser#multiplication.
    def visitMultiplication(self, ctx: yaplParser.MultiplicationContext):
        """
        Visits a multiplication expression with production
        expr '*' expr
        :param ctx:
        :return:
        """
        # Template builder and temporal
        template_builder = TemplateBuilder()
        temporal = self.temporalGenerator.generate_temporal()
        template_builder.set_memory_address(temporal)

        # We get the expression temporal codes
        expression_codes = []
        for node in ctx.expr():
            result = self.visit(node)
            expression_codes.append(result)
            template_builder.add_code(result.code)

        # Generated quadruple
        generated_quadruple = Quadruple('*', expression_codes[0].addr, temporal, expression_codes[1].addr)
        template_builder.add_code([generated_quadruple])

        # Garbage collector
        self.temporalGenerator.free_temporal_variable(temporal)
        return template_builder

    # Visit a parse tree produced by yaplParser#classMethodCall.
    def visitClassMethodCall(self, ctx: yaplParser.ClassMethodCallContext):
        """
        Visits a class method call expression with production
        expr ('@' TYPE)? '.' ID '(' (expr (',' expr)*)? ')'
        :param ctx:
        :return:
        """

        # Template builder and expression codes
        template_builder = TemplateBuilder()
        expression_codes = []
        temporal = self.temporalGenerator.generate_temporal()

        # We get the expression codes
        for node in ctx.expr():
            result = self.visit(node)
            # print("JUST GOT THIS RESULT", result)
            expression_codes.append(result)

        # Adding the temporal code
        template_builder.add_code(expression_codes[0].code)

        # We get the table entry for the method
        if ctx.TYPE():
            method_table_entry = self.functionTable.find_by_name(str(ctx.ID()), str(ctx.TYPE()))
        else:
            root_class = expression_codes[0].type
            method_table_entry = self.functionTable.find_by_name(str(ctx.ID()), root_class)

            # Method could not be found, so we check parent
            if not method_table_entry:

                parent = self.classTable.find_entry(self.currentClass).inherits
                method_table_entry = self.functionTable.find_by_name(str(ctx.ID()), parent)

        # We add the type
        template_builder.type = method_table_entry.type

        # Parameters and variables declared
        method_parameters = self.attributeTable.get_function_parameters(method_table_entry.id)
        variable_declarations = self.attributeTable.get_function_let_values(method_table_entry.id)

        # We calculate the size to be allocated in memory
        size = 0
        for i in method_parameters:
            size += 8
        for j in variable_declarations:
            size += 8
        params = expression_codes[1:]
        template_builder.add_code([Quadruple("STACK_MALLOC", size, method_table_entry.id)])

        # We add the code
        for i in range(len(params)):
            if i < len(method_parameters):
                template_builder.add_code(params[i].code)
                template_builder.add_code(
                    [Quadruple("=", params[i].addr, f"FUNCTION_{method_table_entry.name}@{method_table_entry.parent}[{method_parameters[i].offset}]")])

        # Function call and return address
        template_builder.add_code([Quadruple("CALL", f"{method_table_entry.name}@{method_table_entry.parent}", "method_return_address")])
        template_builder.set_memory_address("method_return_address")

        # Garbage collector
        self.temporalGenerator.free_temporal_variable(temporal)

        return template_builder

    # Visit a parse tree produced by yaplParser#ifElse.
    def visitIfElse(self, ctx: yaplParser.IfElseContext):
        """
        Visits an ifElse expression with production
        IF expr THEN expr ELSE expr FI
        :param ctx:
        :return:
        """

        # Template builder
        template_builder = TemplateBuilder()

        # Return label
        return_label = self.labelGenerator.generate_return_label()

        # If true, if false labels
        if_true_label, if_false_label = self.labelGenerator.generate_if_else_labels()
        ctx.inheritedAttributes = (return_label, if_true_label, if_false_label)

        # Temporal
        temporal = self.temporalGenerator.generate_temporal()

        # Expression codes
        expression_codes = []
        template_builder.next = return_label
        for node in ctx.expr():
            result = self.visit(node)
            expression_codes.append(result)

        # Conditional code
        template_builder.add_code(expression_codes[0].code)

        # We check if it should jump
        if expression_codes[0].code[-1].opp != "goto":
            template_builder.add_code([Quadruple("eq", expression_codes[0].addr, if_true_label, 1)])
            template_builder.add_code([Quadruple("goto", if_false_label, None)])

        # If condition is true
        template_builder.add_code([Quadruple("label", if_true_label, None)])
        template_builder.add_code(expression_codes[1].code)
        template_builder.add_code([Quadruple("=", expression_codes[1].addr, temporal)])
        template_builder.add_code([Quadruple("goto", return_label, None)])

        # If condition is false
        template_builder.add_code([Quadruple("label", if_false_label, None)])
        template_builder.add_code(expression_codes[2].code)
        template_builder.add_code([Quadruple("=", expression_codes[2].addr, temporal)])
        template_builder.add_code([Quadruple("label", return_label, None)])

        # We set the memory address to the temporal
        template_builder.set_memory_address(temporal)

        # Garbage collector
        self.temporalGenerator.free_temporal_variable(temporal)
        return template_builder


del yaplParser
