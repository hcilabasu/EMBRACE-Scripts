# For each book, this script generates a file (e.g., bestFarm_Vocabulary_Audio.txt) containing a list of vocabulary words that require audio.
# It looks for potential words using object IDs in Solutions-MetaData.xml and checks if there is already audio for the corresponding word. If so, the word is removed from the list.
# All EPUB files should be located in the path specified by epubs_path.
# The file image_translations.txt contains the contents of the translationImages dictionary in Translation.m of EMBRACE.xcodeproj.

import os
import re
import xml.etree.ElementTree as ET

def isWordValid(word):
    if "_" in word or any(char.isdigit() for char in word) or any(char.isupper() for char in word):
#        print word
        return False

    return True

def get_book_title(directory):
    book_title = ""
    
    if directory == "bestFarm":
        book_title = "The Best Farm"
    elif directory == "bottled":
        book_title = "Bottled Up Joy"
    elif directory == "celebration":
        book_title = "A Celebration to Remember"
    elif directory == "circulatory":
        book_title = "The Circulatory System"
    elif directory == "disasters":
        book_title = "Natural Disasters"
    elif directory == "house":
        book_title = "The Lopez Family Mystery"
    elif directory == "monkey":
        book_title = "Introduction to EMBRACE"
    elif directory == "native":
        book_title = "Native American Homes"
    elif directory == "physics":
        book_title = "How Objects Move"
    
    return book_title

def get_vocabulary_from_object_id(object_id, book_vocabulary_images, book):
    vocabulary_from_object_id = []
    vocabulary_images = book_vocabulary_images[book]
    
    for vocabulary, images in vocabulary_images.items():
        if object_id in images:
#            print "vocabulary: {0}  images: {1}".format(vocabulary, images)
            vocabulary_from_object_id.append(vocabulary)

    return vocabulary_from_object_id

def read_image_translations():
    image_translations_file_name = "image_translations.txt"
    
    book_order = ["bestFarm", "circulatory", "house", "monkey", "native", "bottled", "physics", "celebration", "disasters"]
    book_index = 0
    book_vocabulary_images = {}
    book_vocabulary_images[book_order[book_index]] = {}

    with open(image_translations_file_name, "r") as image_translations_file:
        lines = image_translations_file.readlines()
        
        for line in lines:
            lineVocabulary = re.findall('"([^"]*)"', line)
            
            if len(lineVocabulary) == 0:
                book_index += 1
                book_vocabulary_images[book_order[book_index]] = {}
            else:
                vocabulary_images = book_vocabulary_images[book_order[book_index]]
                
                vocabulary = lineVocabulary[0]
                images = lineVocabulary[1:]

                vocabulary_images[vocabulary] = images

#    for book, vocabulary_images in book_vocabulary_images.items():
#        for vocabulary, images in vocabulary_images.items():
#            print "{0}[{1}] = {2}".format(book, vocabulary, images)

    return book_vocabulary_images

def main():
    book_vocabulary_images = read_image_translations()
    
    epubs_path = "EPUBS"
    vocabulary_metadata_file_name = "Vocabulary-MetaData.xml"
    vocabulary_audio_file_name_suffix = "_Vocabulary_Audio.txt"
    
    for directory in os.listdir(epubs_path):
        directory_path = os.path.join(epubs_path, directory)
        book_title = get_book_title(directory)

        if book_title != "":
            book_vocabulary = []
            
            solutions_metadata_file_path = os.path.join(directory_path, "OEBPS/Solutions-MetaData.xml")

            with open(solutions_metadata_file_path, "r") as solutions_metadata_file:
                tree = ET.parse(solutions_metadata_file)
                root = tree.getroot()

                for element in root.findall(".//*[@obj1Id]"):
                    obj1Id = element.attrib["obj1Id"]

                    vocabulary = get_vocabulary_from_object_id(obj1Id, book_vocabulary_images, directory)
                    
                    if len(vocabulary) > 0:
                        for vocab in vocabulary:
                            if vocab not in book_vocabulary:
                                book_vocabulary.append(vocab)
                    else:
                        if obj1Id not in book_vocabulary and isWordValid(obj1Id):
                            book_vocabulary.append(obj1Id)

                for element in root.findall(".//*[@obj2Id]"):
                    obj2Id = element.attrib["obj2Id"]

                    vocabulary = get_vocabulary_from_object_id(obj2Id, book_vocabulary_images, directory)
                        
                    if len(vocabulary) > 0:
                        for vocab in vocabulary:
                            if vocab not in book_vocabulary:
                                book_vocabulary.append(vocab)
                    else:
                        if obj2Id not in book_vocabulary and isWordValid(obj2Id):
                            book_vocabulary.append(obj2Id)
        
            vocabulary_metadata_file_path = os.path.join(directory, vocabulary_metadata_file_name)
            
            with open(vocabulary_metadata_file_path, "r") as vocabulary_metadata_file:
                tree = ET.parse(vocabulary_metadata_file)
                root = tree.getroot()

                for vocabularyElement in root.findall(".//vocabulary"):
                    vocabularyElementText = vocabularyElement.text

                    if vocabularyElementText in book_vocabulary:
                        book_vocabulary.remove(vocabularyElementText)
            
            vocabulary_audio_file_path = os.path.join(directory, directory + vocabulary_audio_file_name_suffix)

            with open(vocabulary_audio_file_path, "w") as vocabulary_audio_file:
                for vocabulary in book_vocabulary:
                    vocabulary_audio_file.write(vocabulary + "\n")

if __name__ == "__main__":
    main()
