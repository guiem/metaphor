from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import numpy as np
from collections import defaultdict
import random

CONNECTORS = ['and','whereas',', on the other hand','yet','likewise','similarly','also','for one thing',
        ', for another thing','. In addition,','. Furthermore, ','. In other words, ','meanwhile']

# nltk.help.upenn_tagset() to list all NLTK tags
NOUN_TAGS = {'NN', 'NNP', 'NNS', 'NNPS'}
ADJECTIVE_TAGS = {'JJ', 'JJR', 'JJS'}


def get_language(text):
    score = defaultdict(int)
    words = word_tokenize(text.lower())
    stopwords.ensure_loaded
    stopwords_dict = {lang:stopwords.words(lang) for lang in stopwords.__dict__.get('_fileids')}
    for word in words:
        for lang,stop_list in stopwords_dict.items():
            if word in stop_list:
                score[lang] += 1
    if score:
        max_value = max(score.values())
        if max_value > 0:
            max_keys = [k.capitalize() for k,val in score.items() if val == max_value]
            return (' or ').join(max_keys)
    return "NA"


def get_PoS(text, PoS):
    words = []
    for word, pos in pos_tag(word_tokenize(text)):
        if pos in PoS:
            words.append((word, pos))
    return words


def get_random_connectors(num): 
    selection = [CONNECTORS[random.randint(1, len(CONNECTORS)-1)] for _ in range(0,num)]
    return selection


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def read_glove_vecs(glove_file):
    with open(glove_file, 'r') as f:
        words = set()
        word_to_vec_map = {}

        for line in f:
            line = line.strip().split()
            curr_word = line[0]
            words.add(curr_word)
            word_to_vec_map[curr_word] = np.array(line[1:], dtype=np.float64)

    return words, word_to_vec_map


def read_glove_vecs(glove_file, embedding_d):
    with open(glove_file, 'r') as f:
        word_id_dict = {}
        id_word_dict = {}
        word_vectors = np.empty((0, embedding_d), np.float64)
        test = {}
        curr_id = 0
        for line in f:
            line = line.strip().split()
            curr_word = line[0]
            word_id_dict[curr_word] = curr_id
            #word_vectors = np.append(word_vectors,np.array([line[1:]], dtype=np.float64))
            test[curr_id] = np.array([line[1:]], dtype=np.float64)
            curr_id += 1
        word_vectors = test
    return word_id_dict, id_word_dict, word_vectors


def most_similar(word_vectors, w, word_id_dict, id_word_dict, number=5):
    word_vec = word_vectors[word_id_dict[w]]
    dst = (np.dot(word_vectors, word_vec.T)
               / np.linalg.norm(word_vectors, axis=0)
               / np.linalg.norm(word_vec))
    word_ids = np.argsort(-dst)
    return [(inverse_dictionary[x], dst[x]) for x in word_ids[:number] if x in inverse_dictionary]