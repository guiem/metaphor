from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk import FreqDist
from nltk.corpus import brown
from nltk.tag.mapping import tagset_mapping
from collections import defaultdict
import random

CONNECTORS = ['and','whereas',', on the other hand','yet','likewise','similarly','also','for one thing',
        ', for another thing','. In addition,','. Furthermore, ','. In other words, ','meanwhile']

# nltk.help.upenn_tagset() to list all NLTK tags
# https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
# Universal tagset http://universaldependencies.org/u/pos/
PTB_UNIVERSAL_MAP = tagset_mapping('en-ptb', 'universal')


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
        universal_pos = PTB_UNIVERSAL_MAP[pos]
        if universal_pos in PoS:
            words.append((word, pos))
    return words


def most_frequent(n, categories={'ADJ', 'NOUN', 'ADV'}):
    frequency_list = FreqDist((w.lower(), tag) for w, tag in brown.tagged_words(tagset='universal'))
    most_freq = set()
    for (w, tag), count in frequency_list.most_common():
        if len(most_freq) == n:
            break
        if tag in categories and w not in most_freq:
            most_freq.add(w)
    return list(most_freq)


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


def resolve_can_do(sentence_text, lang):
    info_id = None
    can_do = lang and 'English' in lang and not sentence_text.startswith('i ')
    if not can_do and lang != "NA" and not sentence_text.startswith('i '):
        info_id = 1
    elif not can_do and lang == "NA":
        info_id = 2
    elif not can_do and sentence_text.startswith('i '):
        info_id = 3
    return can_do, info_id
