import pandas as pd
import pickle

file_path = '../static/dicts/bragitoff_dict.csv'
df = pd.read_csv(file_path,names=['word','type','definition'])

nouns = df[df.type=='n.']['word'].tolist()
adjectives = df[df.type=='a.']['word'].tolist()

save_path = '../static/dicts/words.pkl'
pickle.dump((nouns,adjectives), open(save_path, "wb" ) )


