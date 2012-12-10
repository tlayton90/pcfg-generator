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
    #default is reading from treebank.parsed_sents()
    if files is None: bank = treebank.parsed_sents()
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
def learn_pcfg_res(file_input):
    grammar = __init__.generate_pcfg(file_input)
    return grammar


#function for viterbi parsing. returns probability for sentence
def parse_viterbi_with_pcfg (grammar_input, sentence):
    #converts grammar into neccessary format
    grammar = nltk.parse_pcfg(grammar_input)    
    viterbi_parser = nltk.ViterbiParser(grammar)
    viterbiTree=viterbi_parser.parse(sentence.split())
    probability = re.findall(r"[-+]?\d*\.\d+|\d+", str(i))
    return probability[-1]



sentences = file(sys.argv[1])
for i in sentences:
    grammar_gs = learn_treebank(sys.argv[2], None)
    grammar_pred = learn_pcfg_res(sys.argv[2])
    probab_gs = parse_viterbi_with_pcfg(grammar_gs, i)
    probab_pred = parse_viterbi_with_pcfg(grammar_pred, i)
    print i, abs(probab_gs-probab_pred)



#sent = treebank.tagged_sents()


