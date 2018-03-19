from metaphor.models import Metaphor, Dictionary
from metaphor.decorators import check_recaptcha
from metaphor.utils import *
from metaphor.settings import BASE_DIR
from metaphor.ai.embeddings import Embeddings
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
import numpy as np
import random
import pickle
import re
import os


def index(request):
    context = {'checked':'word2vec_subst'}
    if request.POST:
        return metaphorize(request)
    return render(request, 'homepage.html', context)

def strategies(request):
    return render(request, 'strategies.html')


def random_metaphor():
    file_path = os.path.join(BASE_DIR, 'static/metaphors/metaphors.pkl')
    life_metaphors = pickle.load(open(file_path, "rb"), encoding='utf-8')
    return life_metaphors[random.randint(1, len(life_metaphors)-1)]


def is_a_metaphor(sentence_text):
    nouns_tagged = get_PoS(sentence_text, PoS = {'NOUN'})
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


def word2vec_substitution(sentence_text, level=1, num_neighbors=5, emb_info={}):
    if not emb_info:
        emb_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
        emb_info = {'glove.6B.50d': {'path': emb_path, 'dim':50}}
    e = Embeddings('Embeddings', emb = emb_info)
    words_tagged = get_PoS(sentence_text, PoS = {'NOUN', 'ADJ', 'ADV'})
    words = [w for w, tag in words_tagged]
    closest_n = e.closest_n(words, num_neighbors)
    for w, closest in closest_n.items():
        substitute = closest[np.random.randint(0, len(closest))]
        sentence_text = re.sub(r"\b{}\b".format(w), substitute[0], sentence_text)
    return sentence_text

# TODO: make vec_metaphor based on pairs adj-word (context), similar to analogy


def create_metaphor(sentence_text, strategy="is_a-random"):
    if strategy == "random":
        return random_metaphor()
    elif strategy == "is_a-random":
        return is_a_metaphor(sentence_text)
    elif strategy == "word2vec_subst":
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
    can_do = lang and 'English' in lang
    if can_do:
        metaphor_text = create_metaphor(sentence_text.lower(), strategy=strategy)
        metaphor = Metaphor(sentence_text=sentence_text, metaphor_text=metaphor_text, req_date=timezone.now(),
                            remote_addr=remote_addr, strategy=strategy)
        metaphor.save()
    context = {
        'metaphor_text': metaphor_text,
        'sentence_text': sentence_text,
        'can_do': can_do,
        'lang': lang,
        'checked': strategy,
    }
    return render(request, 'homepage.html', context)


def list_metaphors(request):
    metaphor_list = Metaphor.objects.order_by('-total_votes')
    paginator = Paginator(metaphor_list, 15)
    page = request.GET.get('page')
    metaphors = paginator.get_page(page)
    return render(request, 'metaphors.html', {'metaphors': metaphors})

@check_recaptcha
def vote(request):
    if request.recaptcha_is_valid:
        metaphor_id = request.POST.get('metaphor_id')
        direction = request.POST.get('direction')
        metaphor = get_object_or_404(Metaphor, pk=metaphor_id)
        if direction == 'up':
            metaphor.upvotes = metaphor.upvotes + 1
        elif direction == 'down':
            metaphor.downvotes = metaphor.downvotes + 1
        metaphor.total_votes = metaphor.upvotes - metaphor.downvotes
        metaphor.save()
    return HttpResponseRedirect("/metaphors")