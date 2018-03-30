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
