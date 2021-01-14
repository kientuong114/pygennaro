import argparse
import re
import sys
import json
import random
import logging

from pygennaro.grammar import CFGToken, Rule, Grammar, TokenType



def unescape(token: str):
    # Right now the regex splitting method does not allow for the string '\<' or '\>' to appear literally in a production
    # This is due to the fact that we'd need to check if the escaping backslash has been escaped itself etc...
    # Perhaps this would be easier if we had a custom parser instead of relying on regex splitting
    pass


def validate_BNF(rules: list[str]):
    errors = []
    for line_n, rule in enumerate(rules):
        m = re.search(r'<>', rule)
        if m:
            errors.append(
                f'Rules contain empty non terminal token (line {line_n+1}, '
                f'col {m.start()})'
            )
    return errors


def parse_BNF(rules: list[str], to_json: bool):
    rules_dict = {}
    for rule in rules:
        if rule.startswith('#') or rule.isspace():
            continue
        lhs, rhs = rule.strip('\n').split('::=')
        rhs_list = rhs.split('|')
        productions = []

        for el in rhs_list:
            # Searches for tokens like <something> except when angular brackets are escaped
            str_tokens = list(filter(lambda x: x != '', re.split(r'((?<!\\)<.+?(?<!\\)>)', el)))

            # re.split creates empty strings when the separator is at the edges of the string
            # While eliminating them is not needed, it leads to a cleaner json.

            if to_json:
                productions.append(list(map(lambda x: CFGToken.to_token(x).to_json(), str_tokens)))
            else:
                r = Rule(lhs, list(map(CFGToken.to_token, str_tokens)))
                productions.append(r)

        if lhs in rules_dict:
            rules_dict[lhs] += productions
        else:
            rules_dict[lhs] = productions
    return rules_dict


def token_terminal_choice(curr_len: int):
    bound = (-curr_len/3 + 100) / (0.012 * curr_len + 1)
    r = random.random() * 100
    if r > bound:
        return TokenType.TERMINAL
    else:
        return TokenType.NON_TERMINAL


def generate_string(g: Grammar, max_len=300, max_attempts=100):
    for _ in range(max_attempts):
        string = [CFGToken('S', TokenType.NON_TERMINAL)]
        while True:
            non_terms = [(i, token) for i, token in enumerate(string) if token.type == TokenType.NON_TERMINAL]
            if not len(non_terms):
                break
            curr_len = sum(len(tok.str_token) for tok in string if tok.type == TokenType.NON_TERMINAL)
            idx, chosen_token = random.choice(non_terms)

            term_list = [prod for prod in g[chosen_token.str_token] if prod.terminating]
            non_term_list = [prod for prod in g[chosen_token.str_token] if not prod.terminating]
            if len(term_list) == 0: #We expect at least one of them not to be empty
                prod_list = non_term_list
            elif len(non_term_list) == 0:
                prod_list = term_list
            else:
                chosen_type = token_terminal_choice(curr_len)
                if chosen_type == TokenType.TERMINAL:
                    prod_list = term_list
                else:
                    prod_list = non_term_list

            chosen_sub = random.choice(prod_list).apply_flags(chosen_token.flags)
            string = string[:idx] + chosen_sub.rhs + string[idx+1:]
        result = ''.join(tok.str_token for tok in string)
        if len(result) > max_len:
            continue
        else:
            return result
    else:
        raise Exception(f"Could not create a valid string within {max_attempts} attempts")
