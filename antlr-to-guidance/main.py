# main.py

from antlr4 import *
from ANTLRv4Lexer import ANTLRv4Lexer
from ANTLRv4Parser import ANTLRv4Parser
from GuidanceVisitorV5 import GuidanceVisitor

def parse_file(file_path):
    input_stream = FileStream(file_path)
    lexer = ANTLRv4Lexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = ANTLRv4Parser(token_stream)
    tree = parser.grammarSpec()
    return tree

if __name__ == "__main__":
    file_path = "JSON.g4"  # Replace with your actual .g4 file
    parse_tree = parse_file(file_path)
    visitor = GuidanceVisitor()
    visitor.visit(parse_tree)
    generated_code = visitor.generate_code()
    print(generated_code)
    
