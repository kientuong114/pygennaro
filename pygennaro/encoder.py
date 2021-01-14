import json

from pygennaro.rules import Rule, CFGToken


class RuleEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Rule):
            return [token.to_json() for token in o.rhs]
        else:
            return json.JSONEncoder.default(self, o)

class GrammarRulesEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        elif isinstance(o, Rule):
            return [token.to_json() for token in o.rhs]
        else:
            return json.JSONEncoder.default(self, o)


def serialize_rules(rules: dict[str, list[Rule]], indent):
    return json.dumps(rules, cls=GrammarRulesEncoder, indent=indent)

