# Association Recommendation Analysis

import itertools


itemPath = 'EB-build-goods.sql'
receiptsPath = '75000-out1.csv'

with open(receiptsPath, "r") as receiptsFile:
    receiptsdata = receiptsFile.read().split('\n')


baskets = (line.split(', ')[1:] for line in receiptsdata[0:-1])
baskets = list(baskets)

with open(itemPath, "r") as itemfile:
    lines = itemfile.read().split('\n')

items = (line.split('(')[1][0:-2].split(',') for line in lines[0:-1])
items = list(items)

itemMap = { line[0] : line[1] + " " + line[2] for line in items }

numItems = len(items)
numBaskets = len(baskets)



def support(itemset):
    basketSubset = baskets
    for item in itemset:
        basketSubset = [basket for basket in basketSubset if item in basket]
    return float(len(basketSubset))/float(numBaskets)


supportItems1 = []
minsupport = 0.01


for item in range(numItems):
    itemset = [str(item)]
    #print(item)
    if support(itemset)>=minsupport:
        supportItems1.append(str(item))

def aprioriIteration(i, supportItems, assocRules, newSupportItems, minsupport, minconfidence):
    #print(supportItems)
    for itemset in itertools.combinations(supportItems,i):
        itemset = list(itemset)
        if support(itemset) >= minsupport:
            for j in range(i):
                rule_to = itemset[j]
                rule_from = [x for x in itemset if x!=itemset[j]]
                confidence = support(itemset)/support(rule_from)
                if confidence > minconfidence:
                    assocRules.append((rule_from, rule_to))
                    for x in itemset:
                        if x not in newSupportItems:
                            newSupportItems.append(x)
    
    return assocRules, newSupportItems

#print(supportItems1)
assocRuless, supportItems2 = aprioriIteration(2,supportItems1,[],[],0.01,0.5)

assocRuless, supportItems3 = aprioriIteration(3,supportItems2,assocRuless,[],0.01,0.5)


def ruleMeta(rule):
    rule_from = [itemMap[x] for x in rule[0]]
    #print(rule_from+" "+itemMap[rule[1]])
    return rule_from,itemMap[rule[1]]

print([ ruleMeta(rule) for rule in assocRuless])