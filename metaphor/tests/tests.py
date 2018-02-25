from django.test import TestCase
from django.test.client import RequestFactory
from metaphor.utils import get_random_connectors
from metaphor.utils import get_language
from metaphor.utils import get_client_ip
from metaphor.utils import CONNECTORS
from metaphor.views import is_a_metaphor, random_metaphor
from metaphor.settings import BASE_DIR
from metaphor.models import Dictionary
import pickle
import os


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
