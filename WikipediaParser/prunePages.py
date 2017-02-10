"""
@summary This code will remove following pages from Wikipedia dataset (The list is based on the following link: https://en.wikipedia.org/wiki/Special:Export/FULLPAGENAME):
    1) Redirect:            They have '<ns0:redirect>' tag in their xml file.
    2) Category:            There is 'Category:' in the first part of age name
    3) File:                There is 'File:' in the first part of page name
    4) Template:            There is 'Template:' in the first part of page name
    5) Disambiguation:      Some of them have '(disambiguation)' in their page name. Some have 'may refer to:' or 'may also refer to' in their text file.
    6) Portal:              There is 'Portal:' in the first part of page name
   *7) SmallPage:           Pages that have incoming links lower than the threshold. Word2Vec used 5 for the threshold. (Not implemented here see getText.py)
   *8) NoneEnglishTitle:    If it is not redirect and there is no alias remove it. If there is alias put the English one as the main alias. (Not yet implemented)
    9) Draft:               There is 'Draft:' in the first part of page name
   10) MediaWiki:           There is 'MediaWiki:' in the first part of page name
   11) ListPage:            There is 'List of' in the first part of the page name
   12) Wikipedia:           There is 'Wikipedia: in the first part of page name
   13) TimedText:           There is 'TimedText:' in the first part of page name
   14) Help:                There is 'Help:' in the first part of page name
   15) Book:                There is 'Book:' in the first part of page name
   16) Module:              There is 'Module:' in the first part of page name
   17) Topic:               There is 'Topic:' in the first part of page name
@author Ehsan Sherkat
"""

import logging
import re
from xml.dom import minidom
from collections import defaultdict

Path = 'Wikipedia/pages/' # where to save result and where the pages are
ID_TitlePath = "id_title_map.csv" # The path to the ID Title Map file
ID_Title_Map_Pruned = list() # The pruned list of pages
ID_Type_Map = list() # The type of the page (redirect, category, file, template, ...)
redirectDic = defaultdict(list) # dictionary of redirects

# setup logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def isRedirect(key):
    """
    Check if the page is redirect. If it is redirect add it to redirect dictionary.
    @param key:
    @return: True if it is redirect
    """

    folderName = key[0:key.index(":")]
    fileName = key[key.index(":")+1:]
    filePath = Path + folderName + "/" + fileName + '.xml'

    xmlFile = open(filePath, 'r')
    page = minidom.parse(xmlFile)
    xmlFile.close()

    redirect = page.getElementsByTagName('ns0:redirect')

    if redirect:
        for re in redirect:
            reDirectTo = re.getAttribute('title')
            pageTitle = page.getElementsByTagName('ns0:title')[0].firstChild.nodeValue
            redirectDic[reDirectTo].append(pageTitle)

        return True

    return False

def isDisambiguation(key):
    return True

# Read ID Title Map
index = 0
logging.info('Start Processing ID_Title_Map ...')
ID_Title_File = open(ID_TitlePath, 'r')
for line in ID_Title_File:
    key = line[0:line.index(',')]
    value = line[line.index(',')+1:line.index('\r\n')]

    index += 1
    if index % 50000 == 0:
        logging.info(str(index) + ' pages processed successfully.')

    if re.match('^Category:.*', value):
        ID_Type_Map.append(key + ",Category")
    elif re.match('^File:.*', value):
        ID_Type_Map.append(key + ",File")
    elif re.match('^Template:.*', value):
        ID_Type_Map.append(key + ",Template")
    elif re.match('^Wikipedia:.*', value):
        ID_Type_Map.append(key + ",Wikipedia")
    elif re.match('^MediaWiki:.*', value):
        ID_Type_Map.append(key + ",MediaWiki")
    elif re.match('^Portal:.*', value):
        ID_Type_Map.append(key + ",Portal")
    elif re.match('^Draft:.*', value):
        ID_Type_Map.append(key + ",Draft")
    elif re.match('^List of .*', value):
        ID_Type_Map.append(key + ",ListPage")
    elif re.match('^TimedText:.*', value):
        ID_Type_Map.append(key + ",TimedText")
    elif re.match('^Help:.*', value):
        ID_Type_Map.append(key + ",Help")
    elif re.match('^Book:.*', value):
        ID_Type_Map.append(key + ",Book")
    elif re.match('^Module:.*', value):
        ID_Type_Map.append(key + ",Module")
    elif re.match('^Topic:.*', value):
        ID_Type_Map.append(key + ",Topic")
    elif re.match('.*(disambiguation)', value):
        ID_Type_Map.append(key + ",Disambiguation")
    elif isRedirect(key):
        ID_Type_Map.append(key + ",Redirect")
    # elif isDisambiguation(key):
    #     ID_Type_Map.append(key + ",Disambiguation")
    else:
        ID_Type_Map.append(key + ",Page")
        ID_Title_Map_Pruned.append(key+","+value)

logging.info('ID_Title_Map processed successfully.')

#write id_title_map on a file
outputFile = open(Path + "ID_Title_Map_Pruned.csv", "w")
for val in ID_Title_Map_Pruned:
    outputFile.write(val + '\r\n')
outputFile.close()
logging.info('Pruned pages are saved in: ID_Title_Map_Pruned.csv')

#write ID_Type_Map on a file
outputFile = open(Path + "ID_Type_Map.csv", "w")
for val in ID_Type_Map:
    outputFile.write(val + '\r\n')
outputFile.close()
logging.info('Pruned pages are saved in: ID_Type_Map.csv')

#write redirectDic on a file
outputFile = open(Path + "redirectDictionary.csv", "w")
for key, value in redirectDic.iteritems():
    outputFile.write(key.encode("utf-8"))
    for va in value:
        outputFile.write('@@'+va.encode("utf-8"))
    outputFile.write('\r\n')
outputFile.close()
logging.info('Pruned pages are saved in: redirectDictionary.csv')
