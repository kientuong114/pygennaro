import sys
import re
import json

SEPARATOR_CHAR = "|"

#Initializes the rules dict
production = {}
result = {}

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

def generateRules(inputList):
    for line in inputList:
        listOfProductions = []
        for rightProd in line[1]:
            listOfProductions.append({"production": formatNonTerminal(rightProd), "type": getType(rightProd)})
        production[line[0]] = listOfProductions
    result['rules'] = production

def printJson(out_file):
    with open(out_file, 'w') as output_file:
        json.dump(result, output_file, indent=8)

def getType(prod):
    #If there are any non-terminal characters returns nonfinal, returns final otherwise
    if prod.find("<")!=-1:
        return "nonfinal"
    else:
        return "final"

def getArgs():
    if len(sys.argv) == 6:
        SCRIPT_NAME, BNF_FILE, OUTPUT_FILE, RULE_NAME, VERSION, AUTHOR = sys.argv 
    else:
        SCRIPT_NAME, BNF_FILE, OUTPUT_FILE = sys.argv
        RULE_NAME = "Unknown"
        VERSION = "v1.0"
        AUTHOR = "John Doe"
    return BNF_FILE, OUTPUT_FILE, RULE_NAME, VERSION, AUTHOR

def init(inputFile, ruleName, version, author):
    #Initializes the resulting json dict
    result = {
                "name": ruleName,
                "version": version,
                "author": author,
                "rules":{}
            }

    #Reads all lines from input and splits between the left-hand side and the right-hand side
    bnf_content = list([line.split("::=") for line in list(filter(lambda x: x[0]!="#", list(filter(lambda x: len(x)!=0, [line.strip('\n') for line in open(inputFile)]))))])

    #Splits all the lines with the separator
    for production in bnf_content:
        print(production)
        production[1] = production[1].split(SEPARATOR_CHAR)
    
    return bnf_content

if __name__ == "__main__":
    inputFile, outputFile, ruleName, version, author = getArgs()
    inputList = init(inputFile, ruleName, version, author)
    generateRules(inputList)
    printJson(outputFile)
