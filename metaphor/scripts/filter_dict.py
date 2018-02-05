import pandas as pd
import pickle,os
from metaphor.models import Dictionary
from metaphor.settings import BASE_DIR

file_path = os.path.join(BASE_DIR,'static/dicts/bragitoff_dict.csv')
df = pd.read_csv(file_path,names=['word','type','definition'])

nouns = df[df.type=='n.']['word'].tolist()
adjectives = df[df.type=='a.']['word'].tolist()

for noun in nouns:
    word = Dictionary(word=noun,word_type='n.',definition='')
    word.save()
    
for adjective in adjectives:
    word = Dictionary(word=adjective,word_type='a.',definition='')
    word.save()

#save_path = '../static/dicts/words.pkl'
#pickle.dump((nouns,adjectives), open(save_path, "wb" ) )


