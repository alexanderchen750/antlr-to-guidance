#!/bin/bash
G4_FILE=$1
INPUT_FILE=$2
OUTPUT_DIR="./antlr_output"

# Generate Lexer and Parser
java -jar antlr-4.13.2-complete.jar -Dlanguage=Python3 -o $OUTPUT_DIR -no-listener -visitor $G4_FILE

# Run Validation
python validate.py $INPUT_FILE $G4_FILE
