from django.test import TestCase
from django.test.client import RequestFactory
from django.http.response import Http404
from metaphor.views import *
from metaphor.random_metaphor import RandomMetaphor
from metaphor.is_a_metaphor import IsAMetaphor
from metaphor.w2v_subs import W2VSubs
from metaphor.metaphor import Metaphor as MetaphorClass
from metaphor.ai.embeddings import Embeddings
from metaphor.settings import BASE_DIR, GOOGLE_RECAPTCHA_SECRET_KEY, GOOGLE_RECAPTCHA_RESPONSE_TEST
from metaphor.models import Dictionary, Metaphor
import pickle
import os
import time


def create_database():
    Dictionary.objects.create(word="unprecedented", word_type="a.")
    Dictionary.objects.create(word="cat", word_type="n.")
    Metaphor.objects.create(upvotes=69, req_date=timezone.now())


class ModelsTest(TestCase):
    
    def setUp(self):
        create_database()
    
    # ./manage.py test metaphor.tests.tests.ModelsTest.test_dictionary_random
    def test_dictionary_random(self):
        a = Dictionary.objects.random(word_type='n.').word.lower()
        self.assertEqual(a, "cat")


class MetaphorTest(TestCase):

    def test_no_exception(self):
        m = MetaphorClass()
        m.create()
        m.reconstruct()
        m.metaphorize()

class RandomMetaphorTest(TestCase):

    def test_random_metaphor(self):
        file_path = os.path.join(BASE_DIR, 'static/metaphors/metaphors.pkl')
        life_metaphors = pickle.load(open(file_path, "rb"), encoding='utf-8')
        m = RandomMetaphor()
        res = m.metaphorize()
        self.assertIn(res, life_metaphors)


class IsAMetaphorTest(TestCase):

    def setUp(self):
        create_database()
        self.factory = RequestFactory()

    def test_is_a_metaphor(self):
        sentence = "Guiem is nice."
        m = IsAMetaphor()
        is_a = m.metaphorize(sentence)
        self.assertEqual(is_a, "Guiem is an unprecedented cat.")

    def test_is_a_metaphor_no_nouns(self):
        sentence = "this of the that for the those"
        m = IsAMetaphor()
        is_a = m.metaphorize(sentence)
        file_path = os.path.join(BASE_DIR, 'static/metaphors/metaphors.pkl')
        life_metaphors = pickle.load(open(file_path, "rb"), encoding='utf-8')
        self.assertIn(is_a, life_metaphors)


class W2VSubsTest(TestCase):

    def test_w2v_subs(self):
        sentence = "I am a beautiful human being"
        emb_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
        emb_info = {'glove.6B.50d': {'path': emb_path, 'dim': 50}}
        m = W2VSubs(emb_info)
        metaphor = m.metaphorize(sentence, num_neighbors=1)
        self.assertEqual(metaphor, "I am a lovely animal being")
        m.e.add_embeddings({'glove.6B.50d': {'sim_index': True}})
        metaphor = m.metaphorize(sentence, num_neighbors=1, fast_desired=True)
        self.assertEqual(metaphor, "I am a lovely animal being")
        m = W2VSubs()
        m.metaphorize(sentence, num_neighbors=1, fast_desired=1)
        self.assertEqual(metaphor, "I am a lovely animal being")

    def test_w2v_I(self):
        sentence = "i ate too much"
        m = W2VSubs()
        metaphor = m.metaphorize(sentence)
        print(metaphor)


