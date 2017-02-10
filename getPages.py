"""
@summary Get the wikipedia XML dump file and split it to pages (One XML for every page)
@author Ehsan Sherkat
"""
import logging
import os
from xml.etree.cElementTree import iterparse
from xml.etree import ElementTree

dumpPath = "/home/ehsan/Downloads/enwiki-20160501-pages-articles-multistream.xml"
outputPath = '/media/ehsan/My Documents/Shared/Datasets/Wikipedia/pages/'
nameSpace = '{http://www.mediawiki.org/xml/export-0.10/}'
tagName = 'page'
bucket = 50000 # number of file that will be put in each folder

# setup logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# get an iterable
context = iterparse(dumpPath, events=("start", "end"))

# turn it into an iterator
context = iter(context)

# get the root element
event, root = context.next()

index = 0# number of pages
folderCounter = 1# number of folders to store pages

# create subfolder
if not os.path.exists(outputPath + str(folderCounter)):
    os.makedirs(outputPath + str(folderCounter))

#Page id to title map
id_title_map = list()

for event, elem in context:
    if event == "end" and elem.tag == (nameSpace + tagName):

        # get page id
        for node in elem:
            if node.tag == (nameSpace + 'id'):
                pageID = node.text
            if node.tag == (nameSpace + 'title'):
                pageTitle = node.text

        id_title_map.append(str(folderCounter) + ":" + str(pageID) + "," + pageTitle)

        output_file = open(outputPath + str(folderCounter) + '/' + pageID + '.xml', 'w')
        output_file.write('<?xml version="1.0"?>')
        output_file.write(ElementTree.tostring(elem))
        output_file.close()

        index += 1
        if index % bucket == 0:
            logging.info(str(index) + ' pages processed successfully.')
            folderCounter += 1
            if not os.path.exists(outputPath + str(folderCounter)):
                os.makedirs(outputPath + str(folderCounter))
        root.clear()

#write id_title_map on a file
outputFile = open(outputPath + "id_title_map.csv", "w")
for val in id_title_map:
    outputFile.write(val.encode("utf-8") + '\r\n')
outputFile.close()

logging.info(str(index) + ' pages extracted successfully')