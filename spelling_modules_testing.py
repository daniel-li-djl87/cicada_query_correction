
import nlpaug.augmenter.char as nac
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.sentence as nas
from collections import defaultdict
import json

import pkg_resources
from symspellpy import SymSpell, Verbosity
from spellchecker import SpellChecker
from textblob import TextBlob
import re

# 1.) parse json files
json_data = []
queries = []

# with open('data/asana_answer_quality_20210610.json', 'r') as f:
#     json_data.append(json.load(f))
# with open('data/asana_answer_quality_20210621.json', 'r') as f:
#     json_data.append(json.load(f))
# with open('data/asana_answer_quality.json', 'r') as f:
#     json_data.append(json.load(f))
# with open('data/zoom_faq.20210618.json', 'r') as f:
#     json_data.append(json.load(f))
# with open('data/zoom_faq.json', 'r') as f:
#     json_data.append(json.load(f))
# with open('data/temp.json', 'r') as f:
#     json_data.append(json.load(f))

for dict in json_data:
    for data in dict:
        queries.append(data['query'])

# 2.) Use NLP aug to alter queries
query_dict = {}
num_errors = 2

for query in queries:
    # Generate n number of keyboard errored queries
    aug = nac.KeyboardAug()
    keyboard_typo = aug.augment(query, n=num_errors)
    for typo in keyboard_typo:
        query_dict[typo] = query.lower()

    # Generate n number of spelling errored queries
    aug = naw.SpellingAug()
    spelling_typo = aug.augment(query, n=num_errors)
    for typo in spelling_typo:
        query_dict[typo] = query.lower()

# print(query_dict)

# 3.a) Use SymSpell to fix queries
sym_spell_correct = 0
sym_spell_corrections = []
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt")
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

for key, value in query_dict.items():
    suggestions = sym_spell.lookup_compound(key, max_edit_distance=2)
    new_query = suggestions[0]._term.lower()
    sym_spell_corrections.append(new_query)
    print("typo: {}, actual query: {}, corrected query: {}".format(key, value, new_query))
    if (new_query == value or new_query + '?' == value):
        sym_spell_correct += 1

print(sym_spell_correct/(len(query_dict)))

# 3.b) Use pyspellchecker to fix queries
spell = SpellChecker()
py_spell_correct = 0
py_spell_corrections = []

for key, value in query_dict.items():
    new_query = ""

    for word in key.split():
        typos = spell.unknown([word])
        if (len(typos) == 0):
            new_query += word + " "
        else:
            new_query += spell.correction(word) + " "
    new_query = new_query.strip().lower()
    py_spell_corrections.append(new_query)
    # print("typo: {}, actual query: {}, corrected query: {}".format(key, value, new_query))
    if (new_query == value or new_query + '?' == value):
        py_spell_correct += 1

print(py_spell_correct/(len(query_dict)))

# 3.c) Use Textblob to fix queries
spell = SpellChecker()
text_blob_correct = 0
text_blob_corrections = []

for key, value in query_dict.items():
    new_query = ""

    for word in key.split():
        typos = spell.unknown([word])
        if (len(typos) == 0):
            new_query += word + " "
        else:
            new_query += str(TextBlob(word).correct()) + " "
    new_query = new_query.strip().lower()
    text_blob_corrections.append(new_query)
    # print("typo: {}, actual query: {}, corrected query: {}".format(key, value, new_query))
    if (new_query == value or new_query + '?' == value):
        text_blob_correct += 1

print(text_blob_correct/(len(query_dict)))


