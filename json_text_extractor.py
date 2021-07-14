import pkg_resources
from symspellpy import SymSpell, Verbosity
from spellchecker import SpellChecker
from textblob import TextBlob
import re
import json

# 1.) parse json files
data = []

with open('data/webcorpus_zoom_webs_v2.json', 'r') as f:
    json_data = json.load(f)

for dict in json_data:
    for key, value in dict.items():
        if key == 'text':
            data.append(value)
        elif key == 'title':
            data.append(value)

with open ('zoom_corpus_3.txt', 'w') as f:
    for item in data:
        f.write("%s\n" % item)