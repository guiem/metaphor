from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from metaphor.models import Sentence
from metaphor.utils import get_language
import random

def index(request):
    return render(request, 'homepage.html')

def create_metaphor(sentence_text):
    # Intelligent magic will happen here!
    life_metaphors = [
        "Life is a tale, told by an idiot, full of sound and fury, signifying nothing.",
        "All my life I thought air was free, until I bought a bag of chips.",
        "A day without sunshine is like..., you know, night.",
    ]
    return life_metaphors[random.randint(1,len(life_metaphors)-1)]

def metaphorize(request):
    sentence_text = request.POST['sentence']
    remote_addr = request.META.get('REMOTE_ADDR')
    lang = get_language(sentence_text)
    metaphor_text = None
    if lang and lang == 'English':
        metaphor_text = create_metaphor(sentence_text)
        sentence = Sentence(sentence_text=sentence_text,metaphor_text=metaphor_text,req_date=timezone.now(),remote_addr=remote_addr)
        sentence.save()
    context = {
        'metaphor_text': metaphor_text,
        'sentence_text': sentence_text,
        'lang': lang,
    }
    return render(request, 'homepage.html', context)