from metaphor.metaphor import Metaphor
from metaphor.ai.embeddings import Embeddings
from metaphor.settings import BASE_DIR
import numpy as np
import os
import re

class W2VSubs(Metaphor):

    def __init__(self, emb_info={}):
        if not emb_info:
            dim = 50
            emb_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.{}d.txt'.format(dim))
            emb_info = {'glove.6B.{}d'.format(dim): {'path': emb_path, 'dim': dim}}
        self.e = Embeddings('Embeddings', emb=emb_info)

    def _create(self, words_list, num_neighbors=5, fast_desired=False):
        words_vec = self.e.get_vectors(words_list)
        closest_n = self.e.closest_n(words_vec, num_neighbors, fast_desired=fast_desired)
        return closest_n

    def _reconstruct_core(self, text, closest_n):
        for w, closest in closest_n.items():
            substitute = closest[np.random.randint(0, len(closest))]
            text = re.sub(r"\b{}\b".format(w), substitute[0], text)
        return text

    def metaphorize(self, text=None, **kwargs):
        num_neighbors = kwargs.pop('num_neighbors', 5)
        fast_desired = kwargs.pop('fast_desired', False)
        correct = kwargs.pop('correct', False)
        words_tagged = self._deconstruct(text, PoS={'NOUN', 'ADJ', 'ADV'})
        words_list = [w for w, tag in words_tagged]
        closest_n = self._create(words_list, num_neighbors=num_neighbors, fast_desired=fast_desired)
        metaphor = self._reconstruct(correct, text, closest_n)
        return metaphor

