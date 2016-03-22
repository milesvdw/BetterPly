import bly

# simply casts the value of the received token to an int
def lex_int(tok):
    tok.value = int(tok.value)
    return tok

# each token pattern consists of a regular expression and a function which will be called when that token is lexed
token_patterns = [
    bly.TokenPattern(pattern=r'\+', on_lexed=lambda x: x, name="ADD"),
    bly.TokenPattern(pattern=r'\d+', on_lexed=lex_int, name="INT"),
    bly.TokenPattern(pattern=r' ', on_lexed=None, name="ignore")
]

# this will be called when a string or substring is parsed into the 'module' nonterminal
def parse_module(prod):
    prod[0] = prod[1]


# this will be called when a string or substring is parsed into the 'expr' nonterminal
def parse_expr(prod):
    if len(prod) == 4:
        prod[0] = ("+", prod[1], prod[3])
    else:
        prod[0] = prod[1]

# A simple grammar that is not LL(1) parseable.
# Each rule consists of a nonterminal (left side) and a list of productins (right side). Rules also have an on_parsed
# function, which is the function to be called when a string or substring parses to this Rule the formal definition is
# available in bly.py, but essentially the on_parsed function should take a list of nodes and return a single tree node.
# for our example grammar, we simple return a tuple representing the node. This tuple is also what the bly.print_ll1
# function expects, but you may chose to represent your tree differently and write your own function for pretty-printing
complex_rules = [
    bly.GrammarRule(nonterminal="module", productions=[
        bly.Production(symbols=["expr"])
    ], on_parsed=parse_module),
    bly.GrammarRule(nonterminal="expr", productions=[
        bly.Production(symbols=["expr", "ADD", "expr"]),
        bly.Production(symbols=["INT"])
    ], on_parsed=parse_expr)
]

# a set of rules that is LL(1) parseable, though the grammar produces the same strings as the one above
# note that for an LL(1) grammar, no on_parsed function need be defined since bly will detect LL(1) and parse the
# grammar using the LL(1) algorithm
simple_rules = [
    bly.GrammarRule(nonterminal="module", productions=[
        bly.Production(symbols=["expr"])
    ], on_parsed=None),
    bly.GrammarRule(nonterminal="expr", productions=[
        bly.Production(symbols=["INT", "expr2"])
    ], on_parsed=None),
    bly.GrammarRule(nonterminal="expr2", productions=[
        bly.Production(symbols=["ADD", "expr"]),
        bly.Production(symbols=[])
    ], on_parsed=None)]

if __name__ == "__main__":
    tree = bly.yacc(patterns=token_patterns, rules=simple_rules, inputstr="2 + 2 + 6")

    bly.print_ll1(tree)
