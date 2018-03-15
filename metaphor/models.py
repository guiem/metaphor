from django.db import models
from django.db.models import Count
from random import randint


class Metaphor(models.Model):
    sentence_text = models.CharField(max_length=1000)
    metaphor_text = models.CharField(max_length=1000)
    strategy = models.CharField(max_length=1000)
    req_date = models.DateTimeField('date requested')
    remote_addr = models.CharField(max_length=100)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def _get_total_votes(self):
        return self.upvotes - self.downvotes

    total_votes = property(_get_total_votes)

class DictionaryManager(models.Manager):
    def random(self,word_type='n.'):
        count = self.filter(word_type=word_type).aggregate(ids=Count('id'))['ids']
        random_index = randint(0, count - 1)
        return self.filter(word_type=word_type)[random_index]

class Dictionary(models.Model):
    word = models.CharField(max_length=100)
    word_type = models.CharField(max_length=50)
    definition = models.CharField(max_length=1000)
    objects = DictionaryManager()