"""
@summary This code will add the title of the page to the list of anchors if it exactly presented inside the page content.
The following preprossing will be down on the page title:
        1) lower case
        2) convert numbers to literal
        3) Remove info on the parentheses
        4) Convert to English27 char
        5) Remove punctuations
@author Ehsan Sherkat
"""

import gc
import logging
import utility
import re
import unicodedata

Path = '/media/ehsan/My Documents/Shared/Datasets/Wikipedia/pages/'
WikipediaCleanPath = "pagesTextCleanAnchorID.txt"
WikipediaCleanPath_index = "pagesTextCleanAnchorID_Index.txt"
ID_Title_Pruned_Path = "/media/ehsan/My Documents/Shared/Datasets/Wikipedia/pages/ID_Title_Map_Pruned.csv"
wiki_index = list() # index of pages
ID_Title_Pruned = {} # ID tittle hashmap
pagesTextCleanAnchorID_title = list() # clean text of Wikipedia pages by anchorID replaced and title added

# setup logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def addTittle():
    """
    add tittle of a page as an anchor
    @return: number of added anchors
    """
    # read wikipedia index file
    logging.info('Start reading Wikipedia index...')
    wiki_index_file = open(Path + WikipediaCleanPath_index, 'r')
    for index in wiki_index_file:
        wiki_index.append(index.replace('\r','').replace('\n',''))
    wiki_index_file.close()
    logging.info('Wikipedia index read successfully.')

    # read ID title map hashmap
    logging.info('Start reading ID_title_map_pruned...')
    ID_Title_Pruned_File = open(ID_Title_Pruned_Path, 'r')
    for title in ID_Title_Pruned_File:
        key = title[title.index(':') + 1:title.index(',')]
        value = title[title.index(',') + 1:title.index('\r\n')]
        ID_Title_Pruned[key] = value
    ID_Title_Pruned_File.close()
    logging.info('ID_title map_pruned read successfully.')

    logging.info('Start garbage collection')
    gc.collect()  # garbage collector
    logging.info('Garbage collection finished successfully.')

    # read clean Wikipedia dataset
    index = 0
    anchorCount = 0
    flushIndex = 0
    for page in open(Path + WikipediaCleanPath):
        tittleID = wiki_index[index]
        tittle = ID_Title_Pruned[tittleID]
        tittle = processTittle(tittle)
        hitNumber = len(re.findall(r'\b%s\b' % tittle, page))
        anchorCount += hitNumber

        if hitNumber > 0:
            page = re.sub(r'\b%s\b' % tittle, tittleID, page) # word boundary
        pagesTextCleanAnchorID_title.append(page)

        flushIndex += 1
        if flushIndex % 1000000 == 0:
            flushIndex = 0
            writeOutputToFile()
            del pagesTextCleanAnchorID_title[:]
            logging.info('1000000 pages wrote on file successfully.')

        index += 1
        if index % 100000 == 0:
            progress = (float(index) / len(wiki_index)) * 100
            progress = round(progress, 2)
            logging.info(str(index) + ' pages processed successfully. [' + str(progress) + '% progress]')

    writeOutputToFile() # write the rest
    progress = (float(index) / len(wiki_index)) * 100
    progress = round(progress, 2)
    logging.info(str(index) + ' pages processed successfully. [' + str(progress) + '% progress]')
    logging.info(str(anchorCount) + ' new anchors added to the corpus')
    return anchorCount

def processTittle(tittle):
    """
    process the tittle as:
        1) lower case
        2) convert numbers to literal
        3) Remove info on the parentheses
        4) Convert to English27 char
        5) Remove punctuations
    @param tittle:
    @return:
    """
    tittle = tittle.lower()
    tittle = utility.numberToLiteral(tittle)
    tittle = re.sub(r'\(.*\)', '', tittle)
    tittle = utility.clean27English(tittle)
    tittle = unicodedata.normalize('NFKD', unicode(tittle, 'utf-8')).encode('ascii', 'ignore')
    tittle = tittle.strip()

    return tittle

def writeOutputToFile():
    outputFile = open(Path + "pagesTextCleanAnchorID_tittle.txt", "a")
    for value in pagesTextCleanAnchorID_title:
        outputFile.write(value)
    outputFile.close()