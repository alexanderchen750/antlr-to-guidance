# GuidanceVisitor.py
#NOTES:
#- Need to resolve negatation in visit atoms for parser rules
#- need to fix lexer hanlding when calling other lexers, maybe visitLexerAtoms


from antlr4 import *
from ANTLRv4Parser import ANTLRv4Parser
from ANTLRv4Lexer import ANTLRv4Lexer
from ANTLRv4ParserVisitor import ANTLRv4ParserVisitor

class GuidanceVisitor(ANTLRv4ParserVisitor):
    def __init__(self):
        self.code = []
        self.token_map = {}  # Placeholder for mapping TOKEN_REF to their definitions

    def generate_code(self):
        """Consolidates the generated code into a complete script."""
        return '\n\n'.join(self.code)

    #ctx objects are the nodes of the parse tree
    # Root grammar specification handler
    def visitGrammarSpec(self, ctx:ANTLRv4Parser.GrammarSpecContext):
        """Processes the entire grammar specification."""
        if ctx.rules():
            self.visit(ctx.rules())
        return None

    def visitRules(self, ctx:ANTLRv4Parser.RulesContext):
        """Processes all rules in the grammar file."""
        for ruleSpec in ctx.ruleSpec():
            self.visit(ruleSpec)
        return None

    def visitRuleSpec(self, ctx:ANTLRv4Parser.RuleSpecContext):
        """Distinguishes between parser and lexer rules."""
        if ctx.parserRuleSpec():
            self.visit(ctx.parserRuleSpec())
        elif ctx.lexerRuleSpec():
            self.visit(ctx.lexerRuleSpec())
        return None

    # Parser rule handling
    def visitParserRuleSpec(self, ctx:ANTLRv4Parser.ParserRuleSpecContext):
        """Generates code for a parser rule."""
        ruleName = ctx.RULE_REF().getText()
        function_header = f"@guidance(stateless=True)\ndef {ruleName}(lm):"
        ruleBody = self.visit(ctx.ruleBlock())
        function_body = f"    return lm + {ruleBody}"
        self.code.extend([function_header, function_body])
        return None

    def visitRuleBlock(self, ctx:ANTLRv4Parser.RuleBlockContext):
        """Handles a block within a parser rule."""
        return self.visit(ctx.ruleAltList())

    def visitRuleAltList(self, ctx:ANTLRv4Parser.RuleAltListContext):
        """Manages alternative expressions for a rule."""
        alts = [self.visit(alt) for alt in ctx.labeledAlt()]
        return alts[0] if len(alts) == 1 else f"select([\n        {', '.join(alts)}\n    ])"

    def visitLabeledAlt(self, ctx:ANTLRv4Parser.LabeledAltContext):
        """Visits a labeled alternative."""
        return self.visit(ctx.alternative())

    def visitAlternative(self, ctx:ANTLRv4Parser.AlternativeContext):
        """Handles individual elements in an alternative."""
        elements = [self.visit(e) for e in ctx.element()]
        return ' + '.join(elements) if elements else "''"

    def visitElement(self, ctx:ANTLRv4Parser.ElementContext):
        """Enhanced element handling with proper suffix application."""
        if ctx.labeledElement():
            element_code = self.visit(ctx.labeledElement())
        elif ctx.atom():
            element_code = self.visit(ctx.atom())
        elif ctx.ebnf():
            element_code = self.visit(ctx.ebnf())
        else:
            return "''"

        if ctx.ebnfSuffix():
            suffix = ctx.ebnfSuffix().getText()
            if suffix == '*':
                return f"zero_or_more({element_code})"
            elif suffix == '+':
                return f"one_or_more({element_code})"
            elif suffix == '?':
                return f"select(['', {element_code}])"
        return element_code

    def visitBlock(self, ctx:ANTLRv4Parser.BlockContext):
        """Processes a block containing alternatives, handling structural parentheses."""
        # Check if this block has an AltList and visit it directly
        if ctx.altList():
            alternatives = self.visit(ctx.altList())
            
            # If multiple alternatives, wrap them in a grouping `select` construct
            if isinstance(alternatives, list) and len(alternatives) > 1:
                return f"select([{', '.join(alternatives)}])"
            else:
                return alternatives if alternatives else "''"
        
        # Return empty string if no alternatives (for empty block)
        return "''"

    

    def visitAtom(self, ctx:ANTLRv4Parser.AtomContext):
        """Handles atomic elements in the grammar."""
        if ctx.terminalDef():
            print(f"Atom is terminal: {ctx.getText()}")
            return self.visit(ctx.terminalDef())
        elif ctx.ruleref():
            print(f"Atom is rule reference: {ctx.getText()}")
            return self.visit(ctx.ruleref())
        elif ctx.notSet():
            print(f"Atom is not set: {ctx.getText()}")
            return self.visit(ctx.notSet())
        elif ctx.DOT():
            print(f"Atom is dot: {ctx.getText()}")
            return "'.'"
        print(f"Atom is unknown: {ctx.getText()}")
        return "''"

    # Terminal and reference handling
    def visitTerminal(self, ctx):
        """Processes terminal definitions, generating regex if suitable."""
       
        text = ctx.getText()
        if text.isidentifier():
            print(f"Terminal is identifier: {text}")
            return f"{text}()"
        elif text.startswith("'") and text.endswith("'"):
            print(f"Terminal is string: {text}")
            return text  # Literal string
        elif '[' in text or '-' in text:  # Character range or set
            print(f"Terminal is range/set: {text}")
            return f"regex(r'{text}')"
        print(f"Terminal is unknown: {text}")
        return f"'{text}'"
    
    """def visitTerminal(self, ctx:ANTLRv4Parser.TerminalContext):
        #Processes terminal definitions.
        if ctx.TOKEN_REF():
            token_ref = ctx.TOKEN_REF().getText()
            return f"{token_ref}()"
        elif ctx.STRING_LITERAL():
            string_literal = ctx.STRING_LITERAL().getText()
            return string_literal  # Includes quotes
        else:
            return "''" """


    def visitRuleref(self, ctx:ANTLRv4Parser.RulerefContext):
        """Handles rule references in the grammar."""
        rule_ref = ctx.RULE_REF().getText()
        return f"{rule_ref}()"


    def visitLexerRuleSpec(self, ctx:ANTLRv4Parser.LexerRuleSpecContext):
        """Generates code for a lexer rule, handling nested lexer calls properly."""
        tokenName = ctx.TOKEN_REF().getText()
        
        # Check for skip commands
        lexerAltList = ctx.lexerRuleBlock().lexerAltList()
        first_alt = lexerAltList.lexerAlt(0) if lexerAltList and lexerAltList.lexerAlt(0) else None
        lexerCommands = first_alt.lexerCommands() if first_alt else None

        if lexerCommands:
            for cmd in lexerCommands.lexerCommand():
                if cmd.getText() == 'skip':
                    return None  # Ignore lexer rules marked to be skipped

        # Function header
        function_header = f"@guidance(stateless=True)\ndef {tokenName}(lm):"
        
        # Visit the lexer rule block and construct the body
        ruleBody = self.visit(ctx.lexerRuleBlock())
        function_body = f"    return lm + {ruleBody}"
        
        # Store the generated function
        self.code.extend([function_header, function_body])
        return None

    """def visitLexerAtom(self, ctx):
        #Processes atomic parts of a lexer rule, applying regex or nested function calls as needed.
        if ctx.characterRange():
            return self.visitCharacterRange(ctx.characterRange())
        elif ctx.terminalDef():
            return self.visitTerminal(ctx.terminalDef())
        elif ctx.notSet():
            return self.visitNotSet(ctx.notSet())
        elif ctx.DOT():
            return "'.'"  # Matches any character
        elif ctx.getText().startswith('[') and ctx.getText().endswith(']'):
            return f"regex(r'{ctx.getText()}')"
        return "''" """




    def visitLexerRuleBlock(self, ctx:ANTLRv4Parser.LexerRuleBlockContext):
        """Handles lexer rule blocks."""
        print(f"LexerRuleBlock text: {ctx.getText()}")
        temp = self.visit(ctx.lexerAltList())
        print("lexer rule block ", temp)
        return temp


    def visitLexerAltList(self, ctx:ANTLRv4Parser.LexerAltListContext):
        """Manages alternatives within a lexer rule."""
        print(f"AltList text: {ctx.getText()}")
        alts = [self.visit(alt) for alt in ctx.lexerAlt()]
        
        # Check if there are alternatives and format them correctly
        formatted_alts = ', '.join(alts)
        print("post alts: " + formatted_alts)  # Print after processing

        # Format as 'select' if there are multiple alternatives, without adding extra ')'
        return alts[0] if len(alts) == 1 else f"select([\n        {formatted_alts}\n    ])"



    def visitLexerAlt(self, ctx:ANTLRv4Parser.LexerAltContext):
        """Processes each lexer alternative."""
        print(f"Alt text: {ctx.getText()}")
        temp = self.visit(ctx.lexerElements())
        print(f"post lexerAlt: {temp}")
        return temp

    def visitLexerElements(self, ctx:ANTLRv4Parser.LexerElementsContext):
        """Combines lexer elements into a sequence."""
        print(f"elements: {ctx.getText()}")
        elements = [self.visit(e) for e in ctx.lexerElement()]
        print("post lexerElement: " + ' + '.join(elements))
        return ' + '.join(elements)

    def visitLexerElement(self, ctx:ANTLRv4Parser.LexerElementContext):
        """Enhanced lexer element handling with proper grouping."""
        
        if ctx.lexerAtom():
            print(f"ele is ATOM: {ctx.getText()}")
            element_code = self.visit(ctx.lexerAtom())
        elif ctx.lexerBlock():
            print(f"ele is BLOCK: {ctx.getText()}")
            element_code = self.visit(ctx.lexerBlock())
        else:
            print(f"ele is NULL: {ctx.getText()}")
            return "''"

        if ctx.ebnfSuffix():
            suffix = ctx.ebnfSuffix().getText()
            if suffix == '*':
                return f"zero_or_more({element_code})"
            elif suffix == '+':
                return f"one_or_more({element_code})"
            elif suffix == '?':
                return f"select(['', {element_code}])"
        print("final element code: " +  element_code)
        return element_code
    
    def visitLexerBlock(self, ctx:ANTLRv4Parser.LexerBlockContext):
        """Processes a lexer block, managing structural parentheses for grouping alternatives."""
        # Access the alternative list within the lexer block
        if ctx.lexerAltList():
            alternatives = self.visit(ctx.lexerAltList())
            
            # Handle multiple alternatives by wrapping them in a select statement for grouping
            if isinstance(alternatives, list) and len(alternatives) > 1:
                return f"select([{', '.join(alternatives)}])"
            else:
                return alternatives if alternatives else "''"
        
        # If there's no lexerAltList (i.e., empty lexer block), return an empty string
        return "''"


    def visitLexerAtom(self, ctx):
        """Enhanced lexer atom handling with proper parentheses support."""
        if ctx.characterRange():
            return self.visitCharacterRange(ctx.characterRange())
        elif ctx.terminalDef():
            print("terminal: " + ctx.getText())
            print("terminal def:", ctx.terminalDef())
            """terminal_text = ctx.terminalDef().getText()
            # Handle escaped characters in terminal definitions
            if terminal_text.startswith("'") and terminal_text.endswith("'"):
                content = terminal_text[1:-1]
                return f"'{content}'"""""
            temp = self.visitTerminal(ctx.terminalDef())
            print(f"post termianlDef : {temp}")
            return temp
        elif ctx.notSet():
            not_set_text = ctx.notSet().getText()
            if not_set_text.startswith('~[') and not_set_text.endswith(']'):
                # Handle negated character sets
                chars = not_set_text[2:-1]
                return f"regex(r'[^{chars}]')"
            return self.visit(ctx.notSet())
        elif ctx.DOT():
            return "'.'"
        elif ctx.getText().startswith('[') and ctx.getText().endswith(']'):
            # Handle character sets
            chars = ctx.getText()[1:-1]
            return f"regex(r'[{chars}]')"
        return "''"

    

    def visitCharacterRange(self, ctx:ANTLRv4Parser.CharacterRangeContext):
        """Generates regex for a character range selection."""
        start_char = ctx.STRING_LITERAL(0).getText()[1:-1]
        end_char = ctx.STRING_LITERAL(1).getText()[1:-1]
        return f"regex(r'[{start_char}-{end_char}]')"

    def visitLexerCharSet(self, node):
        """Handles character sets in lexer rules, converting to regex."""
        text = node.getText().strip('[]')
        return f"regex(r'[{text}]')"

    def visitEbnf(self, ctx:ANTLRv4Parser.EbnfContext):
        """Processes EBNF expressions, applying repetition or optional suffixes."""
        block_code = self.visit(ctx.block())
        suffix = ctx.blockSuffix().ebnfSuffix().getText()
        if suffix == '*':
            return f"zero_or_more({block_code})"
        elif suffix == '+':
            return f"one_or_more({block_code})"
        elif suffix == '?':
            return f"select(['', {block_code}])"
        else:
            return block_code

    def visitBlock(self, ctx:ANTLRv4Parser.BlockContext):
        """Processes a block containing alternatives."""
        if ctx.altList():
            alternatives = self.visit(ctx.altList())
            return alternatives
        return "''"

    def visitAltList(self, ctx:ANTLRv4Parser.AltListContext):
        """Manages a list of alternatives within blocks."""
        alts = [self.visit(alt) for alt in ctx.alternative()]
        # Filter out empty alternatives
        alts = [alt for alt in alts if alt and alt != "''"]
        
        if len(alts) == 0:
            return "''"
        elif len(alts) == 1:
            return alts[0]
        else:
            # Properly format alternatives for select
            return f"select([{', '.join(alts)}])"
