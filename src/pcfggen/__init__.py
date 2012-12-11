import nltk.grammar, nltk.tag
import uuid

from randsent import *



def generate_pcfg(tagged_sents):
    grammar = generate_exhaustive_grammar(tagged_sents)
    while True:
        while True:
            diff_index, base_prod = find_join(grammar)
            if diff_index is not None:
                grammar = add_join_nonterminal(grammar, diff_index, base_prod)
            else:
                break
        n_gram, freq = get_best_n_gram(grammar)
        if n_gram is not None:
            grammar = add_sub_nonterminal(grammar, n_gram, freq)
        else:
            break
    return grammar


def generate_exhaustive_grammar(tagged_sents, start = 'ROOT'):
    '''Converts a probabilistic POS-tag-sequence corpus into an exhaustive CFG'''
    prods = []
    start = nltk.grammar.Nonterminal(start)
    for tagged_sent in tagged_sents:
        prod = nltk.grammar.WeightedProduction(start, [nltk.grammar.Nonterminal(tag) for token, tag in tagged_sent], prob = 1.0 / len(tagged_sents))
        prod.freq = prod.prob()
        prods.append(prod)
    grammar = nltk.grammar.WeightedGrammar(start, prods)
    grammar.new_symbol_count = 0
    return grammar


def get_best_n_gram(grammar, n = 2):
    '''Finds the best n-gram to replace with a new non-terminal,
       along with the relative frequency of that n-gram'''
    n_grams = {} # maps n-grams to freqs
    for prod in grammar.productions():
        if len(prod.rhs()) == n:
            continue
        for i in range(len(prod.rhs()) - (n - 1)):
            n_gram = prod.rhs()[i:i + n]
            if n_gram not in n_grams:
                n_grams[n_gram] = 0
            n_grams[n_gram] += prod.freq
    if not n_grams:
        return (None, None)
    else:
        return max(n_grams.items(), key = lambda item: item[1])


def add_sub_nonterminal(grammar, n_gram, freq):
    '''Replaces an n-gram in a grammar with a new non-terminal'''
    n_gram = list(n_gram)
    prods = []
    nt = nltk.grammar.Nonterminal('sub_%s_%s' % ('_'.join("(%s)" % nt.symbol() for nt in n_gram), grammar.new_symbol_count))
    grammar.new_symbol_count += 1
    for prod in grammar.productions():
        rhs = list(prod.rhs())
        i = 0
        while i < len(rhs):
            if rhs[i:i + len(n_gram)] == n_gram:
                rhs[i:i + len(n_gram)] = [nt]
            i += 1
        new_prod = nltk.grammar.WeightedProduction(prod.lhs(), rhs, prob = prod.prob())
        new_prod.freq = prod.freq
        prods.append(new_prod)
    new_prod = nltk.grammar.WeightedProduction(nt, n_gram, prob = 1.0)
    new_prod.freq = freq
    prods.append(new_prod)
    new_grammar = nltk.grammar.WeightedGrammar(grammar.start(), prods)
    new_grammar.new_symbol_count = grammar.new_symbol_count
    return new_grammar

def find_join(grammar):
    for i in range(len(grammar.productions())):
        prod1 = grammar.productions()[i]
        if len(prod1.rhs()) < 2:
            continue
        for j in range(i + 1, len(grammar.productions())):
            prod2 = grammar.productions()[j]
            if len(prod1.rhs()) != len(prod2.rhs()):
                continue
            diff_index = None
            for k in range(len(prod1.rhs())):
                if prod1.rhs()[k] != prod2.rhs()[k]:
                    if diff_index is None:
                        diff_index = k
                    else:
                        diff_index = None
                        break
            if diff_index is not None:
                return (diff_index, prod1)
    return (None, None)

def add_join_nonterminal(grammar, diff_index, base_prod):
    prods = []
    new_prods = []
    for prod in grammar.productions():
        if len(prod.rhs()) == len(base_prod.rhs()) and all(prod.rhs()[i] == base_prod.rhs()[i] or i == diff_index for i in range(len(prod.rhs()))):
            prods.append(prod)
        else:
            new_prods.append(prod)
    nt = nltk.grammar.Nonterminal('join_%s_%s' % ('_'.join("(%s)" % prod.rhs()[diff_index] for prod in prods), grammar.new_symbol_count))
    grammar.new_symbol_count += 1
    total_freq = sum(prod.freq for prod in prods)
    new_rhs = list(base_prod.rhs())
    new_rhs[diff_index] = nt
    for prod in prods:
        new_prod = nltk.grammar.WeightedProduction(prod.lhs(), new_rhs, prob = prod.prob())
        new_prod.freq = prod.freq
        new_prods.append(new_prod)
        
        new_prod = nltk.grammar.WeightedProduction(nt, [prod.rhs()[diff_index]], prob = prod.freq / total_freq)
        new_prod.freq = prod.freq
        new_prods.append(new_prod)
    new_grammar = nltk.grammar.WeightedGrammar(grammar.start(), new_prods)
    new_grammar.new_symbol_count = grammar.new_symbol_count
    return new_grammar
