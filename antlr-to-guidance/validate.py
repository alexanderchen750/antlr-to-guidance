import sys
import logging
import importlib.util
from antlr4 import FileStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

# Custom Error Listener to log issues
class CustomErrorListener(ErrorListener):
    def __init__(self, name=""):
        super().__init__()
        self.errors = []
        self.name = name  # To distinguish between lexer and parser in logs

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_message = f"{self.name} Error at line {line}, column {column}: {msg}"
        self.errors.append(error_message)

# Function to dynamically load a module
def load_module(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Function to get the root rule dynamically
def get_start_rule(parser_class):
    rule_names = parser_class.ruleNames
    if not rule_names or len(rule_names) == 0:
        raise ValueError("No rules found in the parser.")
    return rule_names[0]

# Function to validate input text against grammar
def validate_input(input_file, grammar_name):
    # Initialize logger
    logging.basicConfig(
        filename="validation.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    try:
        # Load Lexer and Parser modules dynamically
        lexer_module = load_module(f"{grammar_name}Lexer", f"./antlr_output/{grammar_name}Lexer.py")
        parser_module = load_module(f"{grammar_name}Parser", f"./antlr_output/{grammar_name}Parser.py")

        # Dynamically fetch the class names
        lexer_class = getattr(lexer_module, f"{grammar_name}Lexer")
        parser_class = getattr(parser_module, f"{grammar_name}Parser")

        # Load input file
        input_stream = FileStream(input_file)
        
        # Tokenize using the generated lexer
        lexer = lexer_class(input_stream)
        token_stream = CommonTokenStream(lexer)

        # Attach custom error listener to lexer
        lexer_error_listener = CustomErrorListener("Lexer")
        lexer.removeErrorListeners()
        lexer.addErrorListener(lexer_error_listener)
        
        # Parse using the generated parser
        parser = parser_class(token_stream)
        
        # Attach custom error listener to parser
        parser_error_listener = CustomErrorListener("Parser")
        parser.removeErrorListeners()
        parser.addErrorListener(parser_error_listener)

        # Get the starting rule dynamically
        start_rule = get_start_rule(parser_class)

        # Parse the input starting from the dynamically identified rule
        getattr(parser, start_rule)()

        # Combine lexer and parser errors
        all_errors = lexer_error_listener.errors + parser_error_listener.errors

        if all_errors:
            for error in all_errors:
                logging.error(error)
            print("Validation failed. See 'validation.log' for details.")
        else:
            logging.info("Validation successful!")
            print("Validation successful!")
    except Exception as e:
        logging.error(f"Validation process failed with exception: {e}")
        print(f"Validation process failed. Check 'validation.log' for details.")

# Main function to run validation
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate.py path/to/input.json grammarName")
        sys.exit(1)
    
    input_file = sys.argv[1]
    grammar_name = sys.argv[2].split(".")[0]  # Pass grammar name without extension

    validate_input(input_file, grammar_name)
