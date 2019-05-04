# Context-Free Grammar Generator

This small script takes in a json with a context-free grammar rules and returns a random string generated from that grammar

### A Short Preamble about Grammars

Formally, a grammar is a tuple (T,N,S,P) where:

- T is an alphabet of (T)erminal characters
- N is an alphabet of (N)on-terminal characters
- S is called "Axiom" and is the starting point of the string generation. S belongs to N
- P is a set of rules called (P)roductions.
- A production has the form A->B, where A is referred to as "left-hand side" and B as "right-hand side" of the production

In a context free grammar, A is composed of a single non-terminal character and B can be any string composed of Terminal and Non-Terminal characters
A grammar generates strings by replacing non-terminal characters that match the left-hand side of a production with the relative right-hand side.
When the string is entirely composed of terminal characters, the generation stops and the resulting string is one of the many possible strings contained in
the language that the grammar can produce.

### BNF File Format

The BNF file is a text file which contains all the productions of the grammar.

Comments start with "#": these lines, along with empty lines, will be ignored
The format is typical of the Backus-Naur form. For example:

Left-hand side::=First production|Second <any non terminal character> production|Third production

The number of production is variable and can be indefinitely large. Each production must be separated by a "|" character (This can be changed in the bnf_to_json.py file)

Note that the left-hand side does not have quotes nor brackets around.
Non terminal pieces must be sorrounded by angled brackets.

### How to Use

**Step 1**: Write the bnf file with the specifications of the precedent section. Take a look at the "bnf_example.txt" file if you want an example
**Step 2**: To convert the BNF file to json give the following arguments in the command, following the script name:

OUTPUT_FILE, NAME_OF_GRAMMAR (Optional), VERSION (Optional), AUTHOR (Optional)

e.g. "python3 bnf_to_json.py output.txt "Test Grammar" "v2.3" "John Doe"

**Step 3**: Open the "stringGenerator.py" file with a text editor and change the input file in the constants
**Step 4**: Call the stringGenerator.py program and it will output a string from the grammar

### Additional Things

- Change DEBUG_MODE to True to check the average length of the string. It will generate 1000 strings of the grammar and calculate the average size. This will also print additional informations about the rules.
