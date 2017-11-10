from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from metaphor.models import Sentence,Dictionary
from metaphor.utils import get_language,get_nouns,get_random_connectors
from metaphor.settings import BASE_DIR

import random,pickle,os

def index(request):
    return render(request, 'homepage.html')

def random_metaphor(sentence_text):
    file_path = os.path.join(BASE_DIR,'metaphor/static/metaphors/metaphors.pkl')
    life_metaphors = pickle.load(open(file_path,"rb"))
    return life_metaphors[random.randint(1,len(life_metaphors)-1)]

def is_a_metaphor(sentence_text):
    nouns_list = get_nouns(sentence_text)
    metaphors = []
    if not nouns_list:
        return random_metaphor(sentence_text)
    for idx,noun in enumerate(nouns_list):
        adjective = Dictionary.objects.random(word_type='a.').word.lower()
        a_adjective = 'n' if adjective.startswith('a') else ''
        new_noun = Dictionary.objects.random().word.lower()
        metaphor = "{} is a{} {} {}".format(noun.capitalize(),a_adjective,adjective,new_noun)
        metaphors.append(metaphor)
    connectors = get_random_connectors(len(metaphors))
    return ' '.join([j for i in zip(metaphors,connectors) for j in i][:-1])

def create_metaphor(sentence_text, strategy="random"):
    if strategy == "random":
        return random_metaphor(sentence_text)
    elif strategy == "is_a":
        return is_a_metaphor(sentence_text)
    else:
        pass
    return ""

def metaphorize(request):
    if not request.POST.get('sentence'):
        return render(request,'homepage.html')
    sentence_text = request.POST['sentence']
    remote_addr = request.META.get('REMOTE_ADDR')
    lang = get_language(sentence_text)
    metaphor_text = None
    if lang and lang == 'English':
        metaphor_text = create_metaphor(sentence_text,strategy='is_a')
        sentence = Sentence(sentence_text=sentence_text,metaphor_text=metaphor_text,req_date=timezone.now(),remote_addr=remote_addr)
        sentence.save()
    context = {
        'metaphor_text': metaphor_text,
        'sentence_text': sentence_text,
        'lang': lang,
    }
    return render(request, 'homepage.html', context)