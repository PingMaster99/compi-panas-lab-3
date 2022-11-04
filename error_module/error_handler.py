from antlr4.error.ErrorListener import ErrorListener

global compiler_errors
compiler_errors = []


class ErrorGenerator:
    def __init__(self, message, line=None, warning=False):
        self.line = line
        self.message = message
        self.initial_message = "ERROR" if not warning else "WARNING"
        self.append()

    def __repr__(self):
        if self.line:
            return f"{self.initial_message}: {self.message} [LINE {self.line}]"
        else:
            return f"{self.initial_message}: {self.message}"

    def append(self):
        compiler_errors.append(self)


class CustomErrorListener(ErrorListener):
    """
    Overrides the antlr4 error listener in order to display error messages in GUI
    """

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        ErrorGenerator(
            message=msg,
            line=line
        )
