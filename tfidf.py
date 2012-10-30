#!/usr/bin/env python
# encoding: utf-8

"""
File: tfidf.py
Author: Yasser Ebrahim
Date: Oct 2012

Generate the TF-IDF ratings for a collection of documents.

This script will also tokenize the input files to extract words (removes punctuation and puts all in
    lower case), and it will use the NLTK library to lemmatize words (get rid of stemmings)

IMPORTANT:
    A REQUIRED library for this script is NLTK, please make sure it's installed along with the wordnet
    corpus before trying to run this script

Usage:
    - Create a file to hold the paths+names of all your documents (in the example shown: input_files.txt)
    - Make sure you have the full paths to the files listed in the file above each on a separate line
    - For now, the documents are only collections of text, no HTML, XML, RDF, or any other format
    - Simply run this script file with your input file as a single parameter, for example:
            python tfidf.py input_files.txt
    - This script will generate new files, one for each of the input files, with the suffix "_tfidf"
            which contains terms with corresponding tfidf score, each on a separate line

"""

import sys, re, math
from nltk.stem.wordnet import WordNetLemmatizer
from optparse import OptionParser

# a list of (words-freq) pairs for each document
global_terms_in_doc = {}
# list to hold occurrences of terms across documents
global_term_freq    = {}
num_docs            = 0
foreign_lang        = False
lang_dictionary     = {}
print('initializing..')

# support for custom language if needed
def loadLanguageLemmas(filePath):
    print('loading language from file: ' + filePath)
    f = open(filePath)
    for line in f:
        words = line.split()
        if words[1] == '=' or words[0] == words[1]:
            continue
        lang_dictionary[words[0]] = words[1]
    global foreign_lang
    foreign_lang = True

# function to tokenize text, and put words back to their roots
def tokenize(text):

    # remove punctuation
    if foreign_lang:
        from nltk.tokenize.punkt import PunktWordTokenizer
        tokens = PunktWordTokenizer().tokenize(text)
    else:
        tokens = re.findall(r"<a.*?/a>|<[^\>]*>|[\w'@#]+", text.lower())

    # lemmatize words. try both noun and verb lemmatizations
    lmtzr = WordNetLemmatizer()
    for i in range(0,len(tokens)):
        tokens[i] = tokens[i].strip("'")
        if foreign_lang:
            if tokens[i] in lang_dictionary:
                tokens[i] = lang_dictionary[tokens[i]]
        else:
            res = lmtzr.lemmatize(tokens[i])
            if res == tokens[i]:
                tokens[i] = lmtzr.lemmatize(tokens[i], 'v')
            else:
                tokens[i] = res
    
    # don't return any single letters
    tokens = [i for i in tokens if len(i) > 1]
    return tokens

# __main__ execution

parser = OptionParser(usage='usage: %prog [options] input_file')
parser.add_option('-l', '--language_file', dest='language',
        help='Foreign language lexical file. This file should map\
                words to their lemmas', metavar='LANGUAGE_FILE')
(options, args) = parser.parse_args()

if options.language:
    loadLanguageLemmas(options.language)

if not args:
    parser.print_help()
    quit()

reader = open(args[0])
all_files = reader.read().splitlines()

num_docs  = len(all_files)

for f in all_files:
    
    # local term frequency map
    terms_in_doc = {}
    
    file_reader  = open(f)
    doc_words    = tokenize(file_reader.read())
    
    # increment local count
    for word in doc_words:
        if word in terms_in_doc:
            terms_in_doc[word] += 1
        else:
            terms_in_doc[word]  = 1

    # increment global frequency
    for (word,freq) in terms_in_doc.items():
        if word in global_term_freq:
            global_term_freq[word] += 1
        else:
            global_term_freq[word]  = 1

    global_terms_in_doc[f] = terms_in_doc

for f in all_files:

    writer = open(f + '_tfidf', 'w')
    result = []
    # iterate over terms in f, calculate their tf-idf, put in new list
    for (term,freq) in global_terms_in_doc[f].items():
        idf = math.log(float(1 + num_docs) / float(1 + global_term_freq[term]))
        tfidf = freq * idf
        result.append([tfidf, term])

    # sort result on tfidf and write them in descending order
    result = sorted(result, reverse=True)
    for (tfidf, term) in result:
        writer.write(term + '\t' + str(tfidf) + '\n')

print('success, with ' + str(num_docs) + ' documents.')
