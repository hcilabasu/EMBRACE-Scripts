import os
import xlsxwriter

from bs4 import BeautifulSoup

COLUMN_VOCABULARY = 0
COLUMN_BOOK = 1
COLUMN_CHAPTER_COUNT = 2
COLUMN_TOTAL_CHAPTERS = 3
COLUMN_TOTAL_COUNT = 4
COLUMN_INVOLVES_MANIPULATION = 5

class Vocabulary:
    def __init__(self, text):
        self.text = text
        self.chapter_count = {}
        self.total_chapters = 0
        self.total_count = 0
        self.involves_manipulation = False

    def update_chapter_count(self, chapter_number):
        if chapter_number not in self.chapter_count:
            self.chapter_count[chapter_number] = 1
            self.total_chapters += 1
        else:
            self.chapter_count[chapter_number] += 1

        self.total_count += 1

def setup_workbook(workbook, worksheet):
    # Add a bold format
    bold = workbook.add_format({"bold": True})

    row = 0

    # Write labels
    worksheet.write(row, COLUMN_VOCABULARY, "Vocabulary", bold)
    worksheet.write(row, COLUMN_BOOK, "Book", bold)
    worksheet.write(row, COLUMN_CHAPTER_COUNT, "Chapter (Count)", bold)
    worksheet.write(row, COLUMN_TOTAL_CHAPTERS, "Total Chapters", bold)
    worksheet.write(row, COLUMN_TOTAL_COUNT, "Total Count", bold)
    worksheet.write(row, COLUMN_INVOLVES_MANIPULATION, "Involves Manipulation", bold)

    return (workbook, worksheet)

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

def main():
    epubs_path = "EPUBS"

    # Create Excel file
    workbook = xlsxwriter.Workbook("vocabulary_counts.xlsx")
    worksheet = workbook.add_worksheet()

    setup_workbook(workbook, worksheet)
    
    row = 1
    
    for directory in os.listdir(epubs_path):
        directory_path = os.path.join(epubs_path, directory)
        book_title = get_book_title(directory)
        
        if book_title != "":
            book_vocabulary = {}
            
            oebps_text_path = os.path.join(directory_path, "OEBPS/Text")

            for file in os.listdir(oebps_text_path):
                if "PM" in file and "S.xhtml" not in file:
                    chapter_number = file[5]
                    
                    file_path = os.path.join(oebps_text_path, file)

                    with open(file_path, "r") as pm_file:
                        html = pm_file.read()
                        parsed_html = BeautifulSoup(html, "lxml")
                        
                        audible_words = parsed_html.find_all("a", attrs = {"class": "audible"})

                        if len(audible_words) > 0:
                            for audible_word in audible_words:
                                text = audible_word.text.lower()

                                if text != "":
                                    vocabulary = None
                                    
                                    if text not in book_vocabulary:
                                        vocabulary = Vocabulary(text)
                                    else:
                                        vocabulary = book_vocabulary[text]
                                    
                                    vocabulary.update_chapter_count(chapter_number)
                                    
                                    # Check if vocabulary is part of an action sentence
                                    action_sentence = audible_word.find_parents(attrs = {"class": "actionSentence"})
                                    
                                    if len(action_sentence) > 0:
                                        vocabulary.involves_manipulation = True
        
                                    book_vocabulary[text] = vocabulary

            for vocabulary in book_vocabulary.values():
                worksheet.write(row, COLUMN_VOCABULARY, vocabulary.text)
                worksheet.write(row, COLUMN_BOOK, book_title)
                worksheet.write(row, COLUMN_CHAPTER_COUNT, ", ".join(["CH%s (%s)" % (chapter, count) for (chapter, count) in vocabulary.chapter_count.items()]))
                worksheet.write(row, COLUMN_TOTAL_CHAPTERS, vocabulary.total_chapters)
                worksheet.write(row, COLUMN_TOTAL_COUNT, vocabulary.total_count)
                worksheet.write(row, COLUMN_INVOLVES_MANIPULATION, vocabulary.involves_manipulation)

                row += 1
 
    # Close the workbook
    workbook.close()

if __name__ == "__main__":
    main()
