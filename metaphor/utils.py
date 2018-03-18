from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
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
