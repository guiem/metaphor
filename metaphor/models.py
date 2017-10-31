from django.db import models

class Sentence(models.Model):
    sentence_text = models.CharField(max_length=1000)
    metaphor_text = models.CharField(max_length=1000)
    req_date = models.DateTimeField('date requested')
    remote_addr = models.CharField(max_length=100)