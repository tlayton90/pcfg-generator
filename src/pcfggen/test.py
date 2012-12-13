import nltk
import __init__
import sys
import re
from nltk import *
from nltk.corpus import treebank
from nltk.treetransforms import *


#creating PCFG from parsed sentences
#used for golden standart pcfg
def learn_treebank(files=None, markov_order=None):
    #default is reading from treebank.parsed_sents() - 10% of penn Tree bank
    if files is None: bank = treebank.parsed_sents()[:2]
    else: bank = treebank.parsed_sents(files)
    return learn_trees_gs(bank, collapse=True, markov_order=markov_order)

#returns the most probable PCFG for trees
def learn_trees_gs(trees, collapse=True, markov_order=None):
    productions = []
    for tree in trees:
        if collapse: tree.collapse_unary(collapsePOS=False)
        if markov_order:
            tree.chomsky_normal_form(horzMarkov=markov_order)
        else:
            tree.chomsky_normal_form()
        productions += tree.productions()
    grammar = nltk.grammar.induce_pcfg(Nonterminal('S'), productions)
    return grammar

#make our PCFG
#takes a file with parsed trees taking them as an argument from command line
def learn_pcfg_res(file_input=None):
    if file_input is None: bank = treebank.tagged_sents()[:10]
    else: bank = treebank.tagged_sents(file_input)
    grammar = __init__.generate_pcfg(bank)
    return grammar


#function for viterbi parsing. returns probability for sentence
def parse_viterbi_with_pcfg (grammar, sentence):
    #converts grammar into neccessary format
    viterbi_parser = nltk.ViterbiParser(grammar)
    viterbiTree=viterbi_parser.parse(sentence.split())
    probability = []
    if viterbiTree == None: probability.append(0.0)
    else: probability = re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", str(viterbiTree))
    return probability[-1]


#creating base of sentences for our PCFG
listStr = []
stri = ""
strj = ""
for i in treebank.tagged_sents()[:2]:
    for j in i:
        stri+=str(j[1])+" "
        strj+=str(j[0])+" "
    listStr.append((stri, strj))
    stri = ""

averageProb = 0
amountOfSents = 0

i = learn_treebank(None)
prod = i.productions()
prodsEmp = []
prods=[]
for k in prod:
    #print k.prob()
    if not str(k.rhs()[0]).isupper():
        product = nltk.grammar.WeightedProduction(k.lhs(), ["", ""], prob = k.prob())
        if product not in prodsEmp:
            prodsEmp.append(product)
    else: prods.append(k)

def rules_for_one_nonterm(nonTerm, prods):
    term = str(nonTerm)
    itog_prod = []
    for j in prods:
        if len(j.rhs())==2:
            if str(j.rhs()[0]) == term or str(j.rhs()[1])==term:
                if str(j.rhs()[0]) == term and str(j.rhs()[1])==term:
                    product = nltk.grammar.WeightedProduction(j.lhs(), [term, term], prob = j.prob())
                    itog_prod.append(product)
                elif str(j.rhs()[0]) == term:
                    product = nltk.grammar.WeightedProduction(j.lhs(), [term, j.rhs()[1]], prob = j.prob())
                    itog_prod.append(product)
                else:
                    product = nltk.grammar.WeightedProduction(j.lhs(), [j.rhs()[0], term], prob = j.prob())
                    itog_prod.append(product)
            else:
                itog_prod.append(j)
        else:
            if str(j.rhs()[0]) == term:
                    product = nltk.grammar.WeightedProduction(j.lhs(), [term, ], prob = j.prob())
                    itog_prod.append(product)
            else:
                itog_prod.append(j)
            
    return itog_prod

first_elem = prodsEmp.pop(0)
first_step_prod = rules_for_one_nonterm(first_elem.lhs(), prods)

result =  []

def recurs_CFG(prev_prod, prE):
    next_it = prE.pop(0)
    if len(prE)>0:
        next_prod = rules_for_one_nonterm(next_it.lhs(), prev_prod)
        recurs_CFG(next_prod, prE)
    else:
        result[:] = rules_for_one_nonterm(next_it.lhs(), prev_prod)[:]
    #return result


recurs_CFG(first_step_prod, prodsEmp)

grammar_gs = nltk.grammar.induce_pcfg(Nonterminal('S'), result)
grammar_pred = learn_pcfg_res(None)

for i in listStr:
    probab_gs = parse_viterbi_with_pcfg(grammar_gs, i[0])
    probab_pred = parse_viterbi_with_pcfg(grammar_pred, i[0])
    difference = abs(float(probab_gs) - float(probab_pred))
    amountOfSents+=1
    averageProb+=difference

print "Result Average Difference: ", averageProb/amountOfSents


#sent = treebank.tagged_sents()


