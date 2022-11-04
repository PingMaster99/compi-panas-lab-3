class TemplateBuilder:
    def __init__(self):
        self.addr = 'DEFAULT_RETURN_ADDRESS'
        self.true = "ERROR"
        self.false = "ERROR"
        self.next = "ERROR"
        self.code = []
        self.quadruples = []

    def add_code(self, code, debug=False):
        for line in code:
            # If adding TemplateBuilder
            if isinstance(line, type(self)):
                for inner_line in line.code:
                    self.code.append(inner_line)
                return
            self.code.append(line)

    def set_memory_address(self, address):
        self.addr = address

    def __repr__(self):
        string = ''
        for line in self.code:
            string += str(line) + "\n"
        return string


class TemporalGenerator:
    def __init__(self):
        self.temporal_value = 0
        self.free_temporal_variables = ["t0"]

    def generate_temporal(self):
        if len(self.free_temporal_variables) > 0:
            return self.free_temporal_variables.pop(0)
        else:
            self.temporal_value += 1
            return f"t{self.temporal_value}"

    def free_temporal_variable(self, temporal):
        self.free_temporal_variables.append(temporal)


class LabelGenerator:
    def __init__(self):
        self.if_identifier = 0          # Differentiate between if declarations
        self.while_identifier = 0       # Differentiate between while declarations
        self.return_identifier = 0      # Differentiate between return declarations

    def generate_if_else_labels(self):
        true_condition_label = f"IF_{self.if_identifier}_TRUE"
        false_condition_label = f"IF_{self.if_identifier}_FALSE"
        self.if_identifier += 1
        return true_condition_label, false_condition_label

    def generate_while_labels(self):
        true_condition_label = f"WHILE_{self.while_identifier}_TRUE"
        false_condition_label = f"WHILE_{self.while_identifier}_FALSE"
        while_start_label = f"WHILE_{self.while_identifier}_START"
        self.while_identifier += 1
        return true_condition_label, false_condition_label, while_start_label

    def generate_return_label(self):
        return_label = f"RETURN_ADDRESS_{self.return_identifier}"
        self.return_identifier += 1
        return return_label

