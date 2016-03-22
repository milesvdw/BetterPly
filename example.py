import bly

def lex_int(tok):
    tok.value = int(tok.value)
    return tok

token_patterns = [
    bly.TokenPattern(pattern=r'\+', on_lexed=lambda x: x, name="ADD"),
    bly.TokenPattern(pattern=r'\d+', on_lexed=lex_int, name="INT"),
    bly.TokenPattern(pattern=r' ', on_lexed=None, name="ignore")
]

def parse_module(prod):
    prod[0] = prod[1]

def parse_add(prod):
    if len(prod) == 4:
        prod[0] = ("+", prod[1], prod[3])
    else:
        prod[0] = prod[1]


evil_rules = [
    bly.GrammarRule(nonterminal="module", productions=[
        bly.Production(symbols=["expr"])
    ], on_parsed=parse_module),
    bly.GrammarRule(nonterminal="expr", productions=[
        bly.Production(symbols=["expr", "ADD", "expr"]),
        bly.Production(symbols=["INT"])
    ], on_parsed=parse_add)
]

godly_rules = [
    bly.GrammarRule(nonterminal="module", productions=[
        bly.Production(symbols=["expr"])
    ], on_parsed=parse_module),
    bly.GrammarRule(nonterminal="expr", productions=[
        bly.Production(symbols=["INT", "expr2"])
    ], on_parsed=parse_add),
    bly.GrammarRule(nonterminal="expr2", productions=[
        bly.Production(symbols=["ADD", "expr"]),
        bly.Production(symbols=[])
    ], on_parsed=parse_add)]

if __name__ == "__main__":
    grammar = bly.Grammar(rules=godly_rules, patterns=token_patterns)
    lexer = bly.lex(patterns=token_patterns)
    if grammar.is_LL1:
        print "Parsing input using LL1 grammar..."
        tree = bly.do_LL1(grammar=grammar, lexer=lexer, input_string="2 + 2 + 6")
        bly.print_LL1(tree)
    else:
        print "Parsing input using yacc..."
        tree = bly.yacc(patterns=token_patterns, rules=grammar.rules, input="2 + 2 + 6")

    #print tree
