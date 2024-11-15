# ANTLR-to-Guidance Translator

A simple tool to convert ANTLR grammar files (.g4) into Python Guidance functions for controlled language model decoding.

## Features
  Translates ANTLR grammar rules into Python functions
  Supports non-terminal and terminal grammar elements

## Installation
Clone the repo

```bash
git clone https://github.com/alexanderchen750/antlr-to-guidance.git
cd antlr-to-guidance
```
Install the the runtime

`pip install antlr4-python3-runtime`


## Usage
Add .g4 file to antlr-to-guidance folder

Generate the guidance python functions

`python3 gen_antlr_to_guidance.py path/to/grammar.g4`

This should generate grammar-to-guidance.py folder

Once generate, make sure to do the following:
In the first function in the generated file, which is start rule, remove + EOF()

To generate guidance code following a grammar, use the start rule function.

ex.
```bash
lm = model_name + prompt
lm += json()
```

  
