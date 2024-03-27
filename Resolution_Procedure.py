import re
from tqdm import tqdm
 
def eliminate_implication(sentence):
    parts = sentence.split(" ")
    while ('->' in parts):
        impli = parts.index('->')
        n = impli-1
        if (parts[impli-1] == ")"):
            while parts[n] != '(':
                n=n-1
        parts.insert(n,'~')
        parts.insert(impli+1,'|')
        parts.remove('->')
    sentence = ' '.join(parts)
    return sentence

def demorgans_law(sentence):
    parts = sentence.split(" ")
    sym = ['|', '&']
    p_c = re.compile('[a-zA-Z]')
    
    for i in range(len(parts)):
        if parts[i] == '~':
            exist = re.findall(r'E.', parts[i+1])
            uni = re.findall(r'A.', parts[i+1])
            if uni:
                parts[i:i+2] = ["E" + str(uni[0][1]), "~"]
            elif exist:
                parts[i:i+2] = ["A" + str(exist[0][1]), "~"]
            elif parts[i+1] == '(' and p_c.match(parts[i+2]) and (parts[i+3] in sym) and p_c.match(parts[i+4]) and parts[i+5] == ')':
                parts[i:i+6] = ['(', '~', parts[i+2], sym[(sym.index(parts[i+3])+1)%2], '~', parts[i+4], ')']
            elif parts[i+1] == '(' and parts[i+2] == '~' and p_c.match(parts[i+3]) and (parts[i+4] in sym) and p_c.match(parts[i+5]) and parts[i+6] == ')':
                parts[i:i+7] = ['(', '~', '~', parts[i+3], sym[(sym.index(parts[i+4])+1)%2], '~', parts[i+5], ')']
            elif parts[i+1] == '(' and p_c.match(parts[i+2]) and (parts[i+3] in sym) and parts[i+4] == '~' and p_c.match(parts[i+5]) and parts[i+6] == ')':
                parts[i:i+7] = ['(', '~', parts[i+2], sym[(sym.index(parts[i+3])+1)%2], '~', '~', parts[i+5], ')']
            elif parts[i+1] == '(' and parts[i+2] == '~' and p_c.match(parts[i+3]) and (parts[i+4] in sym) and parts[i+5] == '~' and p_c.match(parts[i+6]) and parts[i+7] == ')':
                parts[i:i+8] = ['(', '~', '~', parts[i+3], sym[(sym.index(parts[i+4])+1)%2], '~', '~', parts[i+6], ')']

    return ' '.join(parts)

def remove_double_not(sentence):
    parts = sentence.split(" ")
    for i in range(len(parts)-2):
        if parts[i] == '~' and parts[i+1] == "~":
            del parts[i:i+2]
    sentence = ' '.join(parts)
    return sentence

def prenex_form(sentence):
    parts = sentence.split(" ")
    for i in range(len(parts)):
        quantifier =  parts[i]
        if re.findall(r'(E|A).',quantifier):
            if (i != 0 or len(re.findall(r'(E|A).', parts[i-1]))==0):
                parts.remove(parts[i])
                if(parts[0] == "~"):
                    parts.insert(1,quantifier)
                else:
                    parts.insert(0,quantifier)
    sentence = ' '.join(parts)
    return sentence

def Skolemization(sentence):
    parts = sentence.split(" ")
    exist = re.findall(r'E.',sentence)
    uni = re.findall(r'A.',sentence)

    if len(uni) == 1:
        relate = f"f({uni[0][1]})"

    elif len(uni) > 1:
        relate = "f("
        for u in uni:
            relate= relate + str(u[1])
            relate = relate + ','
        relate = relate[:-1] + ')'
    if(exist and uni):
        for e in exist:
            for i in range(len(parts)):
                if(re.findall(r".*\(.*(,.*)*?\)",parts[i])):
                    if(e[1] in (list(parts[i]))):
                        parts[i] = str(re.findall(r".*\(",parts[i])[0]) + relate + ")"
            parts.remove(e)

    sentence = ' '.join(parts)
    return sentence

def eliminate_universal(sentence):
    parts = sentence.split(" ")
    parts = [part for part in parts if not re.findall(r'A.', part)]
    sentence = ' '.join(parts)
    return sentence

def convert_to_CNF(sentence):
    sentence = prenex_form(sentence)
    sentence = eliminate_implication(sentence)

    if (re.findall(r"~ ~",sentence)):
        sentence = remove_double_not(sentence)
    
    sentence = demorgans_law(sentence)

    if (re.findall(r"~ ~",sentence)):
        sentence = remove_double_not(sentence)

    sentence = demorgans_law(sentence)

    if (re.findall(r"~ ~",sentence)):
        sentence = remove_double_not(sentence)   

    sentence = Skolemization(sentence)
    sentence = eliminate_universal(sentence)
    return sentence

def turn_to_clauses(sentence):
    clauses = []
    for part in sentence.split('&'):
        clause = []
        for literal in part.split('|'):
            clause.append(literal.strip())
        clauses.append(clause)
    return clauses

def clean(sentence):
    parts = sentence.split(" ")
    for i in range(len(parts)):
        if parts[i] == "(" or parts[i] == ")":
            parts[i] = ""
    return ' '.join(parts)

def solve(clauses):
    resolved = False
    while not resolved:
        new_clauses = []
        for i in tqdm(range(len(clauses)), desc="Resolving Clauses"):
            for j in range(i+1, len(clauses)):
                clause1 = clauses[i]
                clause2 = clauses[j]
                for literal1 in clause1:
                    for literal2 in clause2:
                        if literal1 == '~' + literal2 or literal2 == '~' + literal1:
                            resolvent = [x for x in (clause1 + clause2) if x != literal1 and x != literal2]
                            if len(resolvent) == 0:
                                return True
                            if resolvent not in new_clauses:
                                new_clauses.append(resolvent)
                                resolved = False
        if not new_clauses:
            resolved = True
        else:
            clauses += new_clauses
    return False





print("\n-------------- Sentence1 --------------------------")
sentence1 = "~ Ay Az ( p(y) -> q(z) ) -> Ex ( p(x) -> q(x) )"
print("Orginal: ",sentence1)
sentence1 = convert_to_CNF(sentence1)
print("CNF: ",sentence1)
clauses1 = turn_to_clauses(sentence1)
print(clauses1)
result1 = solve(clauses1)
print("Is the set of clauses satisfiable?", not result1)

print("\n-------------- Sentence2 --------------------------")
sentence2 = "Ay Az ( p(y) -> q(z) ) -> Ex ( p(x) -> q(x) )"
print("Orginal: ",sentence2)
sentence2 = convert_to_CNF(sentence2)
print("CNF: ",sentence2)
clauses2 = turn_to_clauses(sentence2)
print(clauses2)
result2 = solve(clauses2)
print("Is the set of clauses satisfiable?", not result2)
