import re
from collections import Counter
import nltk
nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('portuguese')


# Funções utilizadas

def remove_punctuation(text):
    return re.sub(r'[^\w\s]', ' ', text)

def tokenize(text):
    return re.findall(r'\w+', text)


def remove_stopwords(text):
    tokens_limpos=[]
    for item in text:
        if(item not in stopwords) & (len(item) > 1):
            tokens_limpos.append(item)
    return tokens_limpos


def count_sort_n_tokens(tokens, n=30):
    return Counter(tokens).most_common(n)


def normalize_candidate_felipe_avila(text):
    escrita_equivocada = r'Felipe D’Ávila|Felipe d’Ávila'
    escrita_padrao = 'Felipe D’Avila'
    regex = escrita_equivocada
    return re.sub(regex, escrita_padrao, text)


def normalize_candidate_lula(text):
    escrita_equivocada = r'Luiz Inácio Lula da Silva'
    escrita_padrao = 'Lula'
    regex = escrita_equivocada
    return re.sub(regex, escrita_padrao, text)
