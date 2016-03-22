import ply.yacc as yuck
from parsing import *
import imp

class Grammar:
    def __init__(self, rules, patterns):
        self.rules = rules
        self.nonterms = [rule.nonterminal for rule in rules]
        self.patterns = patterns
        self.first_sets, self.has_firstfirstconflict = compute_first_sets(rules)

        self.follow_sets, self.has_firstfollowconflict = compute_follow_sets(rules, self.first_sets)
        self.has_leftrecursion = has_left_recursion(rules)

        self.is_ll1 = not self.has_firstfirstconflict \
                      and not self.has_firstfollowconflict \
                      and not self.has_leftrecursion

class TokenPattern:
    def __init__(self, pattern, on_lexed, name):
        """
        :param pattern: A regex pattern as a string.
        :param on_lexed: A function which consumes a LexToken and produces a LexToken.
        :param name: The string name of the token.
        """
        self.pattern = pattern
        self.on_lexed = on_lexed
        self.name = name

class GrammarRule:
    def __init__(self, nonterminal, productions, on_parsed):
        """
        :param nonterminal: A string representing the name of the left hand side of the rule.
        :param productions: A list of Productions.
        """
        self.nonterminal = nonterminal
        self.productions = productions
        self.on_parsed = on_parsed

class Production:
    def __init__(self, symbols):
        """
        :param symbols: A list of names of tokens or nonterminals.
        """
        self.symbols = symbols


def lex(patterns, module=None):
    """
    :param patterns: A list of token patterns
    :param module: A runtime module to be modified and passed to ply
    :return: A lexer.
    """

    if module is None:
        module = imp.new_module("bly_to_ply")
    module.tokens = []
    module.__file__ = "blyfile.py"

    for pattern in patterns:
        put_pattern_into_module(pattern, module)

    return plylex.lex(module=module)

def put_pattern_into_module(pattern, module):
        assert isinstance(pattern, TokenPattern)

        # ensure badlex can see the full list of tokens
        module.tokens.append(pattern.name)

        # check for special cases like t_ignore
        if pattern.on_lexed is None:
            setattr(module, "t_" + pattern.name, pattern.pattern)

        # deal with standard cases
        else:
            pattern.on_lexed.__doc__ = pattern.pattern
            pattern.on_lexed.func_name = "t_" + pattern.name
            setattr(module, pattern.on_lexed.func_name, pattern.on_lexed)

def do_yucc(patterns, rules, inputstr):
    """
    :param patterns: A list of TokenPatterns.
    :param rules: A list of GrammarRules.
    :param inputstr: A string to be parsed
    """
    module = imp.new_module("bly_fake_module")
    lexer = lex(patterns=patterns, module=module)
    for rule in rules:
        assert isinstance(rule, GrammarRule)
        production_strings = [" ".join(production.symbols) for production in rule.productions]
        rule.on_parsed.__doc__ = (
            rule.nonterminal + " : " + " \n | ".join(production_strings)
        )
        setattr(module, "p_" + rule.nonterminal, rule.on_parsed)

    yuck.yacc(module=module)
    return yuck.parse(inputstr, lexer=lexer, debug=False)

def yacc(patterns, rules, inputstr):
    """
    :param patterns: A list of TokenPatterns.
    :param rules: A list of GrammarRules.
    :param inputstr: A string to be parsed
    """
    module = imp.new_module("bly_to_py")
    lexer = lex(patterns, module)

    grammar = Grammar(rules=rules, patterns=patterns)
    if grammar.is_ll1:
        # use the more efficient LL1 parsing algorithm where applicable
        tree = parse_ll1(grammar=grammar, lexer=lexer, input_string=inputstr)
    else:
        # otherwise, pass the grammar off to ply.yacc for parsing
        tree = do_yucc(patterns=patterns, rules=rules, inputstr=inputstr)

    return tree
