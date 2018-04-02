from metaphor.metaphor import Metaphor
from metaphor.settings import BASE_DIR
import os
import pickle
import random


class RandomMetaphor(Metaphor):

    def create(self):
        file_path = os.path.join(BASE_DIR, 'static/metaphors/metaphors.pkl')
        life_metaphors = pickle.load(open(file_path, "rb"), encoding='utf-8')
        return life_metaphors[random.randint(1, len(life_metaphors) - 1)]

    def metaphorize(self, text=None):
        return self.create()
