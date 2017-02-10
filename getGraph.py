# -*- coding: utf-8 -*-
"""
@summary This code will extract these information from Wikipedia page:
            1) inlink,
            2) outlink,
            3) inlinkDegree,
            4) outlinkDegree,
            5) surfaceForms,
            6) heads,
            7) infobox,
            8) category of Wikipedia pages
@author Ehsan Sherkat
"""

import WikiExtractor
import logging
import utility
from collections import defaultdict
from xml.dom import minidom

ID_TitlePath = "pages/id_title_map.csv" # The path to the ID Title Map file
ID_TitlePath_Pruned = "ID_Title_Map_Pruned.csv" # The path to the ID Title Map pruned file
ID_Title_Path_All = "id_title_map.csv"
ID_Title_Map_Pruned = {} # The pruned hashmap of pages
Title_ID_Map_All = {} # All wikipedia pages
Path = 'Wikipedia/pages/' # where to save result and where the pages are
redirectHashmapPath = "/pages/redirectHashmap.csv"
redirectHashmap = {}
file_list = list() # list of the path of the pages
inlinkGraph = defaultdict(list) # dictionary of in links of a page
inlinkGraphDegree = {} # hashmap for size of in links degree of a page
outlinkGraph = defaultdict(list) # dictionary of in links of a page
outlinkGraphDegree = {} # hashmap for size of out links degree of a page
surfaceDictionary = defaultdict(list) # surface dictionary
infoboxList = {} # infobox dictionary
headDictionary = defaultdict(list) # head dictionary
categoryDictionary = defaultdict(list) # head dictionary

# setup logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Create redirect dictionary (NOTE: run it only if redirectHashmap does not exists)
# utility.redirectHashmap(redirectDictionaryPath, ID_TitlePath, Path)

# Read redirectHashmap
redirectHashmap_file = open(redirectHashmapPath, 'r')
logging.info('Start reading redirect Hashmap...')
for line in redirectHashmap_file:
    if line > 0:
        key = line[0:line.index(',')]
        value = line[line.index(',')+1:line.index('\r\n')]
        redirectHashmap[key] = value
logging.info('redirect Hashmap read successfully.')

#read id title map pruned list
ID_Title_File = open(ID_TitlePath_Pruned, 'r')
logging.info('Start reading ID Title map...')
for line in ID_Title_File:
    key = line[line.index(':')+1:line.index(',')]
    value = line[line.index(',')+1:line.index('\r\n')]

    ID_Title_Map_Pruned[key] = value
    file_name = line[0:line.index(',')].replace(':', '/')
    file_list.append(file_name)
logging.info('ID Title map read successfully.')

#read id title map all list
ID_Title_File_All = open(ID_Title_Path_All, 'r')
logging.info('Start reading ID Title map (All)...')
for line in ID_Title_File_All:
    key = line[line.index(':')+1:line.index(',')]
    value = line[line.index(',')+1:line.index('\r\n')]
    Title_ID_Map_All[value] = key
logging.info('ID Title map (all) read successfully.')

def addInLink(source, target):
    """
    add in links of page
    @param source: node
    @param target: The in link node
    @return:
    """
    if inlinkGraph.has_key(source):
       # if target not in inlinkGraph[source]:# uncomment to remove repetitives
        inlinkGraph[source].append(target)
        inlinkGraphDegree[source] = inlinkGraphDegree[source] + 1
    else:
        inlinkGraph[source].append(target)
        inlinkGraphDegree[source] = 1

def addOutLink(source, target):
    """
    add out links of page
    @param source: The node
    @param target: The out link node
    @return:
    """
    if outlinkGraph.has_key(source):
        # if target not in outlinkGraph[source]: # uncomment to remove repetitives
        outlinkGraph[source].append(target)
        outlinkGraphDegree[source] = outlinkGraphDegree[source] + 1
    else:
        outlinkGraph[source].append(target)
        outlinkGraphDegree[source] = 1

