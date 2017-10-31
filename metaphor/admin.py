from django.contrib import admin
from .models import Sentence

class SentenceAdmin(admin.ModelAdmin):
    list_display = ('sentence_text', 'metaphor_text', 'req_date', 'remote_addr')

admin.site.register(Sentence, SentenceAdmin)