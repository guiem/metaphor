import pandas as pd
import numpy as np
import csv
from gputils import cosine_similarity
from metaphor.singleton import Singleton


class Embeddings(metaclass=Singleton):

    def __init__(self, name, emb={}):
        super().__init__()
        self.embeddings = {}
        self.default_e = None
        if emb:
            self.add_embeddings(emb)

    def add_embeddings(self, emb):
        for e_id, info in emb.items():
            if not self.default_e:  # first embedding provided will be considered the default one if not assigned yet
                self.default_e = e_id
            if e_id not in self.embeddings:
                dtypes = {k: info.get('dtype', np.float16) for k in range(1, info.get('dim') + 1)}
                self.embeddings[e_id] = pd.read_csv(info.get('path'), sep=" ", index_col=0, dtype=dtypes, header=None,
                                                   quoting=csv.QUOTE_NONE)

    def get_E(self, e_id=None):
        if not e_id:
            e_id = self.default_e
        return self.embeddings[e_id]

    def word_exists(self, w, e_id=None):
        if not e_id:
            e_id = self.default_e
        return w in self.embeddings[e_id].index

    def closest_n(self, words, n, e_id=None):
        closest = {}
        E = self.get_E(e_id)
        for word in words:
            if word not in closest and self.word_exists(word):
                word_vec = E.loc[word]
                sims = cosine_similarity(E, word_vec)
                sims.loc[word] = 0  # little trick to avoid retrieving the word
                closest_n = sims.nlargest(n)
            closest[word] = list(zip(closest_n.index.values, closest_n.values))
        return closest
