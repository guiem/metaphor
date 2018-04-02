from metaphor.metaphor import Metaphor
from metaphor.random_metaphor import RandomMetaphor
from metaphor.models import Dictionary
from metaphor.utils import get_random_connectors


class IsAMetaphor(Metaphor):

    def create(self, nouns_list):
        triplets = []
        for noun in nouns_list:
            adjective = Dictionary.objects.random(word_type='a.').word.lower()
            new_noun = Dictionary.objects.random().word.lower()
            triplets.append((noun, adjective, new_noun))
        return triplets

    def reconstruct(self, triplets):
        metaphors = []
        for noun, adjective, new_noun in triplets:
            a_adjective = 'n' if adjective.startswith(('a', 'e', 'i', 'o', 'u')) else ''
            metaphor = u"{} is a{} {} {}".format(noun.capitalize(), a_adjective, adjective, new_noun)
            metaphors.append(metaphor)
        connectors = get_random_connectors(len(metaphors))
        return ' '.join([j for i in zip(metaphors, connectors) for j in i][:-1]) + "."

    def metaphorize(self, text=None):
        nouns_tagged = self.deconstruct(text, PoS={'NOUN'})
        if not nouns_tagged:
            m = RandomMetaphor()
            return m.metaphorize()
        nouns_list = [n for n, tag in nouns_tagged]
        triplets = self.create(nouns_list)
        return self.reconstruct(triplets)