class ViewsTest(TestCase):
    
    def setUp(self):
        create_database()
        self.factory = RequestFactory()

    def test_vote(self):
        class Messages(): # messages stub to pass tests
            def add(self, level, message, extra_tags):
                pass

        data = {
            'g-recaptcha-response': GOOGLE_RECAPTCHA_RESPONSE_TEST,
            'metaphor_id': 1,
            'direction': 'up',
        }
        request = self.factory.post('/vote', data=data)
        request._messages = Messages()
        vote(request, debug=True)
        metaphor = get_object_or_404(Metaphor, pk=1)
        self.assertEquals(70, metaphor.upvotes)
        self.assertEquals(70, metaphor.total_votes)
        data.update({'direction': 'down'})
        request = self.factory.post('/vote', data=data)
        request._messages = Messages()
        vote(request, debug=True)
        metaphor = get_object_or_404(Metaphor, pk=1)
        self.assertEquals(1, metaphor.downvotes)
        self.assertEquals(70, metaphor.upvotes)
        self.assertEquals(69, metaphor.total_votes)
        vote(request, debug=False)
        metaphor = get_object_or_404(Metaphor, pk=1)
        self.assertEquals(1, metaphor.downvotes)

    def test_metaphorize(self):
        data = {}
        request = self.factory.post('/metaphorize', data=data)
        metaphorize(request)
        with self.assertRaises(Http404):
            get_object_or_404(Metaphor, pk=2)
        data = {'sentence': 'I would love to get a nice metaphor', 'strategy': 'random'}
        request = self.factory.post('/metaphorize', data=data)
        metaphorize(request)
        metaphor = get_object_or_404(Metaphor, pk=2)
        self.assertEquals('I would love to get a nice metaphor', metaphor.sentence_text)
        data = {'sentence': 'I would love to get a nice metaphor', 'strategy': 'is_a-random'}
        request = self.factory.post('/metaphorize', data=data)
        metaphorize(request)
        metaphor = get_object_or_404(Metaphor, pk=3)
        self.assertEquals('I would love to get a nice metaphor', metaphor.sentence_text)
        data = {'sentence': 'I would love to get a nice metaphor', 'strategy': 'word2vec_subst'}
        request = self.factory.post('/metaphorize', data=data)
        metaphorize(request)
        metaphor = get_object_or_404(Metaphor, pk=4)
        self.assertEquals('I would love to get a nice metaphor', metaphor.sentence_text)
        data = {'sentence': 'I would love to get a nice metaphor', 'strategy': 'word2vec_subst_fast'}
        request = self.factory.post('/metaphorize', data=data)
        metaphorize(request)
        metaphor = get_object_or_404(Metaphor, pk=5)
        self.assertEquals('I would love to get a nice metaphor', metaphor.sentence_text)

    """
    def test_combine_words(self):
        file_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
        e = Embeddings('Embeddings', {'glove.6B.50d': {'path': file_path, 'dim': 50}})
        words = ['house', 'bright', 'sun']
        res = combine_words(words, e.get_E(), x=2)
    """

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

    def test_get_PoS(self):
        sentence_text = "This is where I'm standing, and I don't like it"
        words_tagged = get_PoS(sentence_text, PoS={'NOUN', 'ADJ', 'ADV'})
        self.assertEquals([('where', 'WRB'), ("n't", 'RB')], words_tagged)

    def test_PoS_I(self):
        sentence = "I ate too much"
        words_tagged = get_PoS(sentence, PoS={'NOUN', 'ADJ', 'ADV'})
        self.assertEqual(words_tagged, [('too', 'RB'), ('much', 'JJ')])
        sentence = "i ate too much"
        words_tagged = get_PoS(sentence, PoS={'NOUN', 'ADJ', 'ADV'})
        self.assertEqual(words_tagged, [('i', 'JJ'), ('too', 'RB'), ('much', 'JJ')])


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
        words = e.get_vectors(['sun'])
        closest_n = e.closest_n(words, 5)
        self.assertEqual(closest_n['sun'][0][0], 'sky')
        self.assertAlmostEqual(closest_n['sun'][0][1], 0.6626, 3)
        self.assertEqual(closest_n['sun'][2][0], 'bright')
        self.assertAlmostEqual(closest_n['sun'][2][1], 0.6353, 3)

    def test_closest_n_approximate_knn(self):
        file_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
        e = Embeddings('Embeddings', {'glove.6B.50d': {'path': file_path, 'sim_index': True}})
        words = e.get_vectors(['sun'])
        closest_n = e.closest_n(words, 5)
        self.assertEqual(closest_n['sun'][0][0], 'sky')
        self.assertAlmostEqual(closest_n['sun'][0][1], 0.6626, 3)
        self.assertEqual(closest_n['sun'][2][0], 'bright')
        self.assertAlmostEqual(closest_n['sun'][2][1], 0.6353, 3)

    def test_closest_n_modes(self):
        file_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.50d.txt')
        e = Embeddings('Embeddings', {'glove.6B.50d': {'path': file_path, 'dim':50, 'similarities_dim': 2000}})
        if not e.similarities.get('glove.6B.50d'):
            e.add_embeddings(emb={'glove.6B.50d': {'similarities_dim': 2000}})
        words = e.get_vectors(['sun', 'beautiful', 'ugly', 'mother'])
        ping = time.time()
        closest_n = e.closest_n(words, 5)
        pong = time.time()
        closest_n = e.closest_n(words, 5, fast_desired=True)
        pongo = time.time()
        self.assertLess(pongo - pong, pong - ping)


class StrategiesTest(TestCase):

    def test_word_combination(self):
        # Do the neighbours change according to a word context?
        # Result: Not enough
        d = 50
        file_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.{}d.txt'.format(d))
        e = Embeddings('Embeddings', {'glove.6B.50d': {'path': file_path, 'dim': d}})
        words_neg = ["man", "bad", "dirty"]
        words_pos = ["man", "good", "clean"]

        for x in range(2, 11):
            w1 = e.combine_words(words_neg, x=x)
            w2 = e.combine_words(words_pos, x=x)
            res1 = e.closest_n(w1, 5)
            res2 = e.closest_n(w2, 5)
            # print("x = {}. ".format(x), res1)
            # print("x = {}. ".format(x), res2)
            # print('----------------------------')

    def test_analogy_style(self):
        pass

    def test_neighbours_strategy(self):
        d = 50
        file_path = os.path.join(BASE_DIR, 'data/glove.6B/glove.6B.{}d.txt'.format(d))
        e = Embeddings('Embeddings', {'glove.6B.{}d'.format(d): {'path': file_path, 'dim': d, 'sim_index': True}})
        if not e.sim_index.get('glove.6B.50d'):
            e.add_embeddings(emb={'glove.6B.50d': {'sim_index': True}})
        E = e.get_E()
        words = ["war", "child", "mom", "ball", "astral", "eleven", "me", "tennis", "playful", "red"]
        words_vec = e.get_vectors(words)
        ping = time.time()
        res1 = e.closest_n(words_vec, 10, fast_desired=True)
        pong = time.time()
        res2 = e.closest_n(words_vec, 10, fast_desired=False)
        peng = time.time()
        self.assertLess(pong - ping, peng - pong)
        self.assertEquals(res1.keys(), res2.keys())
        for k, values in res1.items():
            in_count = 0
            words1, _ = zip(*values)
            words2, _ = zip(*res2[k])
            for w in words1:
                if w in words2:
                    in_count += 1
            self.assertGreaterEqual(in_count / len(words1), 0.9) # we request 90% similarity