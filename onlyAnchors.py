"""
@summary In this code all text except the anchors will remove from the Wikipedia page
"""
import logging

Path = '/media/ehsan/My Documents/Shared/Datasets/Wikipedia/pages/'
WikipediaCleanPath = "pagesTextCleanAnchorID_tittle_extend.txt"
pagesOnlyAnchorID = list() # clean only anchorID of pages
wiki_index = 4372559

# setup logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def onlyAnchors():
    # read clean Wikipedia dataset
    index = 0
    flushIndex = 0
    for page in open(Path + WikipediaCleanPath):
        page = page.replace('\r','').replace('\n','')
        tokens = page.split(' ')

        newPage = ""
        for token in tokens:
            if token.isdigit():
                newPage += token + ' '

        newPage = newPage.strip()

        pagesOnlyAnchorID.append(newPage)

        flushIndex += 1
        if flushIndex % 1000000 == 0:
            flushIndex = 0
            writeOutputToFile()
            del pagesOnlyAnchorID[:]
            logging.info('1000000 pages wrote on file successfully.')

        index += 1
        if index % 100000 == 0:
            progress = (float(index) / wiki_index) * 100
            progress = round(progress, 2)
            logging.info(str(index) + ' pages processed successfully. [' + str(progress) + '% progress]')

    writeOutputToFile()  # write the rest
    progress = (float(index) / wiki_index) * 100
    progress = round(progress, 2)
    logging.info(str(index) + ' pages processed successfully. [' + str(progress) + '% progress]')

def writeOutputToFile():
    outputFile = open(Path + "pagesOnlyAnchorID_tittle_extend.txt", "a")
    for value in pagesOnlyAnchorID:
        outputFile.write(value + '\n')
    outputFile.close()

onlyAnchors()