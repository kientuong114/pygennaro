import sys
import re
import json

SCRIPT_NAME, BNF_FILE, OUTPUT_FILE, RULE_NAME, VERSION, AUTHOR = sys.argv 

SEPARATOR_CHAR = "|"

#Initializes the resulting json dict
result = {
            "name": RULE_NAME,
            "version": VERSION,
            "author": AUTHOR,
            "rules":{}
        }

#Reads all lines from input and splits between the left-hand side and the right-hand side
bnf_content = [line.split("::=") for line in list(filter(lambda x: x[0]!="#", list(filter(lambda x: len(x)!=0, [line.strip('\n') for line in open(BNF_FILE)]))))]

print(bnf_content)

#Splits all the lines with the separator
for production in bnf_content:
    print(production)
    production[1] = production[1].split(SEPARATOR_CHAR)

#Initializes the rules dict
production = {}

def getType(prod):
    #If there are any non-terminal characters returns nonfinal, returns final otherwise
    if prod.find("<")!=-1:
        return "nonfinal"
    else:
        return "final"

def formatNonTerminal(productionArr):
    #Splits each right-hand side into the terminal and non terminal characters and creates an array
    #For instance: 'a<S>b' becomes ["a", {"non_term": "S"}, "b"]
    lastDelimiter = 0
    production = []
    while productionArr.find("<", lastDelimiter)!=-1:
        if lastDelimiter != productionArr.find("<", lastDelimiter):
            #Appends from the last delimiter up the position where it finds "<", if it's not the empty string
            production.append(productionArr[lastDelimiter:productionArr.find("<", lastDelimiter)])
        #Appends the part between the angled brackets
        production.append({"non_term": re.sub("<|>", "", productionArr[productionArr.find("<",lastDelimiter):productionArr.find(">",lastDelimiter)+1])})
        lastDelimiter = productionArr.find(">", lastDelimiter)+1
    if lastDelimiter != len(productionArr):
        #After everything is finished, appends the last part of the string if it's not the empty string (i.e. the line doesn't end with ">")
        production.append(productionArr[lastDelimiter:])
    return production

def generateRules():
    for line in bnf_content:
        listOfProductions = []
        for rightProd in line[1]:
            listOfProductions.append({"production": formatNonTerminal(rightProd.replace("\"", "")), "type": getType(rightProd)})
        production[line[0]] = listOfProductions
    result['rules'] = production

def printJson():
    with open(OUTPUT_FILE, 'w') as output_file:
        json.dump(result, output_file, indent=8)

if __name__ == "__main__":
    generateRules()
    printJson()
