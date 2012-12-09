import nltk.grammar
import random

def generate_random_sentence(pcfg, tagged_words, start = 'ROOT'):
    vocab = make_vocab(tagged_words)
    def recurse(nt):
        prods = pcfg.productions(lhs = nt)
        if prods:
            v = 1 - random.random()
            for prod in prods:
                if v <= prod.prob():
                    return sum((recurse(nt) for nt in prod.rhs()), [])
                else:
                    v -= prod.prob()
            raise Exception()
        else:
            return [random.choice(vocab[nt.symbol()])]
    return recurse(nltk.grammar.Nonterminal(start))

def make_vocab(tagged_words):
    vocab = {}
    for word, pos in tagged_words:
        if pos not in vocab:
            vocab[pos] = []
        vocab[pos].append(word)
    return vocab
