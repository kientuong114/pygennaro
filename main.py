############################################
#                                          #
#   Context-Free Grammar Generator         #
#                                          #
#   by Truong Kien Tuong (@kientuong114)   #
#   April 2019                             #
#                                          #
############################################

import json
import random
from functools import reduce
from math import exp

#Set here the file from which the grammar productions are loaded
RULES_FILE = "customrules/fulvio2.json"

#Some constants
MAX_LENGTH = 3000
MIN_LENGTH = 10
MAX_RECURSION_DEPTH = 30

#The character used to separate the various terminal characters after the string is finally generated. Can be the empty string "".
SPACING_CHAR = ""

#Currently unused
RSEED = 274691698742

#Loads the file
data = json.load(open(RULES_FILE))

def getProductions(non_term, isFinal="NULL"):
    #Looks at all the productions which have a matching left-hand side and returns the right-hand side of a randomly chosen production
    nonTermExists = False
    for key, rules in data['rules'].items():
        if non_term == key:
            for rule in rules:
                if rule['type'] == "non_final":
                    nonTermExists = True
                    break
            break
    for key, rules in data['rules'].items():
        if non_term == key:
                select = random.choice(rules)
                if isFinal == "NULL" or nonTermExists == False:
                    #print("Selected: ", select)
                    return select
                while select['type'] != isFinal:
                    select = random.choice(rules)
                #print("Selected: ", select)
                return select
    raise Exception('Left hand side not found. No such element as \"'+non_term+'\"')

def stringGenerate(stringArray):
    #Collapses the array into a string
    if len(stringArray)==0:
        return ""
    return reduce((lambda x,y: x+SPACING_CHAR+y), stringArray)

def getStringLength(stringArray):
    #Returns a preliminary length for the string, assessing how close we are to reaching the MAX_LENGTH limit
    length = 0
    for item in stringArray:
        if type(item)!=dict:
            length += len(item)
    return length

def stringValidate(stringArray):
    #String is invalid if either it is not entirely composed of terminal symbols or it doesn't meet the size requirements
    #Returns string if valid, and False otherwise
    for elem in stringArray:
        if type(elem) == dict:
            return False
    string = stringGenerate(stringArray)
    if len(string) < MIN_LENGTH or len(string) > MAX_LENGTH:
        return False
    return string

def generate():
    #Generates a string by using the grammar rules, starting from the single non-terminal "S" axiom
    #Each iterations substitutes a non-terminal with the right-hand side of a production
    #At the start the probability of getting another non-terminal production is 1 and scales down following:
    #probability = 1 - (current_length/max_length)
    stringGen = [{"non_term": "S"}]
    current_length = 0
    while stringValidate(stringGen) == False:
        stringGen = [{"non_term": "S"}]
        for depth in range(MAX_RECURSION_DEPTH): #Supposedly useless, might delete later
            if len(stringGen) == 0:
                return ""
            index = 0
            while index < len(stringGen):
                if type(stringGen[index])==dict:
                    number = random.random()
                    if number < exp(-1*float(current_length)/(float(MAX_LENGTH))):
                        #Requests a non-terminal production
                        #print(stringGen)
                        stringGen[index:index] = getProductions(stringGen.pop(index)['non_term'], "nonfinal")['production']
                    else:
                        #Requests a terminal production
                        #print(stringGen)
                        stringGen[index:index] = getProductions(stringGen.pop(index)['non_term'], "final")['production']
                    current_length = getStringLength(stringGen)
                index += 1
    return stringValidate(stringGen)

def debugGenerate():
    #Checks the average length of the generated strings
    tot = 0
    currmax = 0
    for i in range(10000):
        result = str(generate())
        currmax = max(currmax, len(result))
        print(result)
        tot += len(result)
    print("Average length: ", float(tot)/10000)
    print("Max length: ", currmax)

def printInfo():
    #Preliminary informations
    print("Informations on Opened File")
    print("File Name:",data['name'])
    print("Version:",data['version'])
    print("Author:",data['author'])
    print("Rules:")
    for key, rules in data['rules'].items():
        print(key, "->")
        for production in rules:
            print(production['production'])

#printInfo()
#print(generate())
debugGenerate()
