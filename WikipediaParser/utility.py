# -*- coding: utf-8 -*-
"""
@summary Some public tools for processing Wikipedia. The tools are:
        1) Remove HTML XML special characters notation.
        2) Change numbers to literal (e.g. 0 to zero)
        3) Clean the text and converted to ascii 27 english character plus space
        4) Extract category information of the Wikipedia page
        5) Extract head titles of each section of the Wikipedia page
        6) Extract the clean text from Wikipedia page (tag <text> of the dump)
        7) Extract the infobox of the page
        8) Redirect hashmap <page ID, redirect ID> if the page is not redirect the redirect ID and page ID are the same
@author Ehsan Sherkat
"""

import re
from htmlentitydefs import name2codepoint
import string
import unicodedata
import mwparserfromhell
import WikiExtractor
import logging

# setup logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def remove_HTML_XML_char(text):
    """
    Removes HTML or XML character references and entities from a text string.
    :param text The HTML (or XML) source text.
    :return The plain text, as a Unicode string, if necessary.
    Code from 'https://github.com/attardi/wikiextractor'
    """
    def fixup(m):
        text = m.group(0)
        code = m.group(1)
        try:
            if text[1] == "#":  # character reference
                if text[2] == "x":
                    return unichr(int(code[1:], 16))
                else:
                    return unichr(int(code))
            else:  # named entity
                return unichr(name2codepoint[code])
        except:
            return text  # leave as is

    return re.sub("&#?(\w+);", fixup, text)

def numberToLiteral(page):
    """
    change numbers to literal (e.g. 0 to zero)
    @param page:
    @return:
    """
    page = re.sub('0', ' zero ', page)
    page = re.sub('1', ' one ', page)
    page = re.sub('2', ' two ', page)
    page = re.sub('3', ' three ', page)
    page = re.sub('4', ' four ', page)
    page = re.sub('5', ' five ', page)
    page = re.sub('6', ' six ', page)
    page = re.sub('7', ' seven ', page)
    page = re.sub('8', ' eight ', page)
    page = re.sub('9', ' nine ', page)
    return page

def clean27English(page):
    """
    clean the text and converted to ascii 27 english character plus space
    @param page: input text file
    @return: the clean text
    """
    # page = numberToLiteral(page)  # change numbers to literal (e.g. 0 to zero) [NOTE: If using anchorID comment this line]
    #page = unicodedata.normalize('NFKD', unicode(page, 'utf-8')).encode('ascii', 'ignore')  # Change none English alphabet to English one (e.g. inför to infor)
                                                                          # [NOTE: If using anchorID comment this line]
    page = page.translate(string.maketrans(string.punctuation, ' ' * len(string.punctuation)))  # Remove Punctuations
    page = re.sub('\s+', ' ', page).strip()  # Remove new line, Tab and double spaces
    page = page.lower()  # Lower case

    return page

def extractCategory(page):
    """
    extract categoies of the page
    @param page: the content of the Wikipedia page dump in <text> tag.
    @return: The list of categories
    """
    categories = re.findall('\[\[Category:(.+?)[\||\]\]]', page)
    return categories

def extractHeads(page):
    """
    extract categoies of the page
    @param page: the content of the Wikipedia page dump in <text> tag.
    @return: The list of categories
    """
    try:
        heads = mwparserfromhell.parse(page).filter_headings()
    except:
        logging.error('Error parsing page for extracting headlines')
        return []
    return heads

def extractCleanText(page, anchorID, english27, Title_ID_All, Redirect_Hashmap, In_Link_Graph_Degree, min_degree):
    """
    extract the clean text from Wikipedia page (tag <text> of the dump)
    @param page: Wikipedia page (tag <text> of the dump)
    @param anchor: If ture the anchor ID will be replace unless the surface form will be replaced in the internal links
    @return: clean text of Wikipedia page
    """
    page = WikiExtractor.cleanText(page, anchorID, Title_ID_All, Redirect_Hashmap, In_Link_Graph_Degree, min_degree, english27)
    if english27:
        page = clean27English(page) # Convert to 27 English ASCII char plus space
    return page

