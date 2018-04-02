from metaphor.utils import get_PoS


class Metaphor(object):

    def deconstruct(self, text, PoS):
        tagged = get_PoS(text, PoS=PoS)
        return tagged

    def create(self, *args):
        pass

    def reconstruct(self, *args):
        pass

    def metaphorize(self, text=None):
        pass