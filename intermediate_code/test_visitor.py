# Generated from YAPL2.g4 by ANTLR 4.10.1
from grammar.yaplParser import yaplParser
from grammar.yaplVisitor import yaplVisitor
from intermediate_code.intermediate_template_builder import *
from intermediate_code.quadruple import Quadruple

class IntermediateCodeGenerator():

    def __init__(self, classTable, functionTable, attributeTable, typesTable):
        super().__init__()
        self.functionTable = functionTable
        self.attributeTable = attributeTable
        self.typesTable = typesTable
        self.classTable = classTable
        self.temporalGenerator = TemporalGenerator()
        self.labelGenerator = LabelGenerator()
        self.currentClass = None
        self.currentMethodId = 10
        self.currentScope = 1
        self.currentMethod = None
        self.newCounter = 0

    # Visit a parse tree produced by yaplParser#program.
    def visitStart(self, ctx: yaplParser.StartContext):
        result = self.visit(ctx.program())
        return result

    # Visit a parse tree produced by yaplParser#programBlock.
    def visitProgram(self, ctx: yaplParser.ProgramContext):
        productionInfo = TemplateBuilder()
        if not ctx.EOF():
            classdefResult = self.visit(ctx.classDEF())
            programBlockResult = self.visit(ctx.programBlock())
            productionInfo.add_code(classdefResult.code)
            productionInfo.add_code(programBlockResult.code)
        return productionInfo

    # Visit a parse tree produced by yaplParser#classDEF.
    def visitClassSpecification(self, ctx: yaplParser.ClassDEFContext):
        className = str(ctx.TYPEID()[0])
        self.currentClass = className
        self.currentMethod = None
        self.currentScope = 1
        productionInfo = TemplateBuilder()
        productionInfo.add_code([Quadruple('label', "innit@{0}".format(className), None)])

        for node in ctx.feature():
            result = self.visit(node)
            productionInfo.add_code(result.code)
        return productionInfo

    # Visit a parse tree produced by yaplParser#MethodDef.
    def visitMethodDef(self, ctx: yaplParser.MethodDefContext):
        productionInfo = TemplateBuilder()
        functionName = str(ctx.OBJECTID())
        self.currentMethodId += 1
        self.currentScope = 2
        childResult = self.visit(ctx.expr())
        productionInfo.add_code([Quadruple("label", "{0}@{1}".format(functionName, self.currentClass), None)])
        productionInfo.add_code(childResult.code)
        productionInfo.add_code([Quadruple("=", childResult.addr, "functionCallReturnAddr")])
        # print(productionInfo)
        return productionInfo

    # Visit a parse tree produced by yaplParser#FeactureDecalration.
    def visitFeactureDecalration(self, ctx: yaplParser.FeactureDecalrationContext):
        productionInfo = TemplateBuilder()
        assignTo = str(ctx.OBJECTID())
        assignToEntry = self.attributeTable.findEntry(assignTo, self.currentClass, None, self.currentScope)
        if ctx.expr():
            result = self.visit(ctx.expr())
            productionInfo.add_code(result.code)
            codeToAdd = Quadruple("=", result.addr,
                                  "OBJECT_{0}[{1}]".format(assignToEntry.inClass, assignToEntry.offset))
            productionInfo.add_code([codeToAdd])
        else:
            if assignToEntry.type == "Int":
                codeToAdd = Quadruple("=", 0, "OBJECT_{0}[{1}]".format(assignToEntry.inClass, assignToEntry.offset))
            elif assignToEntry.type == "Bool":
                codeToAdd = Quadruple("=", 0, "OBJECT_{0}[{1}]".format(assignToEntry.inClass, assignToEntry.offset))
            elif assignToEntry.type == "String":
                codeToAdd = Quadruple("=", '', "OBJECT_{0}[{1}]".format(assignToEntry.inClass, assignToEntry.offset))
            else:
                pass
        return productionInfo

    # Visit a parse tree produced by yaplParser#formal.
    def visitFormal(self, ctx: yaplParser.FormalContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by yaplParser#newExpr.
    def visitNewExpr(self, ctx: yaplParser.NewExprContext):
        productionInfo = TemplateBuilder()
        newInstance = str(ctx.TYPEID())
        classEntry = self.classTable.findEntry(newInstance)
        productionInfo.setAddr("Object_{0}{1}".format(newInstance, self.newCounter))
        productionInfo.add_code([Quadruple("allocate_in_heap", classEntry.size, None)])
        productionInfo.type = newInstance
        self.newCounter += 1
        return productionInfo

    # Visit a parse tree produced by yaplParser#divideExpr.
    def visitDivideExpr(self, ctx: yaplParser.DivideExprContext):
        productionInfo = TemplateBuilder()
        address = self.temporalGenerator.newTemporal()
        productionInfo.setAddr(address)
        childrenResults = []
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
            productionInfo.add_code(result.code)
        productionCode = Quadruple('/', childrenResults[0].addr, address, childrenResults[1].addr)
        productionInfo.add_code([productionCode])
        return productionInfo

    # Visit a parse tree produced by yaplParser#FunctionExpr.
    def visitFunctionExpr(self, ctx: yaplParser.FunctionExprContext):
        productionInfo = TemplateBuilder()
        childrenResults = []
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
        # Find the entry of the function in current class
        methodEntry = self.functionTable.findEntryByName(str(ctx.OBJECTID()), self.currentClass)
        # Search it in parent class
        if not methodEntry:
            usingClass = self.classTable.findEntry(self.currentClass)
            methodEntry = self.functionTable.findEntryByName(str(ctx.OBJECTID()), usingClass.inherits)
        savedParams = self.attributeTable.findParamsOfFunction(methodEntry.id)
        letDefinitions = self.attributeTable.findLetsOffFunction(methodEntry.id)
        size = 0
        for i in savedParams:
            size += i.size
        for j in letDefinitions:
            size += j.size
        productionInfo.add_code([Quadruple("allocate_in_stack", size, None)])
        for i in range(len(childrenResults)):
            if i < len(savedParams):
                productionInfo.add_code(childrenResults[i].code)
                productionInfo.add_code([Quadruple("=", childrenResults[i].addr,
                                                  "Function_{0}@{1}[{2}]".format(methodEntry.name,
                                                                                 methodEntry.belongsTo,
                                                                                 savedParams[i].offset))])
        productionInfo.add_code([Quadruple("call", "{}@{}".format(methodEntry.name, methodEntry.belongsTo), None)])
        productionInfo.addr = "functionCallReturnAddr"
        productionInfo.type = methodEntry.type
        return productionInfo

    # Visit a parse tree produced by yaplParser#integerExpr.
    def visitIntegerExpr(self, ctx: yaplParser.IntegerExprContext):
        productionInfo = TemplateBuilder()
        productionInfo.setAddr(str(ctx.INTEGERS()))
        productionInfo.type = "Int"
        return productionInfo

    # Visit a parse tree produced by yaplParser#trueExpr.
    def visitTrueExpr(self, ctx: yaplParser.TrueExprContext):
        productionInfo = TemplateBuilder()
        productionInfo.setAddr(str(ctx.TRUE()))
        productionInfo.type = "Bool"
        return productionInfo

    # Visit a parse tree produced by yaplParser#MethodExpr.
    def visitMethodExpr(self, ctx: yaplParser.MethodExprContext):
        productionInfo = TemplateBuilder()
        childrenResults = []
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
        productionInfo.add_code(childrenResults[0].code)
        print(childrenResults)
        # Find the entry of the function in current class
        if ctx.TYPEID():
            methodEntry = self.functionTable.findEntryByName(str(ctx.OBJECTID()), str(ctx.TYPEID()))
        else:
            mainClass = childrenResults[0].type
            methodEntry = self.functionTable.findEntryByName(str(ctx.OBJECTID()), mainClass)
            if not methodEntry:
                parentClass = self.classTable.findEntry(self.currentClass).inherits
                methodEntry = self.functionTable.findEntryByName(str(ctx.OBJECTID()), parentClass)
        productionInfo.type = methodEntry.type
        savedParams = self.attributeTable.findParamsOfFunction(methodEntry.id)
        letDefinitions = self.attributeTable.findLetsOffFunction(methodEntry.id)
        size = 0
        for i in savedParams:
            size += i.size
        for j in letDefinitions:
            size += j.size
        params = childrenResults[1:]
        productionInfo.add_code([Quadruple("allocate_in_stack", size, None)])
        for i in range(len(params)):
            if i < len(savedParams):
                productionInfo.add_code(params[i].code)
                productionInfo.add_code([Quadruple("=", params[i].addr, "Function_{0}@{1}[{2}]".format(methodEntry.name,
                                                                                                      methodEntry.belongsTo,
                                                                                                      savedParams[
                                                                                                          i].offset))])
        productionInfo.add_code([Quadruple("call", "{}@{}".format(methodEntry.name, methodEntry.belongsTo), None)])
        productionInfo.setAddr("functionCallReturnAddr")
        return productionInfo

    # Visit a parse tree produced by yaplParser#DeclarationExpression.
    def visitDeclarationExpression(self, ctx: yaplParser.DeclarationExpressionContext):
        productionInfo = TemplateBuilder()
        assignTo = str(ctx.OBJECTID())
        assignToEntry = self.attributeTable.findEntry(assignTo, self.currentClass, self.currentMethodId,
                                                      self.currentScope)
        scope = self.currentScope
        while scope > 0:
            if assignToEntry is None:
                assignToEntry = self.attributeTable.findEntry(assignTo, self.currentClass, self.currentMethodId, scope)
            if assignToEntry is None:
                assignToEntry = self.attributeTable.findEntry(assignTo, self.currentClass, None, scope)
            scope -= 1
        childrenResult = self.visit(ctx.expr())
        productionInfo.add_code(childrenResult.code)
        if assignToEntry.inMethod:
            methodEntry = self.functionTable.findEntryByID(assignToEntry.inMethod)
            codeToAdd = Quadruple("=", childrenResult.addr,
                                  "Function_{0}@{1}[{2}]".format(methodEntry.name, assignToEntry.inClass,
                                                                 assignToEntry.offset))
            productionInfo.setAddr(
                "Function_{0}@{1}[{2}]".format(methodEntry.name, assignToEntry.inClass, assignToEntry.offset))
        else:
            codeToAdd = Quadruple("=", childrenResult.addr,
                                  "OBJECT_{0}[{1}]".format(assignToEntry.inClass, assignToEntry.offset))
            productionInfo.setAddr("OBJECT_{0}[{1}]".format(assignToEntry.inClass, assignToEntry.offset))
        productionInfo.add_code([codeToAdd])
        return productionInfo

    # Visit a parse tree produced by yaplParser#ifElseExpr.
    def visitIfElseExpr(self, ctx: yaplParser.IfElseExprContext):
        productionInfo = TemplateBuilder()
        next = self.labelGenerator.generateNext()
        booleanTrue, booleanFalse = self.labelGenerator.generateIfLabels()
        ctx.inheritedAttributes = (next, booleanTrue, booleanFalse)
        returnAddr = self.temporalGenerator.newTemporal()
        childrenResults = []
        productionInfo.next = next
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
        productionInfo.add_code(childrenResults[0].code)
        if childrenResults[0].code[-1].opp != "goto":
            productionInfo.add_code([Quadruple("eq", childrenResults[0].addr, booleanTrue, 1)])
            productionInfo.add_code([Quadruple("goto", booleanFalse, None)])
        productionInfo.add_code([Quadruple("label", booleanTrue, None)])
        productionInfo.add_code(childrenResults[1].code)
        productionInfo.add_code([Quadruple("=", childrenResults[1].addr, returnAddr)])
        productionInfo.add_code([Quadruple("goto", next, None)])
        productionInfo.add_code([Quadruple("label", booleanFalse, None)])
        productionInfo.add_code(childrenResults[2].code)
        productionInfo.add_code([Quadruple("=", childrenResults[2].addr, returnAddr)])
        productionInfo.add_code([Quadruple("label", next, None)])
        productionInfo.setAddr(returnAddr)
        # print(productionInfo)
        return productionInfo

    # Visit a parse tree produced by yaplParser#lessExpr.
    def visitLessExpr(self, ctx: yaplParser.LessExprContext):
        productionInfo = TemplateBuilder()
        inheritedAtributes = ctx.parentCtx.inheritedAttributes
        childrenResults = []
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
        productionInfo.add_code(childrenResults[0].code)
        productionInfo.add_code(childrenResults[1].code)
        productionInfo.add_code(
            [Quadruple("<", childrenResults[0].addr, inheritedAtributes[1], childrenResults[1].addr)])
        productionInfo.add_code([Quadruple("goto", inheritedAtributes[2], None)])
        return productionInfo

    # Visit a parse tree produced by yaplParser#BraketedExpr.
    def visitBraketedExpr(self, ctx: yaplParser.BraketedExprContext):
        productionInfo = TemplateBuilder()
        childrenResults = []
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
            productionInfo.add_code(result.code)
        productionInfo.addr = childrenResults[-1].addr
        # print(productionInfo)

        return productionInfo

    # Visit a parse tree produced by yaplParser#multiplyExpr.
    def visitMultiplyExpr(self, ctx: yaplParser.MultiplyExprContext):
        productionInfo = TemplateBuilder()
        address = self.temporalGenerator.newTemporal()
        productionInfo.setAddr(address)
        childrenResults = []
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
            productionInfo.add_code(result.code)
        productionCode = Quadruple('*', childrenResults[0].addr, address, childrenResults[1].addr)
        productionInfo.add_code([productionCode])
        return productionInfo

    # Visit a parse tree produced by yaplParser#letExpr.
    def visitLetExpr(self, ctx: yaplParser.LetExprContext):
        productionInfo = TemplateBuilder()
        self.currentScope += 1
        firstVisits = ctx.expr()[0:-1]
        firstVisitsResutls = []
        for node in firstVisits:
            firstVisitsResutls.append(self.visit(node))
        for i in range(len(ctx.OBJECTID())):
            if i < len(ctx.ASIGNOPP()):
                name = str(ctx.OBJECTID()[i])
                varEntry = self.attributeTable.findEntry(name, self.currentClass, self.currentMethodId,
                                                         self.currentScope)
                productionInfo.add_code(firstVisitsResutls[i].code)
                if varEntry.inClass:
                    productionInfo.add_code([Quadruple("=", firstVisitsResutls[i].addr,
                                                      "Function_{0}@{1}[{2}]".format(self.currentMethod,
                                                                                     varEntry.inClass,
                                                                                     varEntry.offset))])
                else:
                    productionInfo.add_code([Quadruple("=", firstVisitsResutls[i].addr,
                                                      "Object_{}[{}]".format(varEntry.inClass, varEntry.offset))])
        lastChild = self.visit(ctx.expr()[-1])
        productionInfo.add_code(lastChild.code)
        productionInfo.setAddr(lastChild.addr)
        return productionInfo

    # Visit a parse tree produced by yaplParser#stringExpr.
    def visitStringExpr(self, ctx: yaplParser.StringExprContext):
        productionInfo = TemplateBuilder()
        productionInfo.setAddr(str(ctx.STRINGS()))
        productionInfo.type = "String"
        return productionInfo

    # Visit a parse tree produced by yaplParser#lessEqualExpr.
    def visitLessEqualExpr(self, ctx: yaplParser.LessEqualExprContext):
        productionInfo = TemplateBuilder()
        inheritedAtributes = ctx.parentCtx.inheritedAttributes
        childrenResults = []
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
        productionInfo.add_code(childrenResults[0].code)
        productionInfo.add_code(childrenResults[1].code)
        productionInfo.add_code(
            [Quadruple("<=", childrenResults[0].addr, inheritedAtributes[1], childrenResults[1].addr)])
        productionInfo.add_code([Quadruple("goto", inheritedAtributes[2], None)])
        return productionInfo

    # Visit a parse tree produced by yaplParser#notExpr.
    def visitNotExpr(self, ctx: yaplParser.NotExprContext):
        productionInfo = TemplateBuilder()
        productionInfo.setAddr(self.temporalGenerator.newTemporal())
        chidlrenResult = self.visit(ctx.expr())
        productionInfo.add_code(chidlrenResult.code)
        productionInfo.add_code([Quadruple("!=", chidlrenResult.addr, productionInfo.addr)])
        return productionInfo

    # Visit a parse tree produced by yaplParser#whileExpr.
    def visitWhileExpr(self, ctx: yaplParser.WhileExprContext):
        productionInfo = TemplateBuilder()
        trueLabel, falseLabel, begin = self.labelGenerator.generateWhileLables()
        ctx.inheritedAttributes = (begin, trueLabel, falseLabel)
        childrenResults = []
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
        productionInfo.add_code([Quadruple("label", begin, None)])
        productionInfo.add_code(childrenResults[0].code)
        if childrenResults[0].code[-1].opp != "goto":
            productionInfo.add_code([Quadruple("eq", childrenResults[0].addr, trueLabel, 1)])
            productionInfo.add_code([Quadruple("goto", falseLabel, None)])
        productionInfo.add_code([Quadruple("label", trueLabel, None)])
        productionInfo.add_code(childrenResults[1].code)
        productionInfo.add_code([Quadruple("goto", begin, None)])
        productionInfo.add_code([Quadruple("label", falseLabel, None)])
        productionInfo.setAddr(childrenResults[1].addr)
        # print(productionInfo)
        return productionInfo

    # Visit a parse tree produced by yaplParser#addExpr.
    def visitAddExpr(self, ctx: yaplParser.AddExprContext):
        productionInfo = TemplateBuilder()
        address = self.temporalGenerator.newTemporal()
        productionInfo.setAddr(address)
        childrenResults = []
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
            productionInfo.add_code(result.code)
        productionCode = Quadruple('+', childrenResults[0].addr, address, childrenResults[1].addr)
        productionInfo.add_code([productionCode])
        return productionInfo

    # Visit a parse tree produced by yaplParser#isVoidExpr.
    def visitIsVoidExpr(self, ctx: yaplParser.IsVoidExprContext):
        productionInfo = TemplateBuilder()
        productionInfo.setAddr(self.temporalGenerator.newTemporal())
        chidlrenResult = self.visit(ctx.expr())
        productionInfo.add_code(chidlrenResult.code)
        productionInfo.add_code([Quadruple("void", chidlrenResult.addr, productionInfo.addr)])
        productionInfo.type = "Bool"
        return productionInfo

    # Visit a parse tree produced by yaplParser#objectIdExpr.
    def visitObjectIdExpr(self, ctx: yaplParser.ObjectIdExprContext):
        varName = str(ctx.OBJECTID())
        varEntry = self.attributeTable.findEntry(varName, self.currentClass, self.currentMethodId, self.currentScope)
        scope = self.currentScope
        while scope > 0:
            if varEntry is None:
                varEntry = self.attributeTable.findEntry(varName, self.currentClass, self.currentMethodId, scope)
            if varEntry is None:
                varEntry = self.attributeTable.findEntry(varName, self.currentClass, None, scope)
            if varEntry is not None:
                break
            scope -= 1
        productionInfo = TemplateBuilder()
        if varName == "self":
            return productionInfo
        if varEntry.inMethod:
            methodEntry = self.functionTable.findEntryByID(varEntry.inMethod)
            productionInfo.setAddr("Function_{0}@{1}[{2}]".format(methodEntry.name, varEntry.inClass, varEntry.offset))
        else:
            productionInfo.setAddr("OBJECT_{0}[{1}]".format(varEntry.inClass, varEntry.offset))
        productionInfo.type = varEntry.type
        return productionInfo

    # Visit a parse tree produced by yaplParser#substractExpr.
    def visitSubstractExpr(self, ctx: yaplParser.SubstractExprContext):
        productionInfo = TemplateBuilder()
        address = self.temporalGenerator.newTemporal()
        productionInfo.setAddr(address)
        childrenResults = []
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
            productionInfo.add_code(result.code)
        productionCode = Quadruple('-', childrenResults[0].addr, address, childrenResults[1].addr)
        productionInfo.add_code([productionCode])
        return productionInfo

    # Visit a parse tree produced by yaplParser#falseExpr.
    def visitFalseExpr(self, ctx: yaplParser.FalseExprContext):
        productionInfo = TemplateBuilder()
        productionInfo.setAddr(str(ctx.FALSE()))
        productionInfo.type = "Bool"
        return productionInfo

    # Visit a parse tree produced by yaplParser#parenthExpr.
    def visitParenthExpr(self, ctx: yaplParser.ParenthExprContext):
        productionInfo = self.visit(ctx.expr())
        return productionInfo

    # Visit a parse tree produced by yaplParser#equalExpr.
    def visitEqualExpr(self, ctx: yaplParser.EqualExprContext):
        productionInfo = TemplateBuilder()
        inheritedAtributes = ctx.parentCtx.inheritedAttributes
        childrenResults = []
        for node in ctx.expr():
            result = self.visit(node)
            childrenResults.append(result)
        productionInfo.add_code(childrenResults[0].code)
        productionInfo.add_code(childrenResults[1].code)
        productionInfo.add_code(
            [Quadruple("eq", childrenResults[0].addr, inheritedAtributes[1], childrenResults[1].addr)])
        productionInfo.add_code([Quadruple("goto", inheritedAtributes[2], None)])
        return productionInfo


del yaplParser