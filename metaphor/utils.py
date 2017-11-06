from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import defaultdict

def get_language(text):
    score = defaultdict(int)
    words = word_tokenize(text.lower())
    stopwords.ensure_loaded
    stopwords_dict = {lang:stopwords.words(lang) for lang in stopwords.__dict__.get('_fileids')}
    for word in words:
        for lang,stop_list in stopwords_dict.iteritems():
            if word in stop_list:
                score[lang] += 1
    if score:
        max_value = max(score.values())
        max_keys = [k.capitalize() for k,val in score.iteritems() if val == max_value]
        return (' or ').join(max_keys)
    return 'English'