import logging
import re
import sys
from collections import deque

from pygennaro.rules import TokenType, CFGToken, Rule
from pygennaro.encoder import serialize_rules


class MalformedGrammarError(Exception):
    pass


class Grammar:
    def __init__(self, rules: dict[str, list[Rule]]):
        self.start_sym = 'S'
        self.rules = rules
        self.T = set()
        self.N = set()
        for rule in self.rules.values():
            for prod in rule:
                for tok in prod.rhs:
                    if tok.type == TokenType.TERMINAL:
                        self.T.add(tok.str_token)
                    elif tok.type == TokenType.NON_TERMINAL:
                        self.N.add(tok.str_token)
        self.N.add(self.start_sym)
        self._verify_grammar()
        self._clean_productions()


    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError('Key must be str')
        return self.rules[key]


    def __repr__(self):
        return f'<Grammar: T={self.T}, N={self.N}, Axiom={self.start_sym}, rules={self.rules}>'

    def _check_symbol_rhs(self, sym: str):
        for rule in self.rules.values():
            for prod in rule:
                if sym in prod:
                    return True
        return False

    def _verify_grammar(self):
        errors = []
        #Check that all RHS non-terminals appear as LHS
        lhs_set = set(self.rules.keys())
        if self.N - lhs_set:
            raise MalformedGrammarError(f'Non terminals {[diff for diff in self.N - lhs_set]} appear as right hand side of a rule, but there is no matching left hand side definition')

    def _get_unique_var(self, prefix='S'):
        while True:
            for i in range(0, 100):
                if prefix + str(i) not in self.N:
                    self.N.add(prefix+str(i))
                    return prefix+str(i)
            prefix += prefix

    def _delete_var(self, var: str):
        if var not in self.N:
            raise ValueError('Variable to be deleted does not exist in grammar')
        new_rules = {}
        for lhs, rhs in self.rules.items():
            if lhs != var:
                new_rules[lhs] = list(filter(lambda x: var not in x, rhs))
        self.rules = new_rules
        self.N.remove(var)


    def _clean_productions(self):
        # Check if there is recursion on the axiom, if there is create a new axiom
        if self._check_symbol_rhs(self.start_sym):
            new_start = self._get_unique_var()
            self.rules[new_start] = [Rule(new_start, [CFGToken(self.start_sym, TokenType.NON_TERMINAL)])]
            self.start_sym = new_start

        # Remove variables which never appear on a RHS
        lhs_set = set(self.rules.keys())
        for diff in lhs_set - self.N:
            if diff != self.start_sym:
                logging.info(f'Eliminating rule with LHS \'{diff}\' as it is not used anywhere')
                del self.rules[diff]

        # Remove non-generating and non-reachable variables
        generating = set()
        for lhs, rhs in self.rules.items():
            for prod in rhs:
                if all(map(lambda x: x.type == TokenType.TERMINAL, prod.rhs)):
                    generating.add(lhs)

        for lhs, rhs in self.rules.items(): #Propagate the fact that these variables generate to their ancestors
            rhs_N = set(tok.str_token for prod in rhs for tok in prod.rhs if tok.type == TokenType.NON_TERMINAL)
            if generating & rhs_N:
                generating.add(lhs)

        if generating != self.N:
            logging.info('Found some non-generating productions, cleaning...')
            to_delete = self.N - generating
            logging.info(f'Removing: {to_delete}')
            for var in to_delete:
                self._delete_var(var)

        reachable = set()
        queue = deque()
        reachable.add(self.start_sym)
        queue.append(self.start_sym)
        while len(queue):
            curr = queue.popleft()
            rhs = self.rules[curr]
            for prod in rhs:
                for token in prod.rhs:
                    if token.type == TokenType.NON_TERMINAL and token.str_token not in reachable:
                        reachable.add(token.str_token)
                        queue.append(token.str_token)

        if reachable != self.N:
            logging.info('Found some non-reachable productions, cleaning...')
            to_delete = self.N - reachable
            logging.info(f'Removing: {to_delete}')
            for var in to_delete:
                self._delete_var(var)

        self.T = set()
        for rule in self.rules.values():
            for prod in rule:
                for tok in prod.rhs:
                    if tok.type == TokenType.TERMINAL:
                        self.T.add(tok.str_token)

    def _delete_recursion(self):
        token_enum = {tok: idx for idx, tok in enumerate(self.N)}
        for nt in self.N:
            # For each non-terminal A_i
            while True:
                new_rules = {k: list(v) for k, v in self.rules}
                for rule in self.rules[nt]:
                    if rule.rhs[0].type == TokenType.NON_TERMINAL and token_enum[alpha] < token_enum[nt]:
                        # For each rule of the form A_i -> A_j . b_i with j < i
                        alpha, beta = rule.rhs[0], rule.rhs[1:]
                        new_rules[nt].remove(rule)
                        for rule_2 in self.rules_list():
                            new_rules[nt].append(Rule(nt, rule_2.rhs + beta))
                if self.rules == new_rules:
                    break
                self.rules = new_rules
            for rule in self.rules[nt]:
                pass #TODO


    def rules_list(self):
        for rule in self.rules.values():
            for prod in rule:
                yield prod

    def to_json(self, indent=4):
        return serialize_rules(self.rules, indent)

    @classmethod
    def from_BNF(cls, rules: list[str]):
        return cls(_rules_from_BNF(rules))

    @classmethod
    def from_file(cls, inputfile: str):
        with open(inputfile) as f:
            rules = f.readlines()
        return Grammar.from_BNF(rules)


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


def _rules_from_BNF(bnf_list: list[str]):

    errors = validate_BNF(bnf_list)

    if errors:
        for e in errors:
            logging.error(e)
        sys.exit(1)

    rules_dict = {}

    for rule in bnf_list:
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

            """
            if to_json:
                productions.append(list(map(lambda x: CFGToken.to_token(x).to_json(), str_tokens)))
            else:
            """
            r = Rule(lhs, list(map(CFGToken.to_token, str_tokens)))
            productions.append(r)

        if lhs in rules_dict:
            rules_dict[lhs] += productions
        else:
            rules_dict[lhs] = productions

    return rules_dict