index = 0
logging.info('Start Processing pages ...')
# Create inlink and outlink graph
for file_name in file_list:
    index += 1

    file = open(Path + file_name + ".xml", 'r')
    page_ID = file_name[file_name.index('/')+1:]
    page = minidom.parse(file)
    file.close()

    if index % 20000 == 0:
        progress = (float(index) / len(file_list))*100
        progress = round(progress, 2)
        logging.info(str(index) + ' pages processed successfully. ['+str(progress)+'% progress]' )

    pageText = page.getElementsByTagName('ns0:text')[0].firstChild.nodeValue

    # extract infobox
    infobox = utility.extractInfobox(pageText)
    if infobox != "":
        infoboxList[page_ID] = infobox

    # extract heads
    headings = utility.extractHeads(pageText)
    for head in headings:
        head = head.replace('=', '').strip()
        headDictionary[page_ID].append(head)

    # extract category
    categories = utility.extractCategory(pageText)
    for cat in categories:
        categoryDictionary[page_ID].append(cat)

    anchors, anchorSurfaces = WikiExtractor.getAnchor(pageText)

    #create surface dictionary
    for anchorSurface in anchorSurfaces:
        anchorSurface = anchorSurface.replace('\n', '').replace('\r', '')
        temp = anchorSurface.split("@@")
        surface = temp[1]
        anchor = temp[0]

        #change encoding
        anchor = anchor.encode("utf-8")
        #capitalize the first letter
        anchor = anchor[0:1].capitalize() + anchor[1:]
        # remove # sign
        if '#' in anchor:
            anchor = anchor[0:anchor.index('#')]

        anchor_id = None

        # Normalize the anchor id (if it is redirect put the main title on it)
        if Title_ID_Map_All.has_key(anchor):
            temp_id = Title_ID_Map_All[anchor]
            if redirectHashmap.has_key(temp_id):
                anchor_id = redirectHashmap[temp_id]
            else:
                anchor_id = temp_id

        if ID_Title_Map_Pruned.has_key(anchor_id):
            if surfaceDictionary.has_key(anchor_id):
                if surface not in surfaceDictionary[anchor_id]:
                    surfaceDictionary[anchor_id].append(surface)
            else:
                surfaceDictionary[anchor_id].append(surface)

    #get inlink and outlink graph
    for anchor in anchors:
        anchor_id = None

        #change encoding
        anchor = anchor.encode("utf-8")
        #capitalize the first letter
        anchor = anchor[0:1].capitalize() + anchor[1:]
        # remove # sign
        if '#' in anchor:
            anchor = anchor[0:anchor.index('#')]

        # Normalize the anchor id (if it is redirect put the main title on it)
        if Title_ID_Map_All.has_key(anchor):
            temp_id = Title_ID_Map_All[anchor]
            if redirectHashmap.has_key(temp_id):
                anchor_id = redirectHashmap[temp_id]
            else:
                anchor_id = temp_id

        if ID_Title_Map_Pruned.has_key(anchor_id):
            addInLink(anchor_id, page_ID)
            addOutLink(page_ID, anchor_id)

progress = (float(index) / len(file_list)) * 100
progress = round(progress, 2)
logging.info(str(index) + ' pages processed successfully. [' + str(progress) + '% progress]')

#write outlinkGraph to file
outputFile = open(Path + "outlinkGraph.csv", "w")
for key, value in outlinkGraph.iteritems():
    outputFile.write(key)
    for va in value:
        outputFile.write(',' + va)
    outputFile.write('\r\n')
outputFile.close()
logging.info('Results of outlink graph are saved in outlinkGraph.csv')

#write outlinkGraphDegree to file
outputFile = open(Path + "outlinkGraphDegree.csv", "w")
for key, value in outlinkGraphDegree.iteritems():
    outputFile.write(key + ',' + str(value) + '\r\n')
outputFile.close()
logging.info('Results of outlink graph degree are saved in outlinkGraphDegree.csv')

#write inlinkGraph to file
outputFile = open(Path + "inlinkGraph.csv", "w")
for key, value in inlinkGraph.iteritems():
    outputFile.write(key)
    for va in value:
        outputFile.write(',' + va)
    outputFile.write('\r\n')
outputFile.close()
logging.info('Results of inlink graph are saved in inlinkGraph.csv')

#write inlinkGraphDegree to file
outputFile = open(Path + "inlinkGraphDegree.csv", "w")
for key, value in inlinkGraphDegree.iteritems():
    outputFile.write(key + ',' + str(value) + '\r\n')
outputFile.close()
logging.info('Results of inlink graph degree are saved in inlinkGraphDegree.csv')

#write surface dictionary to file
outputFile = open(Path + "surfaceDictionary.csv", "w")
for key, value in surfaceDictionary.iteritems():
    outputFile.write(key)
    for va in value:
        outputFile.write('@@' + va.encode("utf-8"))
    outputFile.write('\r\n')
outputFile.close()
logging.info('Results of surface Dictionary are saved in surfaceDictionary.csv')

#write head Dictionary to file
outputFile = open(Path + "headDictionary.csv", "w")
for key, value in headDictionary.iteritems():
    outputFile.write(key)
    for va in value:
        outputFile.write('@@' + va.encode("utf-8"))
    outputFile.write('\r\n')
outputFile.close()
logging.info('Results of headDictionary are saved in headDictionary.csv')

#write category Dictionary to file
outputFile = open(Path + "categoryDictionary.csv", "w")
for key, value in categoryDictionary.iteritems():
    outputFile.write(key)
    for va in value:
        outputFile.write('@@' + va.encode("utf-8"))
    outputFile.write('\r\n')
outputFile.close()
logging.info('Results of categoryDictionary are saved in categoryDictionary.csv')

#write infobox to file
outputFile = open(Path + "infoboxList.csv", "w")
for key, value in infoboxList.iteritems():
    outputFile.write(key + ',' + value.encode("utf-8") + '\r\n')
outputFile.close()
logging.info('Results of infoboxList are saved in infoboxList.csv')
