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
    if files is None: bank = treebank.parsed_sents()[:10]
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

grammar_gs = learn_treebank(None, None)
grammar_pred = learn_pcfg_res(None)

for i in listStr:
    probab_gs = parse_viterbi_with_pcfg(grammar_gs, i[1])
    probab_pred = parse_viterbi_with_pcfg(grammar_pred, i[0])
    difference = abs(float(probab_gs) - float(probab_pred))
#    print difference
    amountOfSents+=1
    averageProb+=difference

print "Result Average Difference: ", averageProb/amountOfSents


#sent = treebank.tagged_sents()


