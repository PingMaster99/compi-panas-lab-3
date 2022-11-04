# Generated from yapl.g4 by ANTLR 4.10.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .yaplParser import yaplParser
else:
    from yaplParser import yaplParser

# This class defines a complete generic visitor for a parse tree produced by yaplParser.

class yaplVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by yaplParser#start.
    def visitStart(self, ctx:yaplParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#program.
    def visitProgram(self, ctx:yaplParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#classSpecification.
    def visitClassSpecification(self, ctx:yaplParser.ClassSpecificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#method.
    def visitMethod(self, ctx:yaplParser.MethodContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#attribute.
    def visitAttribute(self, ctx:yaplParser.AttributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#formal.
    def visitFormal(self, ctx:yaplParser.FormalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#add.
    def visitAdd(self, ctx:yaplParser.AddContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#letIn.
    def visitLetIn(self, ctx:yaplParser.LetInContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#identifier.
    def visitIdentifier(self, ctx:yaplParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#negation.
    def visitNegation(self, ctx:yaplParser.NegationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#void.
    def visitVoid(self, ctx:yaplParser.VoidContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#string.
    def visitString(self, ctx:yaplParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#subtract.
    def visitSubtract(self, ctx:yaplParser.SubtractContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#false.
    def visitFalse(self, ctx:yaplParser.FalseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#lessOrEqual.
    def visitLessOrEqual(self, ctx:yaplParser.LessOrEqualContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#expressionContext.
    def visitExpressionContext(self, ctx:yaplParser.ExpressionContextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#assignmentExpression.
    def visitAssignmentExpression(self, ctx:yaplParser.AssignmentExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#integer.
    def visitInteger(self, ctx:yaplParser.IntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#while.
    def visitWhile(self, ctx:yaplParser.WhileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#parenthesis.
    def visitParenthesis(self, ctx:yaplParser.ParenthesisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#division.
    def visitDivision(self, ctx:yaplParser.DivisionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#equal.
    def visitEqual(self, ctx:yaplParser.EqualContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#newObjectInstance.
    def visitNewObjectInstance(self, ctx:yaplParser.NewObjectInstanceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#not.
    def visitNot(self, ctx:yaplParser.NotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#functionCall.
    def visitFunctionCall(self, ctx:yaplParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#lessThan.
    def visitLessThan(self, ctx:yaplParser.LessThanContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#true.
    def visitTrue(self, ctx:yaplParser.TrueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#multiplication.
    def visitMultiplication(self, ctx:yaplParser.MultiplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#classMethodCall.
    def visitClassMethodCall(self, ctx:yaplParser.ClassMethodCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yaplParser#ifElse.
    def visitIfElse(self, ctx:yaplParser.IfElseContext):
        return self.visitChildren(ctx)



del yaplParser