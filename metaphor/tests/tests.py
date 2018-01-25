from django.test import TestCase
from metaphor.utils import get_random_connectors
from metaphor.utils import get_language
from metaphor.utils import CONNECTORS
from metaphor.settings import BASE_DIR
import os

class UtilsTest(TestCase):
    
    # ./manage.py test metaphor.tests.tests.UtilsTest.test_get_random_connectors
    def test_get_random_connectors(self):
        for num_connectors in range(1,10):
            connectors = get_random_connectors(num_connectors)
            self.assertEqual(len(connectors),num_connectors)
            for con in connectors:
                self.assertIn(con,CONNECTORS)
    
    # ./manage.py test metaphor.tests.tests.UtilsTest.test_get_language_1
    def test_get_language_1(self):
        """
        Test on human rights declaration in different languages
        """
        percent_required = 0.95
        langs_to_test = ['en','es','it','dk','nl','fi','fr','de','hu','nn','pt','ru','sv','tr']
        langs_dict = {'en':'English','es':'Spanish','it':'Italian','dk':'Danish','nl':'Dutch','fi':'Finnish','fr':'French','de':'German','hu':'Hungarian'
            ,'nn':'Norwegian','pt':'Portuguese','ru':'Russian','sv':'Swedish','tr':'Turkish'}
        res = {}
        total_ok = total_ko = 0
        for lang in os.listdir("{}/metaphor/tests/lang_texts/".format(BASE_DIR)):
            if lang in langs_to_test:
                res[lang] = {'ok':0,'ko':0}
                with open("{}/metaphor/tests/lang_texts/{}/{}.txt".format(BASE_DIR,lang,lang), 'r') as f:
                    for line in f.readlines():
                        if line != '\n' and len(line.split()) > 2: # we require more than two words in the sentence
                            text = line.replace("\n","").decode('utf-8')
                            l = get_language(text)
                            if langs_dict[lang] in l:
                                res[lang]['ok'] += 1
                                total_ok += 1
                            else:
                                #print lang, text, l, len(line.split())
                                res[lang]['ko'] += 1
                                total_ko += 1
                percent = res[lang]['ok'] / float(res[lang]['ok']+res[lang]['ko'])
                #self.assertGreaterEqual(percent,percent_required)
        total_percent = total_ok / float(total_ok + total_ko)
        #print "total percent",total_percent
        self.assertGreaterEqual(total_percent,percent_required)
        #print res

    # ./manage.py test metaphor.tests.tests.UtilsTest.test_get_language_2
    def test_get_language_2(self):
        """
        Test on really simple examples. 
        """
        lang = get_language("Hola")
        self.assertEqual(lang,"NA")
        lang = get_language("El sol de la vida")
        self.assertEqual(lang,"Spanish")
        lang = get_language("House house house house")
        self.assertEqual(lang,"NA")