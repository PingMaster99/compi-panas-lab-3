


class CodeGenerator:

    def __init__(self, quadruples):
        self.quadruples = quadruples
        self.current_register = 0
        self.generated_code = ""


    def generate_code(self, filename='output.asm'):
        for quadruple in self.quadruples:
            print('checking', quadruple, quadruple.opp)
            match quadruple.opp:
                case '+':
                    print('adding add')
                    self.generate_arithmetic(quadruple, 'add')
                case '-':
                    print('adding sub')
                    self.generate_arithmetic(quadruple, 'sub')
                case '*':
                    self.generate_arithmetic(quadruple, 'mult')
                case '/':
                    self.generate_arithmetic(quadruple, 'div')
                case 'label':
                    self.generate_label(quadruple)
                case 'CALL':
                    self.generate_goto(quadruple)
                case _:
                    print('Unhandled operation')


        return self.get_final_code(self.generated_code)



    def get_final_code(self, code):
        return f"""
.data
.text
.globl main@Main

{code}

# HALT
li $v0, 10 
syscall
        """



    def generate_label(self, quadruple):
        code = f"""
{quadruple.arg1}:
"""
        self.generated_code += code

    def generate_goto(self, quadruple):
        code = f"""
    J {quadruple.arg1}
"""
        self.generated_code += code

    def generate_arithmetic(self, quadruple, operation):


        code = ''
        # Load first instruction
        if '_' in quadruple.arg1:
            code += f"""
    li $s3, {self.get_memory_position(quadruple.arg1)}
    lw $s0, 0($s3)"""
        else:
            code += f"""
    li $s0, {quadruple.arg1}"""

        # Load second instruction
        if '_' in quadruple.arg2:
            code += f"""
    li $s3, {self.get_memory_position(quadruple.arg2)}
    lw $s1, 0($s3)"""

        else:
            code += f"""
    li $s1, {quadruple.arg2}"""

        code += f"""
    {operation} $v0, $s0, $s1
"""
        self.generated_code += code


    def get_memory_position(self, argument):
        return argument[argument.find('[')+1:argument.rfind(']')]