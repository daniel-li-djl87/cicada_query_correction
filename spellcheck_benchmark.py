import nlpaug.augmenter.char as nac
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.sentence as nas
from collections import defaultdict
import json
import ast

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

# 1.) Parse through files to gather queries
json_data = []
queries = []

with open('zoom_baseline_queries.txt') as f:
    lines = f.readlines()
    content = [x.strip() for x in lines]

for line in content:
    x = ast.literal_eval(line)
    x = [n.strip() for n in x]

    queries.append(x)


# 2.) Loop through list of [from, to category] to calculate fp, fn, tn, tp, and precision, recall
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

    new_query = symspell_corrected_spellcheck(from_query)

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
    
print ("symspell took", time.time() - start_time, "to run")

# 3.) Write to text files and output number fn, fp, tn, tp, not_fixed, precision, recall
with open('data/true_negatives.txt', 'w') as f:
    for item in tn_list:
        f.write("%s\n" % item)

with open('data/false_positives.txt', 'w') as f:
    for item in fp_list:
        f.write("%s\n" % item)

with open('data/true_positives.txt', 'w') as f:
    for item in tp_list:
        f.write("%s\n" % item)

with open('data/false_negatives.txt', 'w') as f:
    for item in fn_list:
        f.write("%s\n" % item)

with open('data/not_fixed_list.txt', 'w') as f:
    for item in not_fixed_list:
        f.write("%s\n" % item)

print("false positives: {}".format(fp))
print("false negatives: {}".format(fn))
print("true negatives: {}".format(tn))
print("true positives: {}".format(tp))
print("not fixed: {}".format(not_fixed))
print("precision: {}".format(tp/(tp + fp)))
print("recall: {}".format(tp/(tp + fn)))

