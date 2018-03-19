from django.test import TestCase
from django.test.client import RequestFactory
from metaphor.utils import *
from metaphor.views import is_a_metaphor, random_metaphor, word2vec_substitution
from metaphor.ai.embeddings import Embeddings
from metaphor.settings import BASE_DIR
from metaphor.models import Dictionary
import pickle
import os
import time


def create_database():
    Dictionary.objects.create(word="unprecedented", word_type="a.")
    Dictionary.objects.create(word="cat", word_type="n.")


class ModelsTest(TestCase):
    
    def setUp(self):
        create_database()
    
    # ./manage.py test metaphor.tests.tests.ModelsTest.test_dictionary_random
    def test_dictionary_random(self):
        a = Dictionary.objects.random(word_type='n.').word.lower()
        self.assertEqual(a, "cat")


class ViewsTest(TestCase):
    
    def setUp(self):
        create_database()
    
    def test_is_a_metaphor(self):
        sentence = "Guiem is nice."
        is_a = is_a_metaphor(sentence)
        self.assertEqual(is_a, "Guiem is an unprecedented cat.")

    def test_random_metaphor(self):
        file_path = os.path.join(BASE_DIR, 'static/metaphors/metaphors.pkl')
        life_metaphors = pickle.load(open(file_path, "rb"), encoding='utf-8')
        res = random_metaphor()
        self.assertIn(res, life_metaphors)

    def test_word2vec_substitution(self):
        sentence = "I am a beautiful human being"
        emb_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
        metaphor = word2vec_substitution(sentence, num_neighbors=1, emb_info={'glove.6B.50d': {'path': emb_path, 'dim':
                                                                                                50}})
        self.assertEqual(metaphor, "I am a lovely animal being")


class UtilsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
    
    def test_get_random_connectors(self):
        for num_connectors in range(1, 10):
            connectors = get_random_connectors(num_connectors)
            self.assertEqual(len(connectors), num_connectors)
            for con in connectors:
                self.assertIn(con, CONNECTORS)
    
    def test_get_language_1(self):
        """
        Test on human rights declaration in different languages
        """
        percent_required = 0.95
        langs_to_test = ['en', 'es', 'it', 'dk', 'nl', 'fi', 'fr', 'de', 'hu', 'nn', 'pt', 'ru', 'sv', 'tr']
        langs_dict = {'en': 'English', 'es': 'Spanish', 'it': 'Italian', 'dk': 'Danish', 'nl': 'Dutch', 'fi': 'Finnish',
                      'fr': 'French', 'de': 'German', 'hu': 'Hungarian', 'nn': 'Norwegian', 'pt': 'Portuguese',
                      'ru': 'Russian', 'sv': 'Swedish', 'tr': 'Turkish'}
        res = {}
        total_ok = total_ko = 0
        for lang in os.listdir("{}/tests/lang_texts/".format(BASE_DIR)):
            if lang in langs_to_test:
                res[lang] = {'ok': 0, 'ko': 0}
                with open("{}/tests/lang_texts/{}/{}.txt".format(BASE_DIR, lang, lang), 'r') as f:
                    for line in f.readlines():
                        if line != '\n' and len(line.split()) > 2:  # we require more than two words in the sentence
                            text = line.replace("\n", "")
                            l = get_language(text)
                            if langs_dict[lang] in l:
                                res[lang]['ok'] += 1
                                total_ok += 1
                            else:
                                # print lang, text, l, len(line.split())
                                res[lang]['ko'] += 1
                                total_ko += 1
                # percent = res[lang]['ok'] / float(res[lang]['ok']+res[lang]['ko'])
                # self.assertGreaterEqual(percent,percent_required)
        total_percent = total_ok / float(total_ok + total_ko)
        # print "total percent",total_percent
        self.assertGreaterEqual(total_percent, percent_required)
        # print res

    def test_get_language_2(self):
        """
        Test on really simple examples. 
        """
        lang = get_language("Hola")
        self.assertEqual(lang, "NA")
        lang = get_language("House house house house")
        self.assertEqual(lang, "NA")
        lang = get_language("Sən mənim günəşimdir")
        self.assertEqual(lang, "Azerbaijani")
        lang = get_language("तिमी मेरो सुर्यको किरण हौ")
        self.assertEqual(lang, "Nepali")
        lang = get_language("Сен менің сәулемсің")
        self.assertEqual(lang, "Kazakh")
        lang = get_language("είσαι η ηλιαχτίδα μου")
        self.assertEqual(lang, "Greek")
        lang = get_language("Tú eres el sol de mi vida")
        self.assertEqual(lang, "Spanish")
        lang = get_language("أنت إشراقتي")
        self.assertEqual(lang, "Arabic")
        lang = get_language("Ты мое солнце")
        self.assertEqual(lang, "Russian")

    def test_get_client_ip(self):
        request = self.factory.get('/metaphorize')
        ip = get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')
        request.META = {'HTTP_X_FORWARDED_FOR': '69.69.69.69'}
        ip = get_client_ip(request)
        self.assertEqual(ip, '69.69.69.69')

    def test_most_frequent(self):
        most_freq = most_frequent(10)
        expected = ['not', 'when', 'other', 'new', 'time', 'so', 'only', 'then', 'now', 'more']
        self.assertEquals(sorted(expected), sorted(most_freq))
        most_freq = most_frequent(7, categories={'NOUN'})
        expected = ['time', 'man', 'af', 'years', 'way', 'people', 'mr.']
        self.assertEquals(sorted(expected), sorted(most_freq))
        most_freq = most_frequent(7, categories={'ADJ'})
        expected = ['new', 'such', 'more', 'many', 'other', 'own', 'first']
        self.assertEquals(sorted(expected), sorted(most_freq))


class AiTest(TestCase):

    def tearDown(self):
        pass

    def test_embeddings_singleton(self):
        file_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
        e1 = Embeddings('Embeddings', emb = {'glove.6B.50d': {'path': file_path, 'dim':50}})
        e2 = Embeddings('Embeddings')
        self.assertEqual(e1, e2)

    def test_embeddings_addition(self):
        file_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
        e = Embeddings('Embeddings')
        e.add_embeddings({'glove.6B.50d': {'path': file_path, 'dim':50}})
        self.assertNotEqual({}, e.embeddings)
        self.assertAlmostEqual(-0.388916, e.get_E().loc['house'][41], 3)

    def test_closest_n(self):
        file_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
        e = Embeddings('Embeddings', {'glove.6B.50d': {'path': file_path, 'dim':50}})
        closest_n = e.closest_n(['sun'], 5)
        self.assertEqual(closest_n['sun'][0][0], 'sky')
        self.assertAlmostEqual(closest_n['sun'][0][1], 0.6626, 3)
        self.assertEqual(closest_n['sun'][2][0], 'bright')
        self.assertAlmostEqual(closest_n['sun'][2][1], 0.6353, 3)

    def test_closest_n_modes(self):
        file_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
        e = Embeddings('Embeddings', {'glove.6B.50d': {'path': file_path, 'dim':50, 'similarities_dim': 2000}})
        if not e.similarities.get('glove.6B.50d'):
            e.add_embeddings(emb={'glove.6B.50d': {'similarities_dim': 2000}})
        words = ['sun', 'beautiful', 'ugly', 'mother']
        ping = time.time()
        closest_n = e.closest_n(words, 5)
        pong = time.time()
        closest_n = e.closest_n(words, 5, fast_desired=True)
        pongo = time.time()
        self.assertLess(pongo - pong, pong - ping)
