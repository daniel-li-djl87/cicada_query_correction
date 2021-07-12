import pkg_resources
import json
from symspellpy import SymSpell, Verbosity

# 1.) Extract text elements from webcorpus json and write to txt file
corpus_data = []
corpus_text = "" 

with open('data/webcorpus_zoom_webs_v2.json', 'r') as f:
    corpus_data.append(json.load(f))

for dict in corpus_data:
    for data in dict:
        corpus_text = corpus_text + data['text'].strip('\n')

with open("data/zoom_corpus.txt", "w") as text_file:
    text_file.write(corpus_text)

# 2.) Process corpus.txt and convert into dict
sym_spell = SymSpell()
sym_spell.create_dictionary("data/zoom_corpus.txt")

# 3.) Check for typos using sym spell dict 
input_term = "zom zm ZOoM zoooom"
for word in input_term:
    suggestions = sym_spell.lookup_compound(input_term, max_edit_distance=2)
# display suggestion term, term frequency, and edit distance
for suggestion in suggestions:
    print(suggestion._term)
