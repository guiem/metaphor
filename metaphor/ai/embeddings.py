import pandas as pd
import numpy as np
import csv
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

    def cosine_similarity(self, word, e_id=None):
        E = self.get_E(e_id)
        w = E.loc[word]
        dot = E.dot(w.transpose())
        norm_u = np.linalg.norm(E, axis=1)
        norm_v = np.linalg.norm(w)
        cosine_similarity = dot / (norm_u * norm_v)
        return cosine_similarity

    def closest_n(self, word, n, e_id=None):
        sims = self.cosine_similarity(word, e_id=e_id)
        sims.loc[word] = 0  # little trick to avoid retrieving the word
        closest_n = sims.nlargest(n)
        return list(zip(closest_n.index.values, closest_n.values))
