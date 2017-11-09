from django.contrib import admin
from .models import Sentence, Dictionary

class SentenceAdmin(admin.ModelAdmin):
    list_display = ('sentence_text', 'metaphor_text', 'req_date', 'remote_addr')

admin.site.register(Sentence, SentenceAdmin)

class DictionaryAdmin(admin.ModelAdmin):
    list_display = ('word', 'word_type', 'definition')

admin.site.register(Dictionary, DictionaryAdmin)