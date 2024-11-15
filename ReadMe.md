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


## Usage
Set file_path in main.py to select .g4 file to convert
Run

`python main.py path/to/grammar.g4`

Once generate, make sure to do the following:
In the first function in the generated file, which is start rule, remove + EOF()

To generate guidance code following a grammar, use the start rule function.

ex.
```bash
lm = model_name + prompt
lm += json()
```

  