def extractInfobox(page):
    """
    extract infobox type of the page (This function needs to be improved to get details information of the infobox)
    @param page: page content
    @return: the infobox type
    """
    infoboxs = re.findall('\{\{Infobox([^$\|\n\r\{\}<]+)', page)
    if infoboxs:
        return infoboxs[0].strip()
    return ""

def redirectHashmap(redirectDictionaryPath, ID_Tittle_Map_Path, savePath):
    """
    Redirect hashmap <page ID, redirect ID>
    @param redirectDictionaryPath:
    @param ID_Tittle_Map_Path:
    @param savePath:
    @return: Redirect hashmap <page ID, redirect ID>
    """
    Title_ID_Map = {}  # The hashmap of pages
    ID_Title_File = open(ID_Tittle_Map_Path, 'r')

    # read page list
    logging.info('Start reading ID Title map...')
    for line in ID_Title_File:
        key = line[line.index(':') + 1:line.index(',')]
        value = line[line.index(',') + 1:line.index('\r\n')]
        Title_ID_Map[value] = key
    logging.info('ID Title map read successfully.')

    redirectDictionary = {}
    redirectDictionary_File = open(redirectDictionaryPath, 'r')

    # read redirectDictionary list
    logging.info('Start reading redirect Dictionary...')
    for line in redirectDictionary_File:
        line = line.replace('\n', '').replace('\r', '')
        redirects = line.split("@@")
        i = 1
        if Title_ID_Map.has_key(redirects[0]):
            headPage = Title_ID_Map[redirects[0]]
            while i < len(redirects):
                if Title_ID_Map.has_key(redirects[i]):
                    redirectDictionary[Title_ID_Map[redirects[i]]] = headPage
                else:
                    logging.error("[page not found!]: " + redirects[i])
                i += 1
        else:
            logging.error("[page not found!]: " + redirects[0])
    logging.info('Redirect Dictionary read successfully.')

    # write redirect hashmap
    outputFile = open(savePath + "redirectHashmap.csv", "w")
    for key, value in redirectDictionary.iteritems():
        outputFile.write(key + ',' + value + '\r\n')
    outputFile.close()
    logging.info('Pruned pages are saved in: redirectHashmap.csv')

def extractWikiIDVectors(modelPath, outputPath):
    """
    Extract only wikiIDs from vector list
    @param modelPath:
    @param outputPath:
    @return: Number of vectors
    """
    file = open(modelPath, 'r')
    ID_Title_All_Path = "/media/ehsan/My Documents/Shared/Datasets/Wikipedia/pages/id_title_map.csv"
    Title_ID_All = {}
    output = list()
    # read ID_Title_Map_All
    logging.info('Reading ID title map all...')
    ID_Title_All_File = open(ID_Title_All_Path, 'r')
    for line in ID_Title_All_File:
        key = line[line.index(':') + 1:line.index(',')]
        value = line[line.index(',') + 1:line.index('\r\n')]
        Title_ID_All[key] = value
    logging.info('ID title map all read successfully.')
    count = 0
    for line in file:
        if count == 0:
            dimension = line[line.index(' '):].replace('\r', '').replace('\n', '')
        key = line[0:line.index(' ')]
        if key.isdigit():
            if Title_ID_All.has_key(key):
                count += 1
                output.append(line)
    # write id_title_map on a file
    outputFile = open(outputPath + "OnlyWikiIDVector.txt", "w")
    outputFile.write(str(count)+' '+dimension+'\n')
    for val in output:
        outputFile.write(val.encode("utf-8") + '\n')
    outputFile.close()
    logging.info('Results of vector of '+str(count)+' '+dimension +' saved in OnlyWikiIDVector.txt.')
    return count