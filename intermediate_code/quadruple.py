class Quadruple:
    """
    Quadruples define structures for intermediate code
    """

    def __init__(self, operator, argument_1, destination, argument_2=None):
        # destination = argument_1 operator argument_2
        self.opp = operator
        self.arg1 = argument_1
        self.arg2 = argument_2
        self.result = destination

    def __repr__(self):
        """
        Prints the quadruples once code is ready
        :return: string representation of quadruple
        """
        if self.opp == "=":
            # <value> = <value>
            return f"   {self.result} {self.opp} {self.arg1}"
        elif self.opp == "label":
            # <label>:
            return f"\n{self.arg1}:\n"
        elif self.opp == "goto":
            # goto <label>
            return f"   {self.opp} {self.arg1}"
        elif self.opp == "<" or self.opp == "<=" or self.opp == "eq":
            # <value> <operation> <value> <goto_if_true>
            return f"   {self.arg1} {self.opp} {self.arg2} {self.result}"
        elif self.opp == "STACK_MALLOC" or self.opp == "HEAP_MALLOC":
            # <allocation>[<address>]
            return f"   {self.opp}@{self.result}[{self.arg1}]"
        elif self.opp == "CALL":
            result_string = ""
            if self.result is not None:
                result_string = f"{self.result} = "
            # <call> <function>
            return f"   {result_string}{self.opp} {self.arg1}"
        # Note that ~ and NOT operators are both handled as NOT in intermediate code
        elif self.opp == "NOT":
            # <result> = not <value>
            return f"   {self.result} = not {self.arg1}"
        elif self.opp == "void":
            # <result> isVoid <value>
            return f"   {self.result} = isVoid {self.arg1}"
        elif self.opp == "param":
            # param[<name>] <temporal>
            return f"   {self.opp}{self.arg1} {self.result}"
        elif self.opp == "blank":
            # No operation
            return "BLANK_DEBUGGING"
        elif self.arg2:
            # <result> = <value> <operation> <value>
            return f"   {self.result} = {self.arg1} {self.opp} {self.arg2}"
        else:
            # <result> = <operation><value>
            return f"   {self.result} = {self.opp}{self.arg1}"
