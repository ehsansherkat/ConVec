# -*- coding: utf-8 -*-
"""
@summary The goal of this code is to add new anchors to Wikipedia in which there is at least one existing anchor of the
kind in the page. For example it will add 'data mining' to the page if the 'data mining' anchor exist in a page. The anchor
disambiguation will be the one that has been anchord by Wikipedia user.
@author Ehsan Sherkat
"""

import logging
import utility
import gc
import re
import unicodedata

Path = 'Wikipedia/pages/'
WikipediaCleanPath = "pagesTextCleanAnchorID.txt"
surface_hash = {} # surface hash
ID_Title_Pruned_Path = "ID_Title_Map_Pruned.csv"
ID_Title_Pruned = {} # ID tittle hashmap
indegree = {} # in degree hashmap
pagesTextCleanAnchorID_title_extend = list() # clean text of Wikipedia pages by anchorID replaced and title added
wiki_index = list() # index of pages
WikipediaCleanPath_index = "pagesTextCleanAnchorID_Index.txt"

min_degree = 100 # pages with less thant min indegree need anchor
max_hitnumber = 10 # at most 10 new anchor for each candidate should be exists (skip common concepts)
max_hitnumber_title = 50 # at most 50 new anchor will be added as a page title

# setup logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def extend():
    """
    The goal of this code is to add new anchors to Wikipedia in which there is at least one existing anchor of the
    kind in the page. For example it will add 'data mining' to the page if the 'data mining' anchor exist in a page. The anchor
    disambiguation will be the one that has been anchord by Wikipedia user.
    @return: number of added anchors
    """
    # read ID title map hashmap
    logging.info('Start reading ID_title_map_pruned...')
    ID_Title_Pruned_File = open(ID_Title_Pruned_Path, 'r')
    for title in ID_Title_Pruned_File:
        key = title[title.index(':') + 1:title.index(',')]
        value = title[title.index(',') + 1:title.index('\r\n')]
        ID_Title_Pruned[key] = value
    ID_Title_Pruned_File.close()
    logging.info('ID_title map_pruned read successfully.')

    # read wikipedia index file
    logging.info('Start reading Wikipedia index...')
    wiki_index_file = open(Path + WikipediaCleanPath_index, 'r')
    for index in wiki_index_file:
        wiki_index.append(index.replace('\r','').replace('\n',''))
    wiki_index_file.close()
    logging.info('Wikipedia index read successfully.')

    #read indegree hashmap
    logging.info('Start reading inDegree...')
    indegree_File = open(Path + 'inlinkGraphDegree.csv', 'r')
    for node in indegree_File:
        node = node.replace('\r','').replace('\n','')
        key = node[0:node.index(',')]
        value = node[node.index(',') + 1:]
        indegree[key] = value
    indegree_File.close()
    logging.info('inDegree read successfully.')

    logging.info('Start garbage collection')
    gc.collect()  # garbage collector
    logging.info('Garbage collection finished successfully.')

    # read clean Wikipedia dataset
    index = 0
    anchorCount = 0
    flushIndex = 0
    for page in open(Path + WikipediaCleanPath):
        tokens = page.split(' ')

        candidates = {} # candidate anchors
        for token in tokens:
            if token.isdigit():#if it is anchor
                if indegree.has_key(token):
                    if int(indegree[token]) < min_degree:
                        key = processText(ID_Title_Pruned[token])
                        candidates[key] = token

        # add page title to the candidates
        pageID = wiki_index[index]
        if indegree.has_key(pageID):
            if int(indegree[pageID]) < min_degree:
                candidates[processText(ID_Title_Pruned[pageID])] = pageID

        # sort candidates based on length (longest is in the top)
        for candide in sorted(candidates, key=len, reverse=True):
            hitNumber = len(re.findall(r'\b%s\b' % candide, page))

            # for the page title
            if candidates[candide] == pageID:
                if hitNumber > 0 and hitNumber < max_hitnumber_title:
                    anchorCount += hitNumber
                    page = re.sub(r'\b%s\b' % candide, candidates[candide], page)  # word boundary

            if hitNumber < max_hitnumber and hitNumber > 0:
                anchorCount += hitNumber
                page = re.sub(r'\b%s\b' % candide, candidates[candide], page)  # word boundary

        pagesTextCleanAnchorID_title_extend.append(page)

        flushIndex += 1
        if flushIndex % 1000000 == 0:
            flushIndex = 0
            writeOutputToFile()
            del pagesTextCleanAnchorID_title_extend[:]
            logging.info('1000000 pages wrote on file successfully.')

        index += 1
        if index % 10000 == 0:
            progress = (float(index) / len(wiki_index)) * 100
            progress = round(progress, 2)
            logging.info(str(index) + ' pages processed successfully. [' + str(progress) + '% progress]')

    writeOutputToFile() # write the rest
    progress = (float(index) / len(wiki_index)) * 100
    progress = round(progress, 2)
    logging.info(str(index) + ' pages processed successfully. [' + str(progress) + '% progress]')
    logging.info(str(anchorCount) + ' new anchors added to the corpus')
    return anchorCount

def writeOutputToFile():
    outputFile = open(Path + "pagesTextCleanAnchorID_tittle_extend.txt", "a")
    for value in pagesTextCleanAnchorID_title_extend:
        outputFile.write(value)
    outputFile.close()

def processText(text):
    """
    process the text as:
        1) lower case
        2) convert numbers to literal
        3) Convert to English27 char
        4) Remove punctuations
        5) Remove parenthesise
    @param text:
    @return:
    """
    text = text.lower()
    text = utility.numberToLiteral(text)
    text = utility.clean27English(text)
    text = unicodedata.normalize('NFKD', unicode(text, 'utf-8')).encode('ascii', 'ignore')
    text = re.sub(r'\(.*\)', '', text)
    text = text.strip()
    return text

extend()
