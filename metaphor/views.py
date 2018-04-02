from metaphor.models import Metaphor, Dictionary
from metaphor.decorators import check_recaptcha
from metaphor.utils import *
from metaphor.settings import BASE_DIR
from metaphor.ai.embeddings import Embeddings
from metaphor.random_metaphor import RandomMetaphor
from metaphor.is_a_metaphor import IsAMetaphor
from metaphor.w2v_subs import W2VSubs
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
    context = {'checked': 'word2vec_subst_fast'}
    if request.POST:
        return metaphorize(request)
    return render(request, 'homepage.html', context)


def strategies(request):
    return render(request, 'strategies.html')


def list_metaphors(request):
    metaphor_list = Metaphor.objects.order_by('-total_votes')
    paginator = Paginator(metaphor_list, 15)
    page = request.GET.get('page')
    metaphors = paginator.get_page(page)
    return render(request, 'metaphors.html', {'metaphors': metaphors})


@check_recaptcha
def vote(request, debug=False):
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


def create_metaphor(sentence_text, strategy="word2vec_subst_fast"):
    if strategy == "random":
        m = RandomMetaphor()
        return m.metaphorize()
    elif strategy == "is_a-random":
        m = IsAMetaphor()
        return m.metaphorize(sentence_text)
    elif strategy == "word2vec_subst":
        m = W2VSubs()
        return m.metaphorize(sentence_text)
    elif strategy == "word2vec_subst_fast":
        dim = 50
        emb_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.{}d.txt'.format(dim))
        emb_info = {'glove.6B.{}d'.format(dim): {'path': emb_path, 'dim': dim, 'sim_index': True}}
        m = W2VSubs(emb_info=emb_info)
        return m.metaphorize(sentence_text, fast_desired=True)
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
    can_do, info_id = resolve_can_do(sentence_text, lang)
    if can_do:
        metaphor_text = create_metaphor(sentence_text, strategy=strategy)
        metaphor = Metaphor(sentence_text=sentence_text, metaphor_text=metaphor_text, req_date=timezone.now(),
                            remote_addr=remote_addr, strategy=strategy)
        metaphor.save()
    context = {
        'metaphor_text': metaphor_text,
        'sentence_text': sentence_text,
        'can_do': can_do,
        'lang': lang,
        'checked': strategy,
        'info_id': info_id,
    }
    return render(request, 'homepage.html', context)
