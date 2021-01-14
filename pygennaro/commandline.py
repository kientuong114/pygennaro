import argparse
import json

from pygennaro.grammar import Grammar
from pygennaro.genstring import generate_string


def parse_args():
    parser = argparse.ArgumentParser(
        description = 'Context free grammar generator which takes a BNF grammar and '
        'outputs a string from that grammar'
    )
    parser.add_argument('input_file', type=str, help='Input file in BNF')
    parser.add_argument('-l', '--length', type=int, default=300, help='Maximum length allowed for the generated string', metavar='L')
    parser.add_argument('--json', action='store_true', help='The program will output the BNF in json form instead of outputting a string')
    parser.add_argument('-i', '--indent', type=int, default=4, help='JSON indentation spaces. Only makes sense with the --json option', metavar='N')
    parser.add_argument('--attempts', type=int, default=100, help='Maximum attempts for generating the string. Will throw an exception if all attempts are unsuccessful', metavar='N')
    args = parser.parse_args()
    return args


def command_line_handler():
    args = parse_args()
    if args.json:
        print(Grammar.from_file(args.input_file).to_json(args.indent))
        return
    else:
        g = Grammar.from_file(args.input_file)
        print(generate_string(g, args.length, max_attempts=args.attempts))
        return
