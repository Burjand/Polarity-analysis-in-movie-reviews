import re
import os
import xml.etree.ElementTree as ET
from unidecode import unidecode

class Preprocessing():

    def __init__(self, corpus_folder, stopwords_file, lexicon_file_medium, lexicon_file_full, senticon_file, encoding="latin1"):

        #Obtain the list of numbers
        self.list_of_numbers = self.obtain_list_of_numbers(corpus_folder)

        # Extract tokenized text and classification
        self.ranks, self.lemmatized_reviews = self.extract_text_from_file(corpus_folder, encoding)

        # Clean text from stopwords
        self.reviews_no_stopwords = self.remove_stopwords(self.lemmatized_reviews, stopwords_file)

        # Obtain data from senticon
        self.senticon_data = self.extract_data_from_senticon(senticon_file) # A dictionary where each key is a word and its values are their weighted polarity value

        # Obtain data from lexicon
        self.lexicon_data = self.extract_data_from_lexicon(lexicon_file_medium, lexicon_file_full) # A dictionary where each key is a word and its values are their polarity value

        #Obtain a combined polarity dictionary
        self.polarity_dictionary = self.combine_dictionaries(self.senticon_data, self.lexicon_data)

    def obtain_list_of_numbers(self, corpus_folder):

        file_list = os.listdir(corpus_folder)

        numbers_list = []

        for file in file_list:

            match = re.search(r"^(.*?)(?=\.xml)", file)

            if match:

                numbers_list.append(int(match.group(1)))

        return numbers_list



    def extract_text_from_file(self, corpus_folder, encoding):
        
        ranks = []

        lemmatized_reviews = []
        
        for i in self.list_of_numbers:

            # Extract the assigned rank for the ith review
            xml_file = open(corpus_folder + f"{i}.xml", "r", encoding=encoding)
            raw_text = xml_file.read()
            xml_file.close()

            match = re.search(r'rank="(\d+)"', raw_text)
            rank_number = match.group(1)

            ranks.append(rank_number)
            
            # Extract the lemmatized text for the ith review
            analyzed_review_file = open(corpus_folder + f"{i}.review.pos", "r", encoding=encoding)
            raw_text = analyzed_review_file.readlines()
            analyzed_review_file.close()

            tokenized_lemmatized_review = []

            for line in raw_text:
                
                tokenized = line.split()

                if len(tokenized) == 4:

                    tokenized_lemmatized_review.append(tokenized[1])
            
            lemmatized_review = []

            for token in tokenized_lemmatized_review:

                if token.isalpha():

                    lemmatized_review.append(token.lower())

            lemmatized_reviews.append(lemmatized_review)


        return ranks, lemmatized_reviews



    def remove_stopwords(self, lemmatized_reviews, stopwords_file, encoding="UTF-8"):

        file = open(stopwords_file, "r", encoding=encoding)
        stopwords_raw = file.readlines()
        file.close()

        stopwords_list = [word.replace("\n","") for word in stopwords_raw]

        reviews_no_stopwords = []

        for review in lemmatized_reviews:

            temp_sentence = []

            for item in review:

                if item not in stopwords_list:

                    temp_sentence.append(item)
            
            reviews_no_stopwords.append(temp_sentence)

        return reviews_no_stopwords
    


    def extract_data_from_senticon(self, senticon_file):
        
        xml_file = senticon_file
        tree = ET.parse(xml_file)
        root = tree.getroot()

        lemma_dictionary = {}

        for layer_number in range(1, 9):  # Layers are 1 to 8

            layer = root.find(f".//layer[@level='{layer_number}']")
            
            # Extract lemmas from positive and negative parts
            for part in ["positive", "negative"]:

                section = layer.find(part)

                for lemma in section.findall("lemma"):

                    lemma_text = lemma.text.strip()                    

                    if lemma_text not in lemma_dictionary and '_' not in lemma_text and '-' not in lemma_text:

                        # Extract only the last two attributes
                        last_two_attributes = [float(value) for value in list(lemma.attrib.values())[-2:]]

                        polarity_value = last_two_attributes[0]
                        std = last_two_attributes[1]
                        
                        # Rescaling the std value to the range [1,0.5], this way, the worst standard deviation (0.707) will reduce the valueto half and the best (0) will maintain the value
                        polarity_value_weighted = polarity_value * (0.5 + ((std - 0) / (0.707 - 0)) * (1 - 0.5))

                        lemma_dictionary[unidecode(lemma_text)] = polarity_value_weighted

        return lemma_dictionary


    
    def extract_data_from_lexicon(self, lexicon_file_medium, lexicon_file_full):

        lexicon_data = {}

        file = open(lexicon_file_full, "r", encoding="UTF-8")
        lexicon_full_raw_data = file.readlines()
        file.close

        for line in lexicon_full_raw_data:

            content = line.split()

            if len(content) == 4:

                if content[2] == content[3] and content[3] == 'pos' and content[0] not in lexicon_data:

                    lexicon_data[content[0]] = 1

                elif content[2] != content[3] and content[3] == 'pos' and content[0] not in lexicon_data:

                    lexicon_data[content[0]] = 0.25 # Because the human's opinions are worth more than the automatically generated

                elif content[2] == content[3] and content[3] == 'neg' and content[0] not in lexicon_data:

                    lexicon_data[content[0]] = -1

                elif content[2] != content[3] and content[3] == 'neg' and content[0] not in lexicon_data:

                    lexicon_data[content[0]] = -0.25 # Because the human's opinions are worth more than the automatically generated

            else:

                if content[2] == 'pos' and content[0] not in lexicon_data:

                    lexicon_data[content[0]] = 0.75 # Because the human's opinions combined with the automatically generated is worth more than the automatically generated alone

                elif content[2] == 'neg' and content[0] not in lexicon_data:

                    lexicon_data[content[0]] = -0.75 # Because the human's opinions combined with the automatically generated is worth more than the automatically generated alone

        
        file = open(lexicon_file_medium, "r", encoding="UTF-8")
        lexicon_medium_raw_data = file.readlines()
        file.close

        for line in lexicon_medium_raw_data:

            content = line.split()

            if len(content) == 4:

                if content[2] == content[3] and content[3] == 'pos':

                    lexicon_data[content[0]] = 1

                elif content[2] != content[3] and content[3] == 'pos':

                    lexicon_data[content[0]] = 0.25 # Because the human's opinions are worth more than the automatically generated

                elif content[2] == content[3] and content[3] == 'neg':

                    lexicon_data[content[0]] = -1

                elif content[2] != content[3] and content[3] == 'neg':

                    lexicon_data[content[0]] = -0.25 # Because the human's opinions are worth more than the automatically generated

            else:

                if content[2] == 'pos' and content[0] not in lexicon_data:

                    lexicon_data[content[0]] = 0.75 # Because the human's opinions combined with the automatically generated is worth more than the automatically generated alone

                elif content[2] == 'neg' and content[0] not in lexicon_data:

                    lexicon_data[content[0]] = -0.75 # Because the human's opinions combined with the automatically generated is worth more than the automatically generated alone


        return lexicon_data



    def combine_dictionaries(self, senticon_data, lexicon_data):

        the_dictionary = {}

        # Combine keys from both dictionaries
        all_keys = set(senticon_data.keys()).union(lexicon_data.keys())

        for word in all_keys:
            if word in senticon_data and word in lexicon_data:
                # Average the values if the word is in both dictionaries
                the_dictionary[word] = (senticon_data[word] + lexicon_data[word]) / 2
            elif word in senticon_data:
                # Take the value from senticon_data if not in lexicon_data
                the_dictionary[word] = senticon_data[word]
            else:
                # Take the value from lexicon_data if not in senticon_data
                the_dictionary[word] = lexicon_data[word]

        return the_dictionary




