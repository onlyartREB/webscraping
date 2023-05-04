import json
import glob
import os
import nltk
import spacy


nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

path_to_json = 'DATASET/JSONfrench/'
result = []
for file_name in [file for file in os.listdir(path_to_json)
if file.endswith('.json')]:
#for f in glob.glob("*.json"):
    with open(path_to_json + file_name, "rb") as infile:
        result.append(json.load(infile))

with open("DATASET.json", "wb") as outfile:
     json.dump(result, outfile)


nlp=spacy.load('fr_core_news_md')