import pandas as pd
import numpy as np
import csv
import os
import pickle
from builtins import str
from gputils import cosine_similarity
from sklearn.metrics.pairwise import cosine_similarity as cosine_similarity_sk
import nmslib
from metaphor.singleton import Singleton
from metaphor.utils import *
from metaphor.settings import BASE_DIR


class Embeddings(metaclass=Singleton):

    def __init__(self, name, emb={}):
        super().__init__()
        self.embeddings = {}
        self.default_e = None
        self.similarities = {}
        self.sim_index = {}
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
            if info.get('similarities_dim'):
                dim_S = info.get('similarities_dim')
                words = most_frequent(dim_S, categories={'ADJ', 'NOUN', 'ADV'})
                E = self.embeddings[e_id].loc[self.embeddings[e_id].index.intersection(words)]
                existing_words = E.index.values
                sims = cosine_similarity_sk(E, E)
                sims_df = pd.DataFrame(sims, index=existing_words, columns=existing_words, dtype=np.float16)
                self.similarities[e_id] = sims_df
            if info.get('sim_index'):
                sim_index_path = os.path.join(BASE_DIR, 'data/{}_sim.index'.format(e_id))
                if os.path.isfile(sim_index_path):
                    index = nmslib.init(method='hnsw', space='cosinesimil')
                    index.loadIndex(sim_index_path)
                else:
                    E = self.embeddings[e_id]
                    index = nmslib.init(method='hnsw', space='cosinesimil')
                    index.addDataPointBatch(E)
                    index.createIndex({'post': 2}, print_progress=False)
                    index.saveIndex(sim_index_path)
                self.sim_index[e_id] = index

    def get_E(self, e_id=None):
        e_id = e_id or self.default_e
        return self.embeddings[e_id]

    def word_exists(self, w, e_id=None):
        e_id = e_id or self.default_e
        return w in self.embeddings[e_id].index

    def get_vectors(self, words, e_id=None):
        e_id = e_id or self.default_e
        return [(w, self.embeddings[e_id].loc[w]) for w in words if self.word_exists(w)]

    def closest_n(self, words, n, e_id=None, fast_desired=False):
        # words: list of tuples (word, word_vec)
        # fast desired: if True it tries to execute the fastest strategy applicable
        closest = {}
        e_id = e_id or self.default_e
        E = self.get_E(e_id)
        for word, word_vec in words:
            if word not in closest and self.word_exists(word):
                if fast_desired and e_id in self.sim_index:
                    # Hierarchical Navigable Small World graphs
                    ids, distances = self.sim_index[e_id].knnQuery(word_vec, k=n+1) # +1 because it retrieves itself
                    index_values = E.iloc[ids[1:]].index.values # strong assumption that first element is the word itself
                    similarities = 1 - distances[1:]
                elif (fast_desired and e_id in self.similarities) and (word in self.similarities[e_id].index):
                    # Subset of most frequent word matrix of computed distances
                    sims = self.similarities[e_id].loc[word]
                    sims[word] = 0 # little trick to avoid retrieving the word
                    transp_sims = sims.transpose()
                    closest_n = transp_sims.nlargest(n)
                    index_values = closest_n.index.values
                    similarities = closest_n.values
                else:
                    # Compute cosine_similarity online for every word
                    sims = cosine_similarity(E, word_vec)
                    sims.loc[word] = 0  # little trick to avoid retrieving the word
                    closest_n = sims.nlargest(n)
                    index_values = closest_n.index.values
                    similarities = closest_n.values
                closest[word] = list(zip(index_values, similarities))
        return closest
