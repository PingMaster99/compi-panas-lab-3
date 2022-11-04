# Generated from yapl.g4 by ANTLR 4.10.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .yaplParser import yaplParser
else:
    from yaplParser import yaplParser

# This class defines a complete listener for a parse tree produced by yaplParser.
class yaplListener(ParseTreeListener):

    # Enter a parse tree produced by yaplParser#start.
    def enterStart(self, ctx:yaplParser.StartContext):
        pass

    # Exit a parse tree produced by yaplParser#start.
    def exitStart(self, ctx:yaplParser.StartContext):
        pass


    # Enter a parse tree produced by yaplParser#program.
    def enterProgram(self, ctx:yaplParser.ProgramContext):
        pass

    # Exit a parse tree produced by yaplParser#program.
    def exitProgram(self, ctx:yaplParser.ProgramContext):
        pass


    # Enter a parse tree produced by yaplParser#classSpecification.
    def enterClassSpecification(self, ctx:yaplParser.ClassSpecificationContext):
        pass

    # Exit a parse tree produced by yaplParser#classSpecification.
    def exitClassSpecification(self, ctx:yaplParser.ClassSpecificationContext):
        pass


    # Enter a parse tree produced by yaplParser#method.
    def enterMethod(self, ctx:yaplParser.MethodContext):
        pass

    # Exit a parse tree produced by yaplParser#method.
    def exitMethod(self, ctx:yaplParser.MethodContext):
        pass


    # Enter a parse tree produced by yaplParser#attribute.
    def enterAttribute(self, ctx:yaplParser.AttributeContext):
        pass

    # Exit a parse tree produced by yaplParser#attribute.
    def exitAttribute(self, ctx:yaplParser.AttributeContext):
        pass


    # Enter a parse tree produced by yaplParser#formal.
    def enterFormal(self, ctx:yaplParser.FormalContext):
        pass

    # Exit a parse tree produced by yaplParser#formal.
    def exitFormal(self, ctx:yaplParser.FormalContext):
        pass


    # Enter a parse tree produced by yaplParser#add.
    def enterAdd(self, ctx:yaplParser.AddContext):
        pass

    # Exit a parse tree produced by yaplParser#add.
    def exitAdd(self, ctx:yaplParser.AddContext):
        pass


    # Enter a parse tree produced by yaplParser#letIn.
    def enterLetIn(self, ctx:yaplParser.LetInContext):
        pass

    # Exit a parse tree produced by yaplParser#letIn.
    def exitLetIn(self, ctx:yaplParser.LetInContext):
        pass


    # Enter a parse tree produced by yaplParser#identifier.
    def enterIdentifier(self, ctx:yaplParser.IdentifierContext):
        pass

    # Exit a parse tree produced by yaplParser#identifier.
    def exitIdentifier(self, ctx:yaplParser.IdentifierContext):
        pass


    # Enter a parse tree produced by yaplParser#negation.
    def enterNegation(self, ctx:yaplParser.NegationContext):
        pass

    # Exit a parse tree produced by yaplParser#negation.
    def exitNegation(self, ctx:yaplParser.NegationContext):
        pass


    # Enter a parse tree produced by yaplParser#void.
    def enterVoid(self, ctx:yaplParser.VoidContext):
        pass

    # Exit a parse tree produced by yaplParser#void.
    def exitVoid(self, ctx:yaplParser.VoidContext):
        pass


    # Enter a parse tree produced by yaplParser#string.
    def enterString(self, ctx:yaplParser.StringContext):
        pass

    # Exit a parse tree produced by yaplParser#string.
    def exitString(self, ctx:yaplParser.StringContext):
        pass


    # Enter a parse tree produced by yaplParser#subtract.
    def enterSubtract(self, ctx:yaplParser.SubtractContext):
        pass

    # Exit a parse tree produced by yaplParser#subtract.
    def exitSubtract(self, ctx:yaplParser.SubtractContext):
        pass


    # Enter a parse tree produced by yaplParser#false.
    def enterFalse(self, ctx:yaplParser.FalseContext):
        pass

    # Exit a parse tree produced by yaplParser#false.
    def exitFalse(self, ctx:yaplParser.FalseContext):
        pass


    # Enter a parse tree produced by yaplParser#lessOrEqual.
    def enterLessOrEqual(self, ctx:yaplParser.LessOrEqualContext):
        pass

    # Exit a parse tree produced by yaplParser#lessOrEqual.
    def exitLessOrEqual(self, ctx:yaplParser.LessOrEqualContext):
        pass


    # Enter a parse tree produced by yaplParser#expressionContext.
    def enterExpressionContext(self, ctx:yaplParser.ExpressionContextContext):
        pass

    # Exit a parse tree produced by yaplParser#expressionContext.
    def exitExpressionContext(self, ctx:yaplParser.ExpressionContextContext):
        pass


    # Enter a parse tree produced by yaplParser#assignmentExpression.
    def enterAssignmentExpression(self, ctx:yaplParser.AssignmentExpressionContext):
        pass

    # Exit a parse tree produced by yaplParser#assignmentExpression.
    def exitAssignmentExpression(self, ctx:yaplParser.AssignmentExpressionContext):
        pass


    # Enter a parse tree produced by yaplParser#integer.
    def enterInteger(self, ctx:yaplParser.IntegerContext):
        pass

    # Exit a parse tree produced by yaplParser#integer.
    def exitInteger(self, ctx:yaplParser.IntegerContext):
        pass


    # Enter a parse tree produced by yaplParser#while.
    def enterWhile(self, ctx:yaplParser.WhileContext):
        pass

    # Exit a parse tree produced by yaplParser#while.
    def exitWhile(self, ctx:yaplParser.WhileContext):
        pass


    # Enter a parse tree produced by yaplParser#parenthesis.
    def enterParenthesis(self, ctx:yaplParser.ParenthesisContext):
        pass

    # Exit a parse tree produced by yaplParser#parenthesis.
    def exitParenthesis(self, ctx:yaplParser.ParenthesisContext):
        pass


    # Enter a parse tree produced by yaplParser#division.
    def enterDivision(self, ctx:yaplParser.DivisionContext):
        pass

    # Exit a parse tree produced by yaplParser#division.
    def exitDivision(self, ctx:yaplParser.DivisionContext):
        pass


    # Enter a parse tree produced by yaplParser#equal.
    def enterEqual(self, ctx:yaplParser.EqualContext):
        pass

    # Exit a parse tree produced by yaplParser#equal.
    def exitEqual(self, ctx:yaplParser.EqualContext):
        pass


    # Enter a parse tree produced by yaplParser#newObjectInstance.
    def enterNewObjectInstance(self, ctx:yaplParser.NewObjectInstanceContext):
        pass

    # Exit a parse tree produced by yaplParser#newObjectInstance.
    def exitNewObjectInstance(self, ctx:yaplParser.NewObjectInstanceContext):
        pass


    # Enter a parse tree produced by yaplParser#not.
    def enterNot(self, ctx:yaplParser.NotContext):
        pass

    # Exit a parse tree produced by yaplParser#not.
    def exitNot(self, ctx:yaplParser.NotContext):
        pass


    # Enter a parse tree produced by yaplParser#functionCall.
    def enterFunctionCall(self, ctx:yaplParser.FunctionCallContext):
        pass

    # Exit a parse tree produced by yaplParser#functionCall.
    def exitFunctionCall(self, ctx:yaplParser.FunctionCallContext):
        pass


    # Enter a parse tree produced by yaplParser#lessThan.
    def enterLessThan(self, ctx:yaplParser.LessThanContext):
        pass

    # Exit a parse tree produced by yaplParser#lessThan.
    def exitLessThan(self, ctx:yaplParser.LessThanContext):
        pass


    # Enter a parse tree produced by yaplParser#true.
    def enterTrue(self, ctx:yaplParser.TrueContext):
        pass

    # Exit a parse tree produced by yaplParser#true.
    def exitTrue(self, ctx:yaplParser.TrueContext):
        pass


    # Enter a parse tree produced by yaplParser#multiplication.
    def enterMultiplication(self, ctx:yaplParser.MultiplicationContext):
        pass

    # Exit a parse tree produced by yaplParser#multiplication.
    def exitMultiplication(self, ctx:yaplParser.MultiplicationContext):
        pass


    # Enter a parse tree produced by yaplParser#classMethodCall.
    def enterClassMethodCall(self, ctx:yaplParser.ClassMethodCallContext):
        pass

    # Exit a parse tree produced by yaplParser#classMethodCall.
    def exitClassMethodCall(self, ctx:yaplParser.ClassMethodCallContext):
        pass


    # Enter a parse tree produced by yaplParser#ifElse.
    def enterIfElse(self, ctx:yaplParser.IfElseContext):
        pass

    # Exit a parse tree produced by yaplParser#ifElse.
    def exitIfElse(self, ctx:yaplParser.IfElseContext):
        pass



del yaplParser