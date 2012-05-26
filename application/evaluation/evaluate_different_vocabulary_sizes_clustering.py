'''
Created on 21 Mar 2012

@author: george
'''
import random
import pylab#!@UnresolvedImport 
import numpy 

from database.warehouse import WarehouseServer
from database.model.tweets import *
from analysis.clustering.kmeans import OrangeKmeansClusterer
from analysis.clustering.dbscan import DBSCANClusterer
from analysis.clustering.nmf import NMFClusterer
from evaluation.evaluators import ClusteringEvaluator
from analysis.clustering.algorithms import euclidean 
from analysis.dataset_analysis import DatasetAnalyser
from analysis.text import TextAnalyser

####################HELPER METHODS###########################
def get_words_starting_with(letter):
    '''
    It returns all the words in the dictionary starting with "letter".
    '''
    words = []
    for word in open("/usr/share/dict/words"):
                    if word.startswith(letter):
                            words.append(word.rstrip())
    return words

def create_document(words, max_length=140):
    '''
    Given a list of available words this function creates a document 
    which has no more than "max_length" characters.
    '''
    document = ''

    while (len(document) < max_length):
        randint = random.randint(0, len(words)-1)
        randoccurences = random.randint(1, 4) #how many times will this word appear in the doc?
        new_word = words[randint]
        if len(document) + len(' ') + len(new_word)*randoccurences > 140: break 
        for i in range(randoccurences):
            document += ' ' + new_word
    return document

def create_dataset(words, N, word_max_length=140):
    '''
    It creates a document dataset which has N documents. It takes as input
    a list of words. 
    '''
    ta = TextAnalyser(ngram=1, only_english=True)
    documents = []
    i = 0
    while i < N:
        document = create_document(words=words, max_length=word_max_length)
        analysed = ta.add_document(document)
        t = CustomEvaluationTweet()
        content = Content()
        content.raw = analysed['raw']
        content.tokens = analysed['tokens']
        content.construct_word_freq_list(analysed['word_frequencies'])
        content.date = datetime.datetime.utcnow()
        t.content = content
        t.date = datetime.datetime.utcnow()
        t.author_screen_name = "It's an evaluation tweet"
        t.save()
        documents.append(t)
        i += 1 
    return documents
    
def pick_letters(N, with_replacement=False):
    '''
    Randomly selects a letter from the alphabet. N is the number of letters to be
    retrieved. If with_replacement is true then a letter can be selected more than once. 
    '''
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p' ,'q' ,'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    used = []
    i = 0
    while i<N:
        if not with_replacement:
            letter = random.choice([x for x in alphabet if x not in used])
        else:
            letter = random.choice([x for x in alphabet])
        used.append(letter)
        i += 1 
    return used
        
        
#####################################MAIN SCRIPT############################################
ws = WarehouseServer()
clusterers = [OrangeKmeansClusterer(k=39, ngram=1)] 
              #DBSCANClusterer(epsilon=0.02, min_pts=3, distance=euclidean), 
              #NMFClusterer(rank=39, max_iter=65, display_N_tokens = 5, display_N_documents = 10)] 


f_measures = []

diversity = [1, 2, 13, 26]#How many different letters to pick from the alphabet each time
datasets = []

for d in diversity:
    letters = pick_letters(d)
    words = []
    for letter in letters:
        words += get_words_starting_with(letter)
    dataset = create_dataset(words, 250)
    datasets.append(dataset)

for clusterer in clusterers:
    oc = clusterer
    i = 0
    for dataset in datasets:
        oc.add_documents(dataset)
        oc.run()
        oc.dump_clusters_to_file("vocabulary_tests" + str(i))
        i += 1
    