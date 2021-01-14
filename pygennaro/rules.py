import re
from enum import Enum, Flag, auto

class TokenType(Enum):
    TERMINAL = 0
    NON_TERMINAL = 1


class TokenFlags(Flag):
    NONE = 0
    CAPITALIZE = auto()
    ALL_CAPS = auto()


flag_chars = {
    '^': TokenFlags.CAPITALIZE,
    '!': TokenFlags.ALL_CAPS
}


flag_funcs = {
    TokenFlags.NONE: lambda x: x,
    TokenFlags.CAPITALIZE: lambda x: x.capitalize(),
    TokenFlags.ALL_CAPS: lambda x: x.upper()
}


class CFGToken:
    def __init__(self, str_token: str, type: TokenType, flags: TokenFlags = None):
        self.str_token = str_token
        self.type = type
        self.flags = TokenFlags.NONE
        if self.type == TokenType.NON_TERMINAL:
            #If Terminal we ignore flags, since they're not going to be useful
            for idx, ch in enumerate(str_token):
                if ch in flag_chars:
                    self.flags |= flag_chars[ch]
                else:
                    self.str_token = str_token[idx:]
                    break
        if flags:
            self.flags |= flags


    def __repr__(self):
        return f'<CFGToken: token=\'{self.str_token}\', type={self.type}>'


    def to_json(self):
        return {'token': self.str_token, 'type': self.type.name}


    def apply_flags(self, flags: TokenFlags):
        if self.type == TokenType.TERMINAL:
            res = self.str_token
            for flag in TokenFlags:
                if flag in flags:
                    res = flag_funcs[flag](res)
            return CFGToken(res, self.type)
        else:
            return CFGToken(self.str_token, self.type, self.flags | flags)

    @classmethod
    def to_token(cls, str_token: str):
        m = re.match(r'^<(.+)>$', str_token)
        if m:

            return CFGToken(m.group(1), TokenType.NON_TERMINAL)
        else:
            return CFGToken(str_token, TokenType.TERMINAL)


class Rule:
    def __init__(self, lhs: str, rhs: list[CFGToken]):
        self.lhs = lhs
        self.rhs = rhs
        self.terminating = all(map(lambda x: x.type == TokenType.TERMINAL, self.rhs))

    def __contains__(self, to_find: str):
        if not isinstance(to_find, str):
            raise TypeError('Token must be str')
        for token in self.rhs:
            if token.str_token == to_find:
                return True
        return False


    def __repr__(self):
        return f'<Rule: lhs={self.lhs}, rhs={self.rhs}>'


    def apply_flags(self, flags: TokenFlags):
        return Rule(self.lhs, list(map(lambda x: x.apply_flags(flags), self.rhs)))


    def substitute(self, rule: "Rule"):
        new_rhs = []
        for token in self.rhs:
            if token.str_token == rule.lhs and token.type == TokenType.NON_TERMINAL:
                new_rhs += rule.rhs
            else:
                new_rhs.append(token)
        self.rhs = new_rhs

