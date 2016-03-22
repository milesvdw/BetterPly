import ply.lex as plylex
# region LL1
def get_tokens(lexer):
    tokens = []
    tok = lexer.token()
    while tok:
        tokens.append(tok)
        tok = lexer.token()
    tokens.reverse()
    return tokens

def compute_first_sets(rules):
    nonterms = [rule.nonterminal for rule in rules]
    first = {}
    has_conflict = False
    for rule in rules:
        first[rule.nonterminal] = set()
        for production in rule.productions:
            setattr(production, "first", set())
            if (len(production.symbols) > 0) and production.symbols[0] not in nonterms:
                production.first.add(production.symbols[0])
                first[rule.nonterminal] = first[rule.nonterminal].union(production.first)

    changed = True
    while changed:
        changed = False
        for rule in rules:
            for production in rule.productions:
                if (len(production.symbols) > 0) and production.symbols[0] in nonterms:
                    tmp = production.first.union(first[production.symbols[0]])
                    if tmp != first[rule.nonterminal]:
                        changed = True
                    production.first = tmp
                    first[rule.nonterminal] = first[rule.nonterminal].union(tmp)

            for production in rule.productions:
                for p2 in rule.productions:
                    if production != p2:
                        for symbol in production.symbols:
                            if symbol in p2.symbols:
                                has_conflict = True
    return first, has_conflict

def has_left_recursion(rules):
    nonterms = [rule.nonterminal for rule in rules]
    reachable_nodes = {}
    for rule in rules:
        reachable_nodes[rule.nonterminal] = set()
        for production in rule.productions:
            if (len(production.symbols) > 0) and production.symbols[0] in nonterms:
                reachable_nodes[rule.nonterminal].add(production.symbols[0])

    changed = True
    while changed:
        changed = False
        for rule in rules:
            for nonterm in reachable_nodes[rule.nonterminal]:
                tmp = reachable_nodes[rule.nonterminal].union(reachable_nodes[nonterm])
                changed = tmp != reachable_nodes[rule.nonterminal]
                reachable_nodes[rule.nonterminal] = tmp
                if rule.nonterminal in reachable_nodes[rule.nonterminal]:
                    return True

    return False

def compute_follow_sets(rules, first_sets):
    follow_set = {}
    nonterms = [rule.nonterminal for rule in rules]
    has_first_follow_conflict = False

    for rule in rules:
        follow_set[rule.nonterminal] = set()

    for rule in rules:
        for production in rule.productions:
            for i in range(len(production.symbols)-1):
                if production.symbols[i] in nonterms:
                    if production.symbols[i+1] in nonterms:
                        follow_set[production.symbols[i]] = follow_set[production.symbols[i]].union(follow_set[production.symbols[i+1]])
                    else:
                        follow_set[production.symbols[i]].add(production.symbols[i+1])

    for rule in rules:
        production_symbols = [production.symbols for production in rule.productions]
        if [] in production_symbols:
            if len(follow_set[rule.nonterminal].intersection(first_sets[rule.nonterminal])) != 0:
                has_first_follow_conflict = True

    return follow_set, has_first_follow_conflict

def find_rule(nonterm, rules):
    for rule in rules:
        if rule.nonterminal == nonterm:
            return rule

def choose_production(token, rule):
    for production in rule.productions:
        if token.type in production.first:
            return production

def parse(grammar, stack, tokens):
    if len(stack) == 0:
        assert len(tokens) == 0
    if len(tokens) == 0:
        return ["$"]
    tok = tokens[len(tokens)-1]
    if stack[len(stack)-1] in grammar.nonterms:
        left = stack[len(stack)-1]
        production = choose_production(tok, find_rule(stack.pop(), grammar.rules))
        reversed_symbols = [symbol for symbol in production.symbols]
        reversed_symbols.reverse()
        for item in reversed_symbols:
            stack.append(item)
        ret = [left]
        for item in production.symbols:
            ret.append(parse(grammar, [item], tokens))
        return ret
    else:
        assert tok.type == stack.pop()
        tok = tokens.pop()
        return tok

def parse_ll1(grammar, lexer, input_string):
    lexer.input(input_string)
    stack = ["module"]
    tokens = get_tokens(lexer)
    tree = parse(grammar=grammar, stack=stack, tokens=tokens)
    return tree

def print_ll1(tree):
    lines = []
    indent = 0
    gen_lines(tree, lines, indent)

    # find longest node to be printed
    longest = len((reduce(lambda x,y: y if len(x[0]) < len(y[0]) else x, lines))[0])

    # make the divider between columns (indent levels) 1 more than the longest node
    divider = "|" + "".join(["-"] * (longest + 1))

    print("\nLL1 Parse Tree:\n\n");
    # print tree kind of like the 'tree' tool on linux
    print("\n\n".join(["".join([divider for i in range(l[1])]) + " " + str(l[0]) for l in lines]))
    print("\nEnd Parse Tree\n")

def gen_lines(tree, lines, indent):
    for i, node in enumerate(tree):
        if i == 0:
            lines.append([node, indent])
        else:
            if isinstance(node, plylex.LexToken):
                lines.append([node.type + " = '" + str(node.value) + "'", indent + 1])
            elif isinstance(node, list):
                gen_lines(tree=node, lines=lines, indent=indent + 1)
            else:
                lines.append([node, indent + 1])

# endregion

