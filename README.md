PyGennaro
==========

BNF parsing, formal grammar conversion and string generation utilities

------------------------------------------------------------------------

Do you want to automagically write tweets? Are you also bad at machine learning and do not want to spend hours training a model?

Look no further, for **PyGennaro** is here! PyGennaro is a grammar parser, which constructs an internal model of the grammar and can use that to generate random strings which belong to that grammar.

Using it is as easy as creating a file:

```
# rules.bnf

S::=Easy as <S1>!
S1::=pie|spy|cry|lie|fly
```

and then running the command:

```
$ pygennaro rules.bnf
> Easy as pie!
$ pygennaro rules.bnf
> Easy as lie!
$ pygennaro rules.bnf
> Easy as spy!
```

PyGennaro runs standalone and does not require any external library.

Table of Contents
-----------------
1. [Installation](#installation)
2. [Usage](#usage)
3. [About Formal Grammars](#about-formal-grammars)
4. [BNF File Format](#bnf-file-format)
5. [BNF Metacharacters](#bnf-metacharacters)

Installation
------------

Currently the PyGennaro console command can be installed with pip:

```
$ pip install pygennaro
```

Or, alternatively, from the wheels file:

```
$ pip install pygennaro-0.1.0-py3-none-any.whl
```


Usage
-----

```
usage: pygennaro [-h] [-l L] [--json] [-i N] [--attempts N] input_file

Context free grammar generator which takes a BNF grammar and outputs a string from that grammar

positional arguments:
  input_file        Input file in BNF

optional arguments:
  -h, --help        show this help message and exit
  -l L, --length L  Maximum length allowed for the generated string
  --json            The program will output the BNF in json form instead of outputting a string
  -i N, --indent N  JSON indentation spaces. Only makes sense with the --json option
  --attempts N      Maximum attempts for generating the string. Will throw an exception if all attempts are unsuccessful
```

About Formal Grammars
---------------------

Formally, a grammar is a tuple (T,N,S,P) where:

- T is an alphabet of (T)erminal characters
- N is an alphabet of (N)on-terminal characters
- S is called "Axiom" and is the starting point of the string generation. S belongs to N
- P is a set of rules called (P)roductions.
- A production has the form A->B, where A is referred to as "left-hand side" and B as "right-hand side" of the production

In a context free grammar, A is composed of a single non-terminal character and B can be any string composed of Terminal and Non-Terminal characters
A grammar generates strings by replacing non-terminal characters that match the left-hand side of a production with the relative right-hand side.

For instance with the following rules:

```
(1) S -> a
(2) S -> A
(3) S -> B
(4) A -> cS
(5) B -> d
(6) B -> dB
```

(The first 3 rules are equivalent to `S -> a | A | B`)

Then we could, for example have the following sequence of derivations:

```
S -> A -> cS -> cA -> ccS -> ccB -> ccdB -> ccddB -> ccddd
```

Where, respectively, the rules 2, 4, 2, 4, 3, 6, 6, 5 were used. Note that rules do not necessarily have to be used (for example rule 1).

When the string is entirely composed of terminal characters, the generation stops and the resulting string is one of the many possible strings contained that the grammar can produce. This process is non-deterministic. The set of all possible strings that the grammar can produce is its language.

BNF File Format
---------------

The BNF file is a text file which contains all the productions of the grammar.

Comments start with "#": these lines, along with empty lines, will be ignored
The format is typical of the Backus-Naur form. For example:

```
Var::=First thing!|Second <Var> thing!|<Other>
Other::=Stuff!
```

Multiple productions which share the same LHS can be merged into a single line, separated by pipe character `|`

Non terminal pieces must be sorrounded by angled brackets. Also notice that spaces are relevant and will be included in the productions.

BNF Metacharacters
------------------

To facilitate the writing of the set of rules, there is the possibility of using metacharacters inside non-terminals in the BNF.
These metacharacters describe how the terminals should appear, after substitution of the non-terminal.

The currently implemented metacharacters are as follows:

| Character | Effect |
| --------- | ------ |
| `^`       | Capitalize the first letter of the string ("hello" -> "Hello") |
| `!`       | Render the string in uppercase ("hello" -> "HELLO") |

For instance, suppose we had the following set of rules:

```
S::=Fairly oddparents! <thing>|Fairly oddparents! <!thing> (but screaming)
thing::=obtuse|rubber goose|green moose|guava juice
```

This allows for us to use all of the possible substitutions in `thing` both in lowercase and in uppercase, without having to rewrite them twice.

Thus, both of these are valid strings generated by the grammar:

```
Fairly oddparents! rubber goose

Fairly oddparents! RUBBER GOOSE (but screaming)
```

Why PyGennaro?
--------------

Because it **gen**erates strings and because "Gennaro" is an Italian name, so I thought it would be funny.
