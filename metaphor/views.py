from django.shortcuts import render
from django.utils import timezone
from metaphor.models import Metaphor, Dictionary
from metaphor.utils import *
from metaphor.settings import BASE_DIR
from metaphor.ai.embeddings import Embeddings
import random
import pickle
import os


def index(request):
    return render(request, 'homepage.html')


def random_metaphor():
    file_path = os.path.join(BASE_DIR, 'static/metaphors/metaphors.pkl')
    life_metaphors = pickle.load(open(file_path, "rb"), encoding='utf-8')
    return life_metaphors[random.randint(1, len(life_metaphors)-1)]


def is_a_metaphor(sentence_text):
    nouns_tagged = get_PoS(sentence_text, PoS = NOUN_TAGS)
    nouns_list = [n for n, tag in nouns_tagged]
    metaphors = []
    if not nouns_list:
        return random_metaphor()
    for idx, noun in enumerate(nouns_list):
        adjective = Dictionary.objects.random(word_type='a.').word.lower()
        a_adjective = 'n' if adjective.startswith(('a', 'e', 'i', 'o', 'u')) else ''
        new_noun = Dictionary.objects.random().word.lower()
        metaphor = u"{} is a{} {} {}".format(noun.capitalize(), a_adjective, adjective, new_noun)
        metaphors.append(metaphor)
    connectors = get_random_connectors(len(metaphors))
    return ' '.join([j for i in zip(metaphors, connectors) for j in i][:-1])+"."


def word2vec_substitution(sentence_text, level=1, num_neighbours=5, emb_info={}):
    if not emb_info:
        emb_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
        emb_info = {'glove.6B.50d': {'path': emb_path, 'dim':50}}
    e = Embeddings('Embeddings', emb = emb_info)
    words_tagged = get_PoS(sentence_text, PoS = NOUN_TAGS.union(ADJECTIVE_TAGS))
    for w, tag in words_tagged:
        closest_n = e.closest_n(w, num_neighbours)
        substitute = closest_n[np.random.randint(0, len(closest_n))]
        sentence_text = sentence_text.replace(w, substitute[0])
    return sentence_text

# TODO: make vec_metaphor based on pairs adj-word (context), similar to analogy

def create_metaphor(sentence_text, strategy="is_a"):
    if strategy == "random":
        return random_metaphor()
    elif strategy == "is_a":
        return is_a_metaphor(sentence_text)
    elif strategy == "word2vec_substitution":
        return word2vec_substitution(sentence_text)
    else:
        pass
    return ""


def metaphorize(request):
    if not request.POST.get('sentence'):
        return render(request, 'homepage.html')
    sentence_text = request.POST['sentence']
    remote_addr = get_client_ip(request)  # request.META.get('REMOTE_ADDR')
    strategy = request.POST['strategy']
    lang = get_language(sentence_text)
    metaphor_text = None
    if lang and lang == 'English':
        metaphor_text = create_metaphor(sentence_text, strategy=strategy)
        sentence = Metaphor(sentence_text=sentence_text, metaphor_text=metaphor_text, req_date=timezone.now(),
                            remote_addr=remote_addr)
        sentence.save()
    context = {
        'metaphor_text': metaphor_text,
        'sentence_text': sentence_text,
        'lang': lang,
    }
    return render(request, 'homepage.html', context)
