from django.conf.urls import url
from django.urls import path
from django.contrib import admin
from . import views
from metaphor.ai.embeddings import Embeddings
from metaphor.settings import BASE_DIR
import os

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', views.index, name='index'),
    path('metaphors/', views.list_metaphors, name='list_metaphors'),
    path('strategies/', views.strategies, name='strategies'),
    path('metaphors/vote/', views.vote, name='vote'),
]

# Operations that will be executed at the beginning to avoid timeouts

# 1. Loading embeddings at start
emb_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
emb_info = {'glove.6B.50d': {'path': emb_path, 'dim':50, 'sim_index': True}}
e = Embeddings('Embeddings', emb=emb_info)