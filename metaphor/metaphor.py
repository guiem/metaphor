from metaphor.utils import get_PoS
import language_check
import abc


class Metaphor(object):

    @staticmethod
    def _correct_grammar(metaphor, lang='en-US'):
        tool = language_check.LanguageTool(lang)
        matches = tool.check(metaphor)
        return language_check.correct(metaphor, matches) + " ### " + metaphor

    def _deconstruct(self, text, PoS):
        tagged = get_PoS(text, PoS=PoS)
        return tagged

    @abc.abstractmethod
    def _create(self, *args):
        """The creative part of metaphor creation. Here is where magical analogies happen!"""

    @abc.abstractmethod
    def _reconstruct_core(self, *args):
        """The core of the sentence reconstruction, it hast to return a metaphor"""
        return

    def _reconstruct(self, correct, *args):
        metaphor = self._reconstruct_core(*args)
        if correct:
            return self._correct_grammar(metaphor)
        return metaphor

    @abc.abstractmethod
    def metaphorize(self, text=None, **kwargs):
        """All together: usually one wants to 'deconstruct' first, 'create' and put all together with 'reconstruct'"""
