import sys
import logging
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from antlr4.error.ErrorListener import ErrorListener
from JSONLexer import JSONLexer
from JSONParser import JSONParser

# Custom Error Listener to log issues
class CustomErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"Syntax Error at line {line}, column {column}: {msg}")

# Function to validate input text against grammar
def validate_input(input_file, grammar_file):
    # Initialize logger
    logging.basicConfig(
        filename="validation.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    try:
        # Load input file
        input_stream = FileStream(input_file)
        
        # Tokenize using the generated lexer
        lexer = JSONLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        
        # Parse using the generated parser
        parser = JSONParser(token_stream)
        
        # Attach custom error listener to parser
        error_listener = CustomErrorListener()
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        
        # Parse the input starting from the root rule
        tree = parser.json()  # Replace 'json' with the actual root rule if different

        if error_listener.errors:
            for error in error_listener.errors:
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
        print("Usage: python validate.py path/to/input.json path/to/json.g4")
        sys.exit(1)
    
    input_file = sys.argv[1]
    grammar_file = sys.argv[2]  # Currently not used in validation, as lexer/parser are pre-generated
    
    validate_input(input_file, grammar_file)
