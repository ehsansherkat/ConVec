"""
@summary This module extracts information from Wikipedia pages. These information are:
            1) Clean text of pages with AnchorID replaced (and english 27 char as option)
            2) Clean text of pages (and english 27 char as option)
@author Ehsan Sherkat
"""

import utility
import logging
from xml.dom import minidom

ID_Title_Pruned_Path = "/media/ehsan/My Documents/Shared/Datasets/Wikipedia/pages/ID_Title_Map_Pruned.csv" # The path to the ID Title Map pruned file
ID_Title_All_Path = "/media/ehsan/My Documents/Shared/Datasets/Wikipedia/pages/id_title_map.csv"
Path = '/media/ehsan/My Documents/Shared/Datasets/Wikipedia/pages/' # where to save result and where the pages are
Redirect_Hashmap_Path = "/media/ehsan/My Documents/Shared/Datasets/Wikipedia/pages/redirectHashmap.csv"
Out_Link_Graph_Degree_Path = "/media/ehsan/My Documents/Shared/Datasets/Wikipedia/pages/inlinkGraphDegree.csv"
In_Link_Graph_Degree_Path = "/media/ehsan/My Documents/Shared/Datasets/Wikipedia/pages/outlinkGraphDegree.csv"

file_list = list() # list of the path of the pages
ID_Title_Pruned = {}
Title_ID_All = {}
Redirect_Hashmap = {}
Out_Link_Graph_Degree = {}
In_Link_Graph_Degree = {}

pagesTextCleanAnchorID = list() # clean text of Wikipedia pages by anchorID replaced
pagesIDCleanAnchorID = list() # the ID of pages

# setup logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Read Redirect hashmap
Redirect_Hashmap_File = open(Redirect_Hashmap_Path, 'r')
logging.info('Start reading redirect Hashmap...')
for line in Redirect_Hashmap_File:
    if line > 0:
        key = line[0:line.index(',')]
        value = line[line.index(',')+1:line.index('\r\n')]
        Redirect_Hashmap[key] = value
logging.info('Redirect Hashmap read successfully.')

# read ID_Title_Map_Pruned
ID_Title_Pruned_File = open(ID_Title_Pruned_Path, 'r')
logging.info('Start reading ID Title map...')
for line in ID_Title_Pruned_File:
    key = line[line.index(':')+1:line.index(',')]
    value = line[line.index(',')+1:line.index('\r\n')]

    ID_Title_Pruned[key] = value
    file_name = line[0:line.index(',')].replace(':', '/')
    file_list.append(file_name)
logging.info('ID Title map read successfully.')

# read ID_Title_Map_All
ID_Title_All_File = open(ID_Title_All_Path, 'r')
logging.info('Start reading ID Title map (All)...')
for line in ID_Title_All_File:
    key = line[line.index(':')+1:line.index(',')]
    value = line[line.index(',')+1:line.index('\r\n')]
    Title_ID_All[value] = key
logging.info('ID Title map (all) read successfully.')

# read outLinkDegree
Out_Link_Graph_Degree_File = open(Out_Link_Graph_Degree_Path, 'r')
logging.info('Start reading out degree Hashmap...')
for line in Out_Link_Graph_Degree_File:
    if line > 0:
        key = line[0:line.index(',')]
        value = line[line.index(',')+1:line.index('\r\n')]
        Out_Link_Graph_Degree[key] = value
logging.info('Out degree Hashmap read successfully.')

# read inLinkDegree
In_Link_Graph_Degree_File = open(In_Link_Graph_Degree_Path, 'r')
logging.info('Start reading In degree Hashmap...')
for line in In_Link_Graph_Degree_File:
    if line > 0:
        key = line[0:line.index(',')]
        value = line[line.index(',')+1:line.index('\r\n')]
        In_Link_Graph_Degree[key] = value
logging.info('In degree Hashmap read successfully.')

def writeOutputToFile():
    outputFile = open(Path + "pagesTextCleanAnchorID.txt", "a")
    for value in pagesTextCleanAnchorID:
        outputFile.write(value+ '\r\n')
    outputFile.close()

    outputFile = open(Path + "pagesTextCleanAnchorID_Index.txt", "a")
    for value in pagesIDCleanAnchorID:
        outputFile.write(value+ '\r\n')
    outputFile.close()

def getCleanTextByAnchorID():
    index = 0
    flushIndex = 0
    logging.info('Start Processing pages ...')

    for file_name in file_list:
        index += 1

        if index % 20000 == 0:
            progress = (float(index) / len(file_list)) * 100
            progress = round(progress, 2)
            logging.info(str(index) + ' pages processed successfully. [' + str(progress) + '% progress]')

        page_ID = file_name[file_name.index('/') + 1:]

        # only pages that have at least one out link are considered
        if Out_Link_Graph_Degree.has_key(page_ID):
            file = open(Path + file_name + ".xml", 'r')
            page = minidom.parse(file)
            file.close()

            pageText = page.getElementsByTagName('ns0:text')[0].firstChild.nodeValue
            cleanPage = utility.extractCleanText(pageText,
                                                 anchorID=True,
                                                 english27=True,
                                                 Title_ID_All=Title_ID_All,
                                                 Redirect_Hashmap=Redirect_Hashmap,
                                                 In_Link_Graph_Degree=In_Link_Graph_Degree,
                                                 min_degree=5)

            pagesTextCleanAnchorID.append(cleanPage)
            pagesIDCleanAnchorID.append(page_ID)

            flushIndex += 1
            if flushIndex % 1000000 == 0:
                flushIndex = 0
                writeOutputToFile()
                # clear pagesTextCleanAnchorID and pagesIDCleanAnchorID
                del pagesTextCleanAnchorID[:]
                del pagesIDCleanAnchorID[:]
                logging.info('1000000 pages wrote on file successfully.')
    progress = (float(index) / len(file_list)) * 100
    progress = round(progress, 2)
    logging.info(str(index) + ' pages processed successfully. [' + str(progress) + '% progress]')

# extract clean text and replace anchor with ID
getCleanTextByAnchorID()
writeOutputToFile()
logging.info('Results saved on pagesTextCleanAnchorID.txt and pagesTextCleanAnchorID_Index.txt')