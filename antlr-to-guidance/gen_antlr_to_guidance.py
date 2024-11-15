import argparse
import os
from antlr4 import *
from ANTLRv4Lexer import ANTLRv4Lexer
from ANTLRv4Parser import ANTLRv4Parser
from GuidanceVisitorV5 import GuidanceVisitor

def parse_file(file_path):
    input_stream = FileStream(file_path, encoding='utf-8')
    lexer = ANTLRv4Lexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = ANTLRv4Parser(token_stream)
    tree = parser.grammarSpec()
    return tree

def generate_output_filename(file_path):
    base_name = os.path.basename(file_path)
    file_name = os.path.splitext(base_name)[0]
    output_filename = f"{file_name}-to-guidance.py"
    
    # Check if the file already exists and modify the name if needed
    count = 1
    while os.path.exists(output_filename):
        output_filename = f"{file_name}-to-guidance_{count}.py"
        count += 1

    return output_filename

def main(file_path):
    parse_tree = parse_file(file_path)
    visitor = GuidanceVisitor()
    visitor.visit(parse_tree)
    generated_code = visitor.generate_code()

    output_filename = generate_output_filename(file_path)
    with open(output_filename, "w") as output_file:
        output_file.write(generated_code)

    print(f"Generated code saved to {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a .g4 grammar file and generate code.")
    parser.add_argument(
        "file_path",
        type=str,
        help="Path to the .g4 grammar file to parse."
    )
    args = parser.parse_args()
    main(args.file_path)
