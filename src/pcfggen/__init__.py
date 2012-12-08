import nltk.grammar, nltk.tag
import uuid



def generate_pcfg(tagged_sents):
##    pos_corpus = generate_pos_corpus(sents)
    grammar = generate_exhaustive_grammar(tagged_sents)
    while True:
        n_gram, freq = get_best_n_gram(grammar)
        if n_gram is not None and is_above_threshold(freq):
            grammar = create_non_terminal(grammar, n_gram, freq)
        else:
            break
    return grammar


##def generate_pos_corpus(sents):
##    '''Uses a POS tagger to convert a sentence corpus
##       into a POS-tag-sequence corpus'''
##    return nltk.tag.batch_pos_tag(sents)


def generate_exhaustive_grammar(tagged_sents, start = 'ROOT'):
    '''Converts a probabilistic POS-tag-sequence corpus into an exhaustive CFG'''
    prods = []
    start = nltk.grammar.Nonterminal(start)
    for tagged_sent in tagged_sents:
        prod = nltk.grammar.WeightedProduction(start, [nltk.grammar.Nonterminal(tag) for token, tag in tagged_sent], prob = 1.0 / len(tagged_sents))
        prod.freq = prod.prob()
        prods.append(prod)
    grammar = nltk.grammar.WeightedGrammar(start, prods)
    grammar.new_tag_count = 0
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


def is_above_threshold(freq):
    '''Checks whether a relative frequency is high enough'''
    return freq >= 0.0


def create_non_terminal(grammar, n_gram, freq):
    n_gram = list(n_gram)
    '''Replaces an n-gram in a grammar with a new non-terminal'''
    prods = []
    nt = nltk.grammar.Nonterminal('_'.join("({0})".format(nt.symbol()) for nt in n_gram))
    grammar.new_tag_count += 1
    for prod in grammar.productions():
        rhs = list(prod.rhs())
        i = 0
        while i < len(rhs):
            if rhs[i:i + len(n_gram)] == n_gram:
                rhs[i:i + len(n_gram)] = [nt]
            i += 1
        new_prod = nltk.grammar.WeightedProduction(prod.lhs(), rhs, prob = prod.prob())
        new_prod.freq = prod.freq * prod.prob()
        prods.append(new_prod)
    new_prod = nltk.grammar.WeightedProduction(nt, n_gram, prob = 1.0)
    new_prod.freq = freq
    prods.append(new_prod)
    new_grammar = nltk.grammar.WeightedGrammar(grammar.start(), prods)
    new_grammar.new_tag_count = grammar.new_tag_count
    return new_grammar
