



def generate_pcfg(corpus, vocab):
    pos_corpus = generate_pos_corpus(corpus, vocab)
    grammar = generate_exhaustive_grammar(pos_corpus)
    while True:
        n_gram, prob = get_best_n_gram(grammar)
        if is_above_threshold(prob):
            grammar = add_non_terminal(grammar, n_gram)
        else:
            break
    return grammar


def generate_pos_corpus(corpus, vocab):
    '''Uses a POS vocabulary to convert a sentence corpus
       into a POS-tag-sequence corpus'''
    raise NotImplementedError()


def generate_exhaustive_grammar(corpus):
    '''Converts a corpus into an exhaustive CFG'''
    raise NotImplementedError()


def get_best_n_gram(grammar):
    '''Finds the best n-gram to replace with a new non-terminal,
       along with the probability of that n-gram'''
    raise NotImplementedError()


def is_above_threshold(prob):
    '''Checks whether a probability is high enough'''
    raise NotImplementedError()


def add_non_terminal(grammar, n_gram):
    '''Replaces an n-gram in a grammar with a new non-terminal'''
    raise NotImplementedError()
