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
        """Processes each element, handling EBNF suffixes."""
        element_code = self.visit(ctx.labeledElement() or ctx.atom() or ctx.ebnf() or "")
        if ctx.ebnfSuffix():
            suffix = ctx.ebnfSuffix().getText()
            if suffix == '*':
                return f"zero_or_more({element_code})"
            elif suffix == '+':
                return f"one_or_more({element_code})"
            elif suffix == '?':
                return  f"select(['', {element_code}])"
        return element_code

    def visitAtom(self, ctx:ANTLRv4Parser.AtomContext):
        """Handles atomic elements in the grammar."""
        if ctx.terminalDef():
            return self.visit(ctx.terminalDef())
        elif ctx.ruleref():
            return self.visit(ctx.ruleref())
        elif ctx.notSet():
            return self.visit(ctx.notSet())
        elif ctx.DOT():
            return "'.'"
        return "''"

    # Terminal and reference handling
    def visitTerminal(self, ctx):
        """Processes terminal definitions, generating regex if suitable."""
        text = ctx.getText()
        if text.isidentifier():
            return f"{text}()"
        elif text.startswith("'") and text.endswith("'"):
            return text  # Literal string
        elif '[' in text or '-' in text:  # Character range or set
            return f"regex(r'{text}')"
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
        return self.visit(ctx.lexerAltList())

    def visitLexerAltList(self, ctx:ANTLRv4Parser.LexerAltListContext):
        """Manages alternatives within a lexer rule."""
        alts = [self.visit(alt) for alt in ctx.lexerAlt()]
        return alts[0] if len(alts) == 1 else f"select([\n        {', '.join(alts)}\n    ])"

    def visitLexerAlt(self, ctx:ANTLRv4Parser.LexerAltContext):
        """Processes each lexer alternative."""
        #print( self.visit(ctx.lexerElements()) or "''")
        return self.visit(ctx.lexerElements()) or "''"


    def visitLexerElements(self, ctx:ANTLRv4Parser.LexerElementsContext):
        """Combines lexer elements into a sequence."""
        elements = [self.visit(e) for e in ctx.lexerElement()]
        print( ' + '.join(elements))
        return ' + '.join(elements)

    def visitLexerElement(self, ctx: ANTLRv4Parser.LexerElementContext):
        """Handles elements within lexer rules, applying EBNF suffixes as needed."""
        element_code = self.visit(ctx.lexerAtom() or ctx.lexerBlock() or "")
        
        # Debugging to track element code before suffix application
        print(f"Element before suffix: {element_code}")

        # If there's a suffix, apply it directly to the element or sequence
        if ctx.ebnfSuffix():
            suffix = ctx.ebnfSuffix().getText()
            element_code = {
                '*': f"zero_or_more({element_code})",
                '+': f"one_or_more({element_code})",
                '?': f"select(['', {element_code}])"
            }.get(suffix, element_code)
    
        # Debugging to track element code after suffix application
        print(f"Element after suffix: {element_code}")
        return element_code


    def visitLexerAtom(self, ctx):
        """Processes atomic parts of a lexer rule, applying regex if suitable."""
        if ctx.characterRange():
            result = self.visitCharacterRange(ctx.characterRange())
        elif ctx.terminalDef():
            result = self.visitTerminal(ctx.terminalDef())
        elif ctx.notSet():
            not_set_text = ctx.notSet().getText()
            if not_set_text.startswith('~[') and not_set_text.endswith(']'):
                result = f"regex(r'[^{not_set_text[2:-1]}]')"
            else:
                result = self.visit(ctx.notSet())
        elif ctx.DOT():
            result = "'.'"
        elif ctx.getText().startswith('[') and ctx.getText().endswith(']'):
            result = f"regex(r'{ctx.getText()}')"  # Regex for character set
        else:
            result = "''"

        # Debugging to track lexer atom result
        print(f"LexerAtom result: {result}")
        return result

    

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
            # Wrap the entire block content in parentheses to preserve grouping
            block_content = self.visit(ctx.altList())
            # Only add parentheses if there's more than one alternative
            if ',' in block_content:
                return f"({block_content})"
            return block_content
        return "''"

    def visitAltList(self, ctx: ANTLRv4Parser.AltListContext):
        """Manages a list of alternatives, using select if there are multiple options."""
        alts = [self.visit(alt) for alt in ctx.alternative()]
        
        # Debugging to track the list of alternatives
        print(f"Alternatives: {alts}")
        
        # Wrap alternatives in select only if more than one alternative exists
        result = alts[0] if len(alts) == 1 else f"select([{', '.join(alts)}])"
        print(f"AltList result: {result}")
        return result
