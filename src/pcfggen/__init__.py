import nltk.grammar
import uuid



def generate_pcfg(corpus, vocab):
    pos_corpus = generate_pos_corpus(corpus, vocab)
    grammar = generate_exhaustive_grammar(pos_corpus)
    while True:
        n_gram, freq = get_best_n_gram(grammar)
        if n_gram is not None and is_above_threshold(freq):
            grammar = create_non_terminal(grammar, n_gram, freq)
        else:
            break
    return grammar


def generate_pos_corpus(corpus, vocab):
    '''Uses a POS vocabulary to convert a sentence corpus
       into a POS-tag-sequence corpus'''
    pos_corpus = []
    for sent in corpus:
        #TODO: use vocab (or tagger) to produce seqs and probs and add to pos_corpus
        pos_corpus.append((1.0 / len(corpus), sent.split()))
    return pos_corpus


def generate_exhaustive_grammar(pos_corpus, start = 'ROOT'):
    '''Converts a probabilistic POS-tag-sequence corpus into an exhaustive CFG'''
    prods = []
    for prob, seq in pos_corpus:
        prod = nltk.grammar.parse_pcfg_production("{0} -> {1} [{2}]".format(start, " ".join(seq), prob))[0]
        prod.freq = prod.prob()
        prods.append(prod)
    return nltk.grammar.WeightedGrammar(start, prods)


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
        pass
    if not n_grams:
        return (None, None)
    else:
        return max(n_grams.items(), key = lambda item: item[1])


def is_above_threshold(freq):
    '''Checks whether a relative frequency is high enough'''
    #TODO: return comparison to some selected probability
    return freq >= 1.0


def create_non_terminal(grammar, n_gram, freq):
    n_gram = list(n_gram)
    '''Replaces an n-gram in a grammar with a new non-terminal'''
    prods = []
    nt = nltk.grammar.Nonterminal('{0}-{1}'.format('-'.join(nt.symbol() for nt in n_gram), uuid.uuid1()))
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
    return nltk.grammar.WeightedGrammar(grammar.start(), prods)
