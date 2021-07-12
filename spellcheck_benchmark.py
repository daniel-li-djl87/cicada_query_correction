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

import time

start_time = time.time()
sym_spell = SymSpell()
sym_spell.create_dictionary("data/zoom_corpus.txt")
word_split = re.compile(r"[^\W]+", re.U)

def textblob_corrected_spellcheck(term):
    spell = SpellChecker()
    new_query = ""

    for word in term.split():
        typos = spell.unknown([word])
        if (len(typos) == 0):
            new_query += word + " "
        else:
            new_query += str(TextBlob(word).correct()) + " "
    new_query = new_query.strip().lower()
    return new_query

def pyspell_corrected_spellcheck(term):
    spell = SpellChecker()
    new_query = ""

    for word in term:
        typos = spell.unknown([word])
        if (len(typos) == 0):
            new_query += word + " "
        else:
            new_query += spell.correction(word) + " "
    new_query = new_query.strip().lower()
    return new_query

def symspell_corrected_spellcheck(term):
    suggestions = sym_spell.lookup_compound(
    term,
    max_edit_distance=2, # The maximum edit distance between input and suggested words.
    ignore_non_words=True, # numbers and acronyms are left alone
    ignore_term_with_digits=True # any term with digits is left alone
    )

    corrected = suggestions[0].term
    # This combined with split_phrase_by_space=True would be enough just to spell check
    # but punctuation is lost.

    # The spell check is already done in 'corrected'. Now we just want to keep the punctuation.
    in_list = word_split.findall(term)
    chk_list = word_split.findall(corrected)

    # To keep punctuation we take the original phrase and do word by word replacement
    out_term = term
    word_count = 0
    for word in in_list:
        out_term = out_term.replace(word, chk_list[word_count])
        word_count += 1
    return out_term

# 1.) Parse through json files to gather queries
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

queries = []

with open('data/correct_queries.txt') as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]
for item in content:
    queries.append([item, item, 'CC'])

with open('data/incorrect_queries.txt') as f:
    lines = f.readlines()
    for line in lines:
        temp = ''.join(line).split('@')
        queries.append([temp[0], temp[1], 'IC'])

# for dict in json_data:
#     for data in dict:
#         queries.append(data['query'])

# sym_spell = SymSpell()
# sym_spell.create_dictionary("data/zoom_corpus.txt")
# typos = []

# with open('data/queries.txt', 'w') as f:
#     for query in queries:
#         f.write("%s\n" % query.lower())

# 2.) Use NLP Aug to generate CC and IC queries in a list --> [from, to category]
# num_errors = 2
# query_categories = []

# for query in queries:

#     # Generate CC queries
#     query_categories.append([query.lower(), query.lower(), 'CC'])

#     # Generate IC queries
#     aug = nac.KeyboardAug()
#     keyboard_typo = aug.augment(query, n=num_errors)
#     for typo in keyboard_typo:
#         query_categories.append([typo.lower() ,query.lower(), 'IC'])

#     # Generate n number of spelling errored queries
#     aug = naw.SpellingAug()
#     spelling_typo = aug.augment(query, n=num_errors)
#     for typo in spelling_typo:
#         query_categories.append([typo.lower() ,query.lower(), 'IC'])

# print(query_categories)

# 3.) Loop through list of [from, to category] to calculate fp, fn, tn, tp, and precision, recall

fp = 0.0
fn = 0.0
tn = 0.0
tp = 0.0
not_fixed = 0

fp_list = []
fn_list = []
tn_list = []
tp_list = []
not_fixed_list = []

for query in queries:
    from_query = query[0].strip().lower()
    to_query = query[1].strip().lower()
    category = query[2]
    type = ""

    new_query = textblob_corrected_spellcheck(from_query)

    if (category == 'CC'):
        if (new_query == to_query): 
            type = "true negative"
            tn_list.append([from_query, new_query, to_query])
            tn += 1
        else:
            type = "false positive"
            fp_list.append([from_query, new_query, to_query])
            fp += 1
    else:
        if (new_query == to_query):
            type = "true positive"
            tp_list.append([from_query, new_query, to_query])
            tp += 1
        else:
            if (new_query == from_query):
                type = "false negative"
                fn_list.append([from_query, new_query, to_query])
                fn += 1
            else:
                type = "not_fixed"
                not_fixed_list.append([from_query, new_query, to_query])
                not_fixed += 1
    
print ("textblob took", time.time() - start_time, "to run")

with open('true_negatives.txt', 'w') as f:
    for item in tn_list:
        f.write("%s\n" % item)

with open('false_positives.txt', 'w') as f:
    for item in fp_list:
        f.write("%s\n" % item)

with open('true_positives.txt', 'w') as f:
    for item in tp_list:
        f.write("%s\n" % item)

with open('false_negatives.txt', 'w') as f:
    for item in fn_list:
        f.write("%s\n" % item)

with open('not_fixed_list.txt', 'w') as f:
    for item in not_fixed_list:
        f.write("%s\n" % item)

print("false positives: {}".format(fp))
print("false negatives: {}".format(fn))
print("true negatives: {}".format(tn))
print("true positives: {}".format(tp))
print("not fixed: {}".format(not_fixed))

# Thing with fn is that the error is found, but sometimes not always fixed
print("precision: {}".format(tp/(tp + fp)))
print("recall: {}".format(tp/(tp + fn)))

