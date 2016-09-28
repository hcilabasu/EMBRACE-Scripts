# For each book, this script generates a Vocabulary-Metadata.xml file which lists the vocabulary words (and specifies whether they appear in the introduction list or not)
# for each chapter. It gathers this information from the audible tags in the .xhtml files of the EPUBS.
# All EPUB files should be located in the path specified by epubs_path.

import os

from bs4 import BeautifulSoup
from lxml import etree

def getBookTitle(directory):
    book = ""
    
    if directory == "bestFarm":
        book = "The Best Farm"
    elif directory == "bottled":
        book = "Bottled Up Joy"
    elif directory == "celebration":
        book = "A Celebration to Remember"
    elif directory == "circulatory":
        book = "The Circulatory System"
    elif directory == "disasters":
        book = "Natural Disasters"
    elif directory == "house":
        book = "The Lopez Family Mystery"
    elif directory == "monkey":
        book = "Introduction to EMBRACE"
    elif directory == "native":
        book = "Native American Homes"
    elif directory == "physics":
        book = "How Objects Move"

    return book

def main():
    epubsPath = "EPUBS"
    metaDataFileName = "Vocabulary-MetaData.xml"

    for directory in os.listdir(epubsPath):
        directoryPath = os.path.join(epubsPath, directory)
        book = getBookTitle(directory)

        if book != "":
            oebpsTextPath = os.path.join(directoryPath, "OEBPS/Text")
            
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            storyDictionary = {}
            
            for file in os.listdir(oebpsTextPath):
                if ("Intro-E.xhtml" in file or ("PM" in file and "S.xhtml" not in file)) and ("Introduction-At-the-Farm" not in file and "Introduction-At-the-House" not in file):
                    filePath = os.path.join(oebpsTextPath, file)
                    
                    introWord = "false"
                    
                    if "Intro-E.xhtml" in file:
                        introWord = "true"

                    with open(filePath, "r") as iFile:
                        html = iFile.read()
                        parsed_html = BeautifulSoup(html, "lxml")

                        chapter = parsed_html.find("title").text
                        wordDictionary = {}
                        
                        if chapter in storyDictionary:
                            wordDictionary = storyDictionary[chapter]

                        audibleWords = parsed_html.find_all("a", attrs = {"class": "audible"})

                        if len(audibleWords) > 0:
                            for audibleWord in audibleWords:
                                vocabulary = audibleWord.text.lower()

                                if vocabulary != "" and vocabulary not in wordDictionary:
                                    wordDictionary[vocabulary] = introWord
    
                        storyDictionary[chapter] = wordDictionary
        
            metaDataFile = open(os.path.join(directory, metaDataFileName), "w")
            
            metadata = etree.Element("metadata")
            vocabulary = etree.SubElement(metadata, "vocabulary")
        
            for story, dictionary in storyDictionary.items():
                storyElement = etree.SubElement(vocabulary, "story")
                storyElement.set("title", story)
                
                for word, introWord in dictionary.items():
                    vocabularyElement = etree.SubElement(storyElement, "vocabulary")
                    vocabularyElement.text = word
                    vocabularyElement.set("introWord", introWord)

            metaDataFile.write(etree.tostring(metadata, pretty_print = True))
            metaDataFile.close()

if __name__ == "__main__":
    main()
